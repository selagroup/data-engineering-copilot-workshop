# This script connects to a REST API, fetches JSON data, processes the response,
# and saves the results into a local CSV file. The goal is to automate data retrieval
# and analysis from the API. Include error handling, retries, and logging.
import requests
import csv
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s -
    %(message)s')
# Function to create a session with retries
def create_session_with_retries(retries, backoff_factor, status_forcelist):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session
# Function to fetch data from the API
def fetch_data(api_url):
    session = create_session_with_retries(retries=3, backoff_factor=0.3,
        status_forcelist=(500, 502, 504))
    try:
        response = session.get(api_url)
        response.raise_for_status()  # Raise an error for bad responses
        logging.info('Data fetched successfully from API.')
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f'Error fetching data from API: {e}')
        return None
