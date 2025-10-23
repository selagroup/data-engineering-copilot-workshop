import pytest
from Modules.Modules_2_3.Demos.functions_for_testing import calculate_discount

def test_calculate_discount_normal():
    assert calculate_discount(100, 20) == 80.0
    assert calculate_discount(50, 0) == 50.0
    assert calculate_discount(200, 100) == 0.0

def test_calculate_discount_zero_price():
    assert calculate_discount(0, 10) == 0.0

def test_calculate_discount_invalid_price():
    with pytest.raises(ValueError, match="Price cannot be negative"):
        calculate_discount(-10, 10)

def test_calculate_discount_invalid_discount_percent_negative():
    with pytest.raises(ValueError, match="Discount percent must be between 0 and 100"):
        calculate_discount(100, -5)

def test_calculate_discount_invalid_discount_percent_above_100():
    with pytest.raises(ValueError, match="Discount percent must be between 0 and 100"):
        calculate_discount(100, 150)

if __name__ == "__main__":
    pytest.main()