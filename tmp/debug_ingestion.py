import pandas as pd
import io
import numpy as np
import json
import sys
import os

# Create a mock environment for schemas
sys.path.append(os.getcwd())
from backend.core.schemas import SupplyDataSchema

def test_pydantic_validation():
    # Mock DataCo rows (from screenshot)
    data = [
        {
            "Type": "DEBIT",
            "Days for shipping (real)": 3,
            "Days for shipment (scheduled)": 4,
            "Benefit per order": 91.25,
            "Sales per customer": 314.6400146,
            "Delivery Status": "Advance shipping",
            "order date (DateOrders)": "1/31/2018 22:56",
            "shipping date (DateOrders)": "2/3/2018 22:56",
            "Product Name": "Smart watch",
            "Category Name": "Sporting Goods",
            "Product Price": 327.75,
            "Order Item Quantity": 1
        }
    ]
    
    # This is what the auto-detected mapping looks like in the screenshot
    mapping = {
        "region": "Market", # Wait, Market is missing from my mock but it's okay
        "shipment_id": "Order Id", 
        "order_date": "order date (DateOrders)",
        "delivery_date": "shipping date (DateOrders)",
        "category": "Type", # Wait, screenshot shows Type -> category
        "sku": "Order Item Product Price", # Weird mapping in screenshot
        "cost": "Product Price",
        "quantity": "Order Item Quantity",
        "supplier": "Category Name"
    }
    
    for row in data:
        mapped_values = {k: row.get(v) for k, v in mapping.items()}
        print(f"Mapped Values: {mapped_values}")
        try:
            validated = SupplyDataSchema(**mapped_values)
            print("SUCCESS: Row validated correctly")
            print(validated.dict())
        except Exception as e:
            print(f"FAILURE: {e}")
            # print error details
            if hasattr(e, 'errors'):
                print(f"Errors: {e.errors()}")

if __name__ == "__main__":
    test_pydantic_validation()
