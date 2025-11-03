import pandas as pd
from datetime import datetime, date
from typing import List, Optional, Dict, Any
import requests
import time
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def apply_scd_type2_logic(existing_records: pd.DataFrame, 
                         new_records: pd.DataFrame,
                         business_key: str = 'customer_id',
                         effective_date_col: str = 'effective_date',
                         expiration_date_col: str = 'expiration_date',
                         is_current_col: str = 'is_current',
                         process_date: Optional[date] = None) -> pd.DataFrame:
    """
    Apply Slowly Changing Dimension Type 2 logic to customer records.
    
    This function compares new customer records with existing records and creates
    historical versions when changes are detected. It maintains effective and
    expiration dates to track record validity periods.
    
    Parameters:
    existing_records (pd.DataFrame): Current customer records in the dimension table.
    new_records (pd.DataFrame): New customer records to process.
    business_key (str): Column name that uniquely identifies a customer.
    effective_date_col (str): Column name for record effective date.
    expiration_date_col (str): Column name for record expiration date.
    is_current_col (str): Column name indicating if record is current.
    process_date (Optional[date]): Date to use for processing. Defaults to today.
    
    Returns:
    pd.DataFrame: Updated customer records with SCD Type 2 applied.
    """
    if process_date is None:
        process_date = date.today()
    
    # Validate input dataframes
    _validate_scd_inputs(existing_records, new_records, business_key)
    
    # Initialize result with existing records
    result_records = existing_records.copy()
    
    # Ensure required SCD columns exist
    result_records = _ensure_scd_columns(result_records, effective_date_col, 
                                       expiration_date_col, is_current_col, process_date)
    
    # Get columns to compare (excluding SCD metadata columns)
    scd_metadata_cols = {business_key, effective_date_col, expiration_date_col, is_current_col}
    comparison_columns = [col for col in new_records.columns if col not in scd_metadata_cols]
    
    processed_customers = set()
    
    for _, new_record in new_records.iterrows():
        customer_id = new_record[business_key]
        processed_customers.add(customer_id)
        
        # Find current record for this customer
        current_record_mask = ((result_records[business_key] == customer_id) & 
                              (result_records[is_current_col] == True))
        current_records = result_records[current_record_mask]
        
        if current_records.empty:
            # New customer - insert as current record
            new_customer_record = _create_new_customer_record(
                new_record, business_key, effective_date_col, 
                expiration_date_col, is_current_col, process_date
            )
            result_records = pd.concat([result_records, new_customer_record], ignore_index=True)
        else:
            # Existing customer - check for changes
            current_record = current_records.iloc[0]
            
            if _has_data_changed(current_record, new_record, comparison_columns):
                # Data changed - expire current record and create new one
                result_records = _expire_current_record(
                    result_records, current_record_mask, expiration_date_col, 
                    is_current_col, process_date
                )
                
                new_version_record = _create_new_version_record(
                    new_record, business_key, effective_date_col,
                    expiration_date_col, is_current_col, process_date
                )
                result_records = pd.concat([result_records, new_version_record], ignore_index=True)
    
    return result_records.sort_values([business_key, effective_date_col]).reset_index(drop=True)


def _validate_scd_inputs(existing_records: pd.DataFrame, 
                        new_records: pd.DataFrame, 
                        business_key: str) -> None:
    """
    Validate input dataframes for SCD processing.
    
    Parameters:
    existing_records (pd.DataFrame): Existing customer records.
    new_records (pd.DataFrame): New customer records.
    business_key (str): Business key column name.
    
    Returns:
    None: Raises ValueError if validation fails.
    """
    if business_key not in new_records.columns:
        raise ValueError(f"Business key '{business_key}' not found in new records")
    
    if not existing_records.empty and business_key not in existing_records.columns:
        raise ValueError(f"Business key '{business_key}' not found in existing records")
    
    if new_records[business_key].isnull().any():
        raise ValueError(f"Business key '{business_key}' contains null values in new records")


