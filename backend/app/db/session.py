from contextlib import asynccontextmanager
from db.base import async_session

SessionLocal = async_session()


@asynccontextmanager
async def get_db():
    db = SessionLocal
    try:
        yield db
    finally:
        await db.close()
