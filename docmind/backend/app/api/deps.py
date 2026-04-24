from app.db.database import get_db
from app.services.vector_store import get_vector_store, VectorStoreBase
from app.core.config import settings

def get_vector_store_depend() -> VectorStoreBase:
    return get_vector_store(settings)