def _ensure_scd_columns(dataframe: pd.DataFrame, 
                       effective_date_col: str,
                       expiration_date_col: str, 
                       is_current_col: str,
                       default_date: date) -> pd.DataFrame:
    """
    Ensure SCD metadata columns exist in the dataframe.
    
    Parameters:
    dataframe (pd.DataFrame): Input dataframe.
    effective_date_col (str): Effective date column name.
    expiration_date_col (str): Expiration date column name.
    is_current_col (str): Is current flag column name.
    default_date (date): Default date for new columns.
    
    Returns:
    pd.DataFrame: Dataframe with SCD columns added if missing.
    """
    df = dataframe.copy()
    
    if effective_date_col not in df.columns:
        df[effective_date_col] = default_date
    
    if expiration_date_col not in df.columns:
        df[expiration_date_col] = pd.NaT
    
    if is_current_col not in df.columns:
        df[is_current_col] = True
    
    return df


def _has_data_changed(current_record: pd.Series, 
                     new_record: pd.Series, 
                     comparison_columns: List[str]) -> bool:
    """
    Check if customer data has changed between records.
    
    Parameters:
    current_record (pd.Series): Current customer record.
    new_record (pd.Series): New customer record.
    comparison_columns (List[str]): Columns to compare for changes.
    
    Returns:
    bool: True if data has changed, False otherwise.
    """
    for column in comparison_columns:
        if column in current_record.index and column in new_record.index:
            current_value = current_record[column]
            new_value = new_record[column]
            
            # Handle NaN comparisons
            if pd.isna(current_value) and pd.isna(new_value):
                continue
            elif pd.isna(current_value) or pd.isna(new_value):
                return True
            elif current_value != new_value:
                return True
    
    return False


def _expire_current_record(records: pd.DataFrame, 
                          current_record_mask: pd.Series,
                          expiration_date_col: str, 
                          is_current_col: str,
                          expiration_date: date) -> pd.DataFrame:
    """
    Expire the current record by setting expiration date and is_current flag.
    
    Parameters:
    records (pd.DataFrame): All customer records.
    current_record_mask (pd.Series): Boolean mask for current record.
    expiration_date_col (str): Expiration date column name.
    is_current_col (str): Is current flag column name.
    expiration_date (date): Date to set as expiration.
    
    Returns:
    pd.DataFrame: Updated records with expired current record.
    """
    updated_records = records.copy()
    updated_records.loc[current_record_mask, expiration_date_col] = expiration_date
    updated_records.loc[current_record_mask, is_current_col] = False
    return updated_records


def _create_new_customer_record(new_record: pd.Series,
                               business_key: str,
                               effective_date_col: str,
                               expiration_date_col: str,
                               is_current_col: str,
                               effective_date: date) -> pd.DataFrame:
    """
    Create a new customer record with SCD metadata.
    
    Parameters:
    new_record (pd.Series): New customer data.
    business_key (str): Business key column name.
    effective_date_col (str): Effective date column name.
    expiration_date_col (str): Expiration date column name.
    is_current_col (str): Is current flag column name.
    effective_date (date): Effective date for the new record.
    
    Returns:
    pd.DataFrame: New customer record as DataFrame.
    """
    record_dict = new_record.to_dict()
    record_dict[effective_date_col] = effective_date
    record_dict[expiration_date_col] = pd.NaT
    record_dict[is_current_col] = True
    
    return pd.DataFrame([record_dict])


def _create_new_version_record(new_record: pd.Series,
                              business_key: str,
                              effective_date_col: str,
                              expiration_date_col: str,
                              is_current_col: str,
                              effective_date: date) -> pd.DataFrame:
    """
    Create a new version record for existing customer.
    
    Parameters:
    new_record (pd.Series): New customer data.
    business_key (str): Business key column name.
    effective_date_col (str): Effective date column name.
    expiration_date_col (str): Expiration date column name.
    is_current_col (str): Is current flag column name.
    effective_date (date): Effective date for the new version.
    
    Returns:
    pd.DataFrame: New version record as DataFrame.
    """
    return _create_new_customer_record(new_record, business_key, effective_date_col,
                                     expiration_date_col, is_current_col, effective_date)


