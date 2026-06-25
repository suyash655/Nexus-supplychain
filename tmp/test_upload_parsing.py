import io
import pandas as pd
import os

def test_parse():
    file_path = "sample_supply_chain_data.csv"
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    with open(file_path, "rb") as f:
        contents = f.read()
    
    print(f"Read {len(contents)} bytes from {file_path}")
    
    try:
        # Emulate the backend logic
        df = pd.read_csv(io.BytesIO(contents))
        print("Successfully parsed CSV with pandas")
        print(df.head())
    except Exception as e:
        print(f"FAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parse()
