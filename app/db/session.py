from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base


database_url = make_url(settings.DATABASE_URL)
engine_options = {"pool_pre_ping": True}

if database_url.get_backend_name() == "sqlite":
    engine_options["connect_args"] = {"check_same_thread": False}
else:
    engine_options.update(
        pool_size=10,
        max_overflow=20,
        pool_recycle=1800,
    )

engine = create_engine(settings.DATABASE_URL, **engine_options)

if database_url.get_backend_name() == "sqlite":
    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()