def extract_api_data(base_url: str,
                    endpoint: str,
                    auth_token: Optional[str] = None,
                    auth_type: str = 'bearer',
                    api_key: Optional[str] = None,
                    rate_limit_requests: int = 100,
                    rate_limit_period: int = 60,
                    max_retries: int = 3,
                    timeout: int = 30,
                    pagination_param: str = 'page',
                    page_size_param: str = 'limit',
                    page_size: int = 100,
                    max_pages: Optional[int] = None,
                    additional_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Extract data from an API endpoint with pagination, rate limiting, and authentication.
    
    Parameters:
    base_url (str): Base URL of the API.
    endpoint (str): API endpoint to call.
    auth_token (Optional[str]): Authentication token.
    auth_type (str): Type of authentication ('bearer', 'basic', 'api_key').
    api_key (Optional[str]): API key for authentication.
    rate_limit_requests (int): Maximum requests allowed per period.
    rate_limit_period (int): Time period in seconds for rate limiting.
    max_retries (int): Maximum number of retry attempts.
    timeout (int): Request timeout in seconds.
    pagination_param (str): Parameter name for pagination.
    page_size_param (str): Parameter name for page size.
    page_size (int): Number of records per page.
    max_pages (Optional[int]): Maximum number of pages to fetch.
    additional_params (Optional[Dict[str, Any]]): Additional query parameters.
    
    Returns:
    List[Dict[str, Any]]: Extracted data from all pages.
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize session with retry strategy
        session = _create_http_session(max_retries, timeout)
        
        # Setup authentication headers
        headers = _setup_authentication_headers(auth_token, auth_type, api_key)
        
        # Initialize rate limiting
        rate_limiter = _RateLimiter(rate_limit_requests, rate_limit_period)
        
        # Build base URL
        full_url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Initialize pagination
        all_data = []
        current_page = 1
        total_records = 0
        
        logger.info(f"Starting API data extraction from {full_url}")
        
        while True:
            if max_pages and current_page > max_pages:
                logger.info(f"Reached maximum page limit: {max_pages}")
                break
            
            # Apply rate limiting
            rate_limiter.wait_if_needed()
            
            # Build request parameters
            params = _build_request_params(
                current_page, page_size, pagination_param, 
                page_size_param, additional_params
            )
            
            logger.info(f"Fetching page {current_page} with {page_size} records")
            
            # Make API request
            response_data = _make_api_request(session, full_url, headers, params, timeout)
            
            # Extract data from response
            page_data = _extract_data_from_response(response_data)
            
            if not page_data:
                logger.info("No more data available, stopping pagination")
                break
            
            all_data.extend(page_data)
            total_records += len(page_data)
            
            logger.info(f"Retrieved {len(page_data)} records from page {current_page}")
            
            # Check if we should continue pagination
            if not _should_continue_pagination(response_data, page_data, page_size):
                logger.info("Reached end of data, stopping pagination")
                break
            
            current_page += 1
        
        logger.info(f"API extraction completed. Total records: {total_records}")
        return all_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error during API extraction: {str(e)}")
        raise
    except ValueError as e:
        logger.error(f"Value error during API extraction: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during API extraction: {str(e)}")
        raise


def _create_http_session(max_retries: int, timeout: int) -> requests.Session:
    """
    Create HTTP session with retry strategy.
    
    Parameters:
    max_retries (int): Maximum number of retry attempts.
    timeout (int): Request timeout in seconds.
    
    Returns:
    requests.Session: Configured session object.
    """
    session = requests.Session()
    
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


def _setup_authentication_headers(auth_token: Optional[str], 
                                 auth_type: str, 
                                 api_key: Optional[str]) -> Dict[str, str]:
    """
    Setup authentication headers based on auth type.
    
    Parameters:
    auth_token (Optional[str]): Authentication token.
    auth_type (str): Type of authentication.
    api_key (Optional[str]): API key for authentication.
    
    Returns:
    Dict[str, str]: Headers dictionary with authentication.
    """
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'DataEngineering-Copilot-Workshop/1.0'
    }
    
    if auth_type.lower() == 'bearer' and auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'
    elif auth_type.lower() == 'basic' and auth_token:
        headers['Authorization'] = f'Basic {auth_token}'
    elif auth_type.lower() == 'api_key' and api_key:
        headers['X-API-Key'] = api_key
    
    return headers


