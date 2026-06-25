from sqlalchemy import create_engine, event  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore

from app.core.config import settings  # type: ignore

DATABASE_URL = settings.DATABASE_URL

_connect_args = {}
if settings.is_sqlite:
    _connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    connect_args=_connect_args,
    pool_recycle=300,  # recycle connections every 5 min to avoid stale handles
)


# Enable WAL journal mode for better concurrent read/write (SQLite only)
if settings.is_sqlite:
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
