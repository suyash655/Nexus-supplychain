"""
Test date parsing specifically
"""
import sys
sys.path.insert(0, 'backend')
import pandas as pd
import io

csv_data = """supplier,sku,warehouse,region,shipment_id,order_date,delivery_date,delay_days,cost,quantity,category,quality_score
Global Logistics,SKU-100,WH-North,Region-1,SHP-001,2023-01-01,2023-01-05,4,1200.50,500,Electronics,95.0
Swift Source,SKU-200,WH-South,Region-2,SHP-002,2023-01-02,2023-01-03,1,850.00,300,Textiles,88.0
Apex Supply,SKU-100,WH-North,Region-1,SHP-003,2023-01-03,2023-01-10,7,1500.00,450,Electronics,72.0"""

df = pd.read_csv(io.StringIO(csv_data))
print("DataFrame columns:", df.columns.tolist())
print("\norder_date values:", df['order_date'].tolist())
print("delivery_date values:", df['delivery_date'].tolist())

# Test the validator's date parsing logic
def _is_parseable_date(v) -> bool:
    if v is None or str(v).strip() in ("", "nan", "NaT"):
        return True
    try:
        pd.to_datetime(str(v), infer_datetime_format=True)
        return True
    except Exception:
        return False

for idx, row in df.head(3).iterrows():
    order_date = row['order_date']
    delivery_date = row['delivery_date']
    
    print(f"\nRow {idx}:")
    print(f"  order_date: {order_date} -> parseable: {_is_parseable_date(order_date)}")
    print(f"  delivery_date: {delivery_date} -> parseable: {_is_parseable_date(delivery_date)}")
    
    # Try direct pandas parsing
    try:
        parsed = pd.to_datetime(order_date, infer_datetime_format=True)
        print(f"  Pandas parsed order_date: {parsed}")
    except Exception as e:
        print(f"  Pandas failed to parse order_date: {e}")
