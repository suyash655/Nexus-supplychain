import sys
import os
from sqlalchemy import text
sys.path.append(os.getcwd())
# Fix imports
from backend.database import engine
from backend.models import Base

def check_db():
    print(f"Database Engine: {engine.url}")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = [row[0] for row in result]
            print(f"Tables in DB: {tables}")
            
            if 'supply_data' in tables:
                count = conn.execute(text("SELECT COUNT(*) FROM supply_data;")).scalar()
                print(f"Current rows in supply_data: {count}")
            else:
                print("CRITICAL: supply_data table MISSING!")
    except Exception as e:
        print(f"DB Error: {e}")

if __name__ == "__main__":
    check_db()