def _build_request_params(current_page: int,
                         page_size: int,
                         pagination_param: str,
                         page_size_param: str,
                         additional_params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build request parameters for API call.
    
    Parameters:
    current_page (int): Current page number.
    page_size (int): Number of records per page.
    pagination_param (str): Parameter name for pagination.
    page_size_param (str): Parameter name for page size.
    additional_params (Optional[Dict[str, Any]]): Additional parameters.
    
    Returns:
    Dict[str, Any]: Complete parameters dictionary.
    """
    params = {
        pagination_param: current_page,
        page_size_param: page_size
    }
    
    if additional_params:
        params.update(additional_params)
    
    return params


def _make_api_request(session: requests.Session,
                     url: str,
                     headers: Dict[str, str],
                     params: Dict[str, Any],
                     timeout: int) -> Dict[str, Any]:
    """
    Make API request and handle response.
    
    Parameters:
    session (requests.Session): HTTP session object.
    url (str): Request URL.
    headers (Dict[str, str]): Request headers.
    params (Dict[str, Any]): Request parameters.
    timeout (int): Request timeout.
    
    Returns:
    Dict[str, Any]: Response data as dictionary.
    """
    logger = logging.getLogger(__name__)
    
    try:
        response = session.get(url, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error {response.status_code}: {str(e)}")
        raise
    except requests.exceptions.Timeout as e:
        logger.error(f"Request timeout: {str(e)}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception: {str(e)}")
        raise


def _extract_data_from_response(response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract data array from API response.
    
    Parameters:
    response_data (Dict[str, Any]): API response data.
    
    Returns:
    List[Dict[str, Any]]: Extracted data array.
    """
    # Common patterns for data extraction
    if 'data' in response_data and isinstance(response_data['data'], list):
        return response_data['data']
    elif 'results' in response_data and isinstance(response_data['results'], list):
        return response_data['results']
    elif 'items' in response_data and isinstance(response_data['items'], list):
        return response_data['items']
    elif isinstance(response_data, list):
        return response_data
    else:
        return []


def _should_continue_pagination(response_data: Dict[str, Any],
                               page_data: List[Dict[str, Any]],
                               page_size: int) -> bool:
    """
    Determine if pagination should continue.
    
    Parameters:
    response_data (Dict[str, Any]): API response data.
    page_data (List[Dict[str, Any]]): Current page data.
    page_size (int): Expected page size.
    
    Returns:
    bool: True if pagination should continue, False otherwise.
    """
    # Check if response indicates more pages
    if 'has_more' in response_data:
        return response_data['has_more']
    
    if 'next' in response_data and response_data['next']:
        return True
    
    # Check if current page is smaller than expected page size
    if len(page_data) < page_size:
        return False
    
    return True


class _RateLimiter:
    """Rate limiter for API requests."""
    
    def __init__(self, max_requests: int, time_window: int):
        """
        Initialize rate limiter.
        
        Parameters:
        max_requests (int): Maximum requests allowed.
        time_window (int): Time window in seconds.
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self.logger = logging.getLogger(__name__)
    
    def wait_if_needed(self) -> None:
        """
        Wait if rate limit would be exceeded.
        
        Returns:
        None: Blocks execution if needed.
        """
        current_time = time.time()
        
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests 
                        if current_time - req_time < self.time_window]
        
        # Check if we need to wait
        if len(self.requests) >= self.max_requests:
            oldest_request = min(self.requests)
            wait_time = self.time_window - (current_time - oldest_request)
            
            if wait_time > 0:
                self.logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                time.sleep(wait_time)
        
        # Record this request
        self.requests.append(current_time)


# Example usage and testing
if __name__ == "__main__":
    # Create sample existing customer records
    existing_customers = pd.DataFrame({
        'customer_id': [1, 2, 3],
        'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'email': ['john@email.com', 'jane@email.com', 'bob@email.com'],
        'city': ['New York', 'Los Angeles', 'Chicago'],
        'effective_date': [date(2024, 1, 1), date(2024, 1, 1), date(2024, 1, 1)],
        'expiration_date': [pd.NaT, pd.NaT, pd.NaT],
        'is_current': [True, True, True]
    })
    
    # Create new customer records with some changes
    new_customers = pd.DataFrame({
        'customer_id': [1, 2, 4],
        'name': ['John Doe', 'Jane Smith-Wilson', 'Alice Brown'],
        'email': ['john.doe@newemail.com', 'jane.wilson@email.com', 'alice@email.com'],
        'city': ['New York', 'San Francisco', 'Miami']
    })
    
    # Apply SCD Type 2 logic
    updated_records = apply_scd_type2_logic(
        existing_customers, 
        new_customers,
        process_date=date(2024, 6, 1)
    )
    
    print("Updated customer records with SCD Type 2:")
    print(updated_records.to_string(index=False))
