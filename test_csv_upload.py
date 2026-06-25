"""
Test CSV upload parsing directly
"""
import io
import pandas as pd
import sys
sys.path.insert(0, 'backend')

from app.services.upload.parser import parse_upload_file
from app.services.upload.schema import auto_detect_columns, mapping_dict_from_detection, low_confidence_fields
from app.services.upload.validator import validate_mapped_values

# Test with sample CSV
csv_path = "data/samples/test_upload.csv"
with open(csv_path, "rb") as f:
    contents = f.read()

print(f"File size: {len(contents)} bytes")
print(f"File: {csv_path}")

try:
    # Test parsing
    df = parse_upload_file(contents, "test_upload.csv", max_bytes=50*1024*1024)
    print(f"\nParsing successful")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nFirst few rows:")
    print(df.head())
    
    # Test column detection
    detection = auto_detect_columns(df.columns.tolist(), sample_data=df.head(50).to_dict("records"))
    print(f"\nColumn detection successful")
    print(f"Detection result: {detection}")
    
    mapping = mapping_dict_from_detection(detection)
    print(f"\nMapping: {mapping}")
    
    low_conf = low_confidence_fields(detection)
    print(f"\nLow confidence fields: {low_conf}")
    
    # Test validation
    validation = validate_mapped_values(df, mapping)
    print(f"\nValidation result: {validation}")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
