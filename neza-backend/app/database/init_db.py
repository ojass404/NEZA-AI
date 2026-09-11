from sqlalchemy import text
from app.database.connection import engine
from app.database.base import Base
from app.models import scan, scan_metadata, detection, report

def init_db():
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__": init_db()
