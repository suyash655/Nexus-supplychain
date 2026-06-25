import traceback, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

try:
    from core.config import settings
    print("DATABASE_URL:", settings.DATABASE_URL)
    print("Is SQLite:", settings.is_sqlite)
    
    from database import SessionLocal
    db = SessionLocal()
    print("DB session created OK")
    db.close()
    print("DB session closed OK")
    
    import main
    print("SUCCESS: main imported OK")
except Exception:
    traceback.print_exc()
