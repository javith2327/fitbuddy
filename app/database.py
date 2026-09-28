from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


# SQLite needs special connection settings when used with FastAPI.
is_sqlite = settings.database_url.startswith("sqlite")

connect_args = {}

if is_sqlite:
    connect_args = {
        "check_same_thread": False,
        "timeout": 30,
    }


engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()