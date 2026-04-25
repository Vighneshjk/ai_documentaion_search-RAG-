from fastapi import Depends
from app.db.database import get_db
from app.services.vector_store import get_vector_store, VectorStoreBase
from app.core.config import settings

_vector_store_instance = None

def get_vector_store_depend() -> VectorStoreBase:
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = get_vector_store(settings)
    return _vector_store_instance
