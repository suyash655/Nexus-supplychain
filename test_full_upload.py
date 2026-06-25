"""
Test full upload process with the API
"""
import requests
import os

# Start the backend server first
csv_path = "data/samples/sample_supply_chain_data.csv"
if not os.path.exists(csv_path):
    print(f"File not found: {csv_path}")
    exit(1)

try:
    with open(csv_path, "rb") as f:
        files = {"file": (csv_path, f, "text/csv")}
        response = requests.post("http://localhost:8000/upload", files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
except requests.exceptions.ConnectionError:
    print("Error: Could not connect to backend server. Make sure it's running on http://localhost:8000")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
