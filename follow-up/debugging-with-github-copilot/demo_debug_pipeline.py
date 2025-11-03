"""
Demo Data Pipeline Script - WITH INTENTIONAL BUGS FOR DEBUGGING EXERCISE
=======================================================================

This script demonstrates a typical ETL pipeline with 3 carefully selected bugs
that students will debug with GitHub Copilot assistance.

Pipeline Flow:
1. Extract data from CSV files
2. Transform and clean the data
3. Validate data quality
4. Load to database/output files

INSTRUCTOR: This script contains 3 intentional bugs of varying difficulty levels:
- Bug 1: Path concatenation type error (Line ~49)
- Bug 2: DateTime conversion without error handling (Line ~65) 
- Bug 3: Logic error in conditions (Line ~74)
Run this script to see the errors, then use GitHub Copilot to debug step by step.
"""

import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime
from pathlib import Path

class DataPipeline:
    def __init__(self, data_dir="../../setup/sample_data", output_dir="output"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.customers = None
        self.orders = None
        self.products = None
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True)
        
    def extract_data(self):
        """Extract data from CSV files"""
        
        try:
            self.customers = pd.read_csv(self.data_dir + "/customers.csv")
            self.orders = pd.read_csv(self.data_dir / "orders.csv")
            self.products = pd.read_csv(self.data_dir / "products.csv")
            
        except FileNotFoundError as e:
            raise
            
    def transform_customer_data(self):
        """Transform customer data"""
        
        if self.customers is None:
            raise ValueError("Customer data not loaded. Run extract_data() first.")
        
        # Incorrect datetime conversion (missing error handling)
        self.customers['signup_date'] = pd.to_datetime(self.customers['signup_date'])
        
        # Calculate customer tenure in days
        today = datetime.now()
        self.customers['tenure_days'] = (today - self.customers['signup_date']).dt.days
        
        # Categorize customers by tenure
        conditions = [
            self.customers['tenure_days'] < 30,
            self.customers['tenure_days'] < 365,
            self.customers['tenure_days'] > 365
        ]
        choices = ['New', 'Regular', 'Loyal']
        self.customers['customer_category'] = np.select(conditions, choices, default='Unknown')
        
        # Clean email addresses (Fix Bug 4 - handle NaN values properly)
        self.customers['email_domain'] = self.customers['email'].str.split('@').str[1]
        self.customers['email_domain'] = self.customers['email_domain'].fillna('unknown')
        
    def calculate_order_metrics(self):
        """Calculate order metrics"""
        
        if self.orders is None:
            raise ValueError("Order data not loaded. Run extract_data() first.")
            
        customer_metrics = self.orders.groupby('customer_id').agg({
            'total_amount': ['sum', 'mean', 'count'],
            'order_date': ['min', 'max']
        }).round(2)
        
        # Flatten column names
        customer_metrics.columns = [
            'total_spent', 'avg_order_value', 'order_count', 
            'first_order', 'last_order'
        ]
        
        self.customers = self.customers.merge(
            customer_metrics, 
            left_on='customer_id', 
            right_index=True, 
            how='left'
        )
        
    def validate_data_quality(self):
        """Validate data quality"""
        
        issues = []
        
        # Check for missing critical fields
        if self.customers['customer_name'].isnull().any():
            issues.append("Missing customer names found")
            
        if self.customers['email'].isnull().any():
            issues.append("Missing customer emails found")
            
        # Fixed validation logic (Bug 6 fixed - check for non-positive values)
        if (self.customers['total_spent'] <= 0).any():
            issues.append("Non-positive total spent values found")
            
        # Check for duplicate customers
        duplicates = self.customers['email'].duplicated().sum()
        if duplicates > 0:
            issues.append(f"{duplicates} duplicate email addresses found")
            
        return issues
        
    def save_results(self):
        """Save processed data to output files"""
        
        # Save customer analysis
        customer_output = self.output_dir / "customer_analysis.csv"
        self.customers.to_csv(customer_output, index=False)
        
        # Create summary report
        summary = {
            'total_customers': len(self.customers),
            'total_orders': len(self.orders),
            'avg_customer_value': self.customers['total_spent'].mean(),
            'processing_timestamp': datetime.now().isoformat()
        }
        
        summary_output = self.output_dir / "pipeline_summary.txt"
        with open(summary_output, 'w') as f:
            for key, value in summary.items():
                f.write(f"{key}: {value}\n")
                
    def run_pipeline(self):
        """Run the complete data pipeline"""
        
        try:
            self.extract_data()
            self.transform_customer_data()
            self.calculate_order_metrics()
            
            # Validate data quality
            issues = self.validate_data_quality()
            
            self.save_results()
            
            return True
            
        except Exception as e:
            return False

def main():
    """Main function to run the pipeline"""
    print("🚀 Starting Demo Data Pipeline (Shortened Debugging Exercise)")
    print("📝 This script contains 3 intentional bugs for educational purposes")
    print("-" * 60)
    
    # Initialize and run pipeline
    pipeline = DataPipeline()
    success = pipeline.run_pipeline()
    
    if success:
        print("\n✅ Pipeline completed successfully!")
        print("📊 Check the 'output' directory for results")
        print("🎯 All 3 core debugging concepts demonstrated!")
    else:
        print("\n❌ Pipeline failed - time to debug with Copilot!")
        print("💡 Use GitHub Copilot + VS Code debugger to fix the issues")
        print("🔧 Focus on the 3 main bug types: Type Error, Data Error, Logic Error")

if __name__ == "__main__":
    main()