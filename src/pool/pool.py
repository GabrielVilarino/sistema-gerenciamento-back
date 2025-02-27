from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os

HOST = os.getenv("HOST")
USER_DB = os.getenv("USER_DB")
PASSWD = os.getenv("PASSWD")
DB = os.getenv("DB")
PORT = os.getenv("PORT")

DATABASE_URL = f"postgresql+asyncpg://{USER_DB}:{PASSWD}@{HOST}/{DB}"

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    async with async_session() as session:
        yield session