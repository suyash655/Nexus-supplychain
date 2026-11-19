import pytest
from app.core.database import engine
from app.models import Base

# Also import any models not in app.models if needed
try:
    from app.models.models import *  # noqa: F403
except Exception:
    pass

@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    Base.metadata.create_all(bind=engine)
    yield
