from contextlib import asynccontextmanager
from db.base import session_factory

SessionLocal = session_factory()


@asynccontextmanager
async def get_db():
    db = SessionLocal
    try:
        yield db
    finally:
        await db.close()
