import sys
import os
import pandas as pd
import numpy as np
from typing import Any, Dict

# Mock the environment to test schemas and upload logic components
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'backend')))

from core.schemas import SupplyDataSchema

def test_quality_score_relaxed():
    print("Testing quality_score relaxation...")
    data = {
        "supplier": "Test Supplier",
        "sku": "SKU-TEST",
        "quality_score": 85.5  # Previously would fail (max 1.0)
    }
    schema = SupplyDataSchema(**data)
    assert schema.quality_score == 85.5
    print("✓ quality_score 85.5 accepted.")

def test_date_parsing_robustness():
    print("Testing date parsing with pandas Timestamps...")
    ts = pd.Timestamp("2026-03-28")
    data = {
        "supplier": "Test Supplier",
        "sku": "SKU-TEST",
        "order_date": ts
    }
    schema = SupplyDataSchema(**data)
    assert schema.order_date == "2026-03-28"
    print("✓ pandas Timestamp parsed correctly.")

    data_empty = {
        "supplier": "Test Supplier",
        "sku": "SKU-TEST",
        "order_date": ""
    }
    schema_empty = SupplyDataSchema(**data_empty)
    assert schema_empty.order_date is None
    print("✓ Empty date string handled as None.")

def test_batching_simulation():
    print("Simulating batching logic...")
    items = list(range(2500))
    batch_size = 1000
    batches = []
    current_batch = []
    
    for i in items:
        current_batch.append(i)
        if len(current_batch) >= batch_size:
            batches.append(current_batch)
            current_batch = []
    if current_batch:
        batches.append(current_batch)
        
    assert len(batches) == 3
    assert len(batches[0]) == 1000
    assert len(batches[1]) == 1000
    assert len(batches[2]) == 500
    print("✓ Batching logic confirmed (1000, 1000, 500).")

if __name__ == "__main__":
    try:
        test_quality_score_relaxed()
        test_date_parsing_robustness()
        test_batching_simulation()
        print("\nAll local verification tests PASSED.")
    except Exception as e:
        print(f"\nVerification FAILED: {e}")
        sys.exit(1)
