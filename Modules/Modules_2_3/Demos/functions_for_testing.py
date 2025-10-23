"""
Sales Data Processing Module

This module contains various functions for processing sales data with interesting edge cases.
Perfect for demonstrating Copilot's /tests capability.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re


def calculate_discount(price: float, discount_percent: float) -> float:
    """
    Calculate the final price after applying a discount.
    
    Args:
        price: Original price
        discount_percent: Discount percentage (0-100)
    
    Returns:
        Final price after discount
    """
    if price < 0:
        raise ValueError("Price cannot be negative")
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount percent must be between 0 and 100")
    
    return price * (1 - discount_percent / 100)


def parse_order_id(order_id: str) -> Dict[str, str]:
    """
    Parse an order ID into its components.
    Expected format: ORD-YYYY-NNNN (e.g., ORD-2024-0001)
    
    Args:
        order_id: Order ID string
    
    Returns:
        Dictionary with 'year' and 'number' keys
    """
    pattern = r'^ORD-(\d{4})-(\d{4})$'
    match = re.match(pattern, order_id)
    
    if not match:
        raise ValueError(f"Invalid order ID format: {order_id}")
    
    return {
        'year': match.group(1),
        'number': match.group(2)
    }


def calculate_shipping_cost(weight: float, distance: float, express: bool = False) -> float:
    """
    Calculate shipping cost based on weight, distance, and shipping type.
    
    Args:
        weight: Package weight in kg
        distance: Shipping distance in km
        express: Whether to use express shipping
    
    Returns:
        Shipping cost in currency units
    """
    if weight <= 0:
        raise ValueError("Weight must be positive")
    if distance <= 0:
        raise ValueError("Distance must be positive")
    
    base_cost = weight * 0.5 + distance * 0.1
    
    if express:
        base_cost *= 1.5
    
    # Minimum charge
    return max(base_cost, 5.0)


def group_orders_by_status(orders: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group orders by their status.
    
    Args:
        orders: List of order dictionaries with 'status' key
    
    Returns:
        Dictionary mapping status to list of orders
    """
    if not orders:
        return {}
    
    grouped = {}
    for order in orders:
        if 'status' not in order:
            raise KeyError("Order missing 'status' field")
        
        status = order['status']
        if status not in grouped:
            grouped[status] = []
        grouped[status].append(order)
    
    return grouped


def calculate_loyalty_points(total_amount: float, customer_tier: str = 'bronze') -> int:
    """
    Calculate loyalty points based on purchase amount and customer tier.
    
    Args:
        total_amount: Total purchase amount
        customer_tier: Customer tier ('bronze', 'silver', 'gold', 'platinum')
    
    Returns:
        Number of loyalty points earned
    """
    tier_multipliers = {
        'bronze': 1.0,
        'silver': 1.5,
        'gold': 2.0,
        'platinum': 3.0
    }
    
    if total_amount < 0:
        raise ValueError("Total amount cannot be negative")
    
    tier_lower = customer_tier.lower()
    if tier_lower not in tier_multipliers:
        raise ValueError(f"Invalid customer tier: {customer_tier}")
    
    base_points = total_amount * 10  # 10 points per currency unit
    return int(base_points * tier_multipliers[tier_lower])


def is_business_day(date: datetime, holidays: Optional[List[datetime]] = None) -> bool:
    """
    Check if a given date is a business day (Monday-Friday, excluding holidays).
    
    Args:
        date: Date to check
        holidays: Optional list of holiday dates
    
    Returns:
        True if business day, False otherwise
    """
    # Check if weekend (Saturday=5, Sunday=6)
    if date.weekday() >= 5:
        return False
    
    # Check if holiday
    if holidays:
        date_only = date.replace(hour=0, minute=0, second=0, microsecond=0)
        for holiday in holidays:
            holiday_only = holiday.replace(hour=0, minute=0, second=0, microsecond=0)
            if date_only == holiday_only:
                return False
    
    return True


def calculate_delivery_date(order_date: datetime, processing_days: int = 2) -> datetime:
    """
    Calculate expected delivery date, accounting for business days only.
    
    Args:
        order_date: Date the order was placed
        processing_days: Number of business days for processing
    
    Returns:
        Expected delivery datetime
    """
    if processing_days < 0:
        raise ValueError("Processing days cannot be negative")
    
    current_date = order_date
    days_added = 0
    
    while days_added < processing_days:
        current_date += timedelta(days=1)
        if is_business_day(current_date):
            days_added += 1
    
    return current_date


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not email:
        return False
    
    # Basic email validation pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def merge_customer_data(primary: Dict, secondary: Dict) -> Dict:
    """
    Merge two customer data dictionaries, with primary taking precedence.
    
    Args:
        primary: Primary customer data
        secondary: Secondary customer data (fallback)
    
    Returns:
        Merged customer dictionary
    """
    if not isinstance(primary, dict) or not isinstance(secondary, dict):
        raise TypeError("Both arguments must be dictionaries")
    
    merged = secondary.copy()
    
    for key, value in primary.items():
        # Only use primary value if it's not None or empty string
        if value is not None and value != '':
            merged[key] = value
    
    return merged


def calculate_tax(amount: float, tax_rate: float, region: str = 'US') -> float:
    """
    Calculate tax amount based on region-specific rules.
    
    Args:
        amount: Base amount before tax
        tax_rate: Tax rate as decimal (e.g., 0.20 for 20%)
        region: Region code for special tax rules
    
    Returns:
        Tax amount
    """
    if amount < 0:
        raise ValueError("Amount cannot be negative")
    if tax_rate < 0 or tax_rate > 1:
        raise ValueError("Tax rate must be between 0 and 1")
    
    # Tax-free threshold for certain regions
    tax_free_thresholds = {
        'US': 0,
        'EU': 22,  # Small value exemption
        'UK': 15
    }
    
    threshold = tax_free_thresholds.get(region, 0)
    
    if amount <= threshold:
        return 0.0
    
    return (amount - threshold) * tax_rate
