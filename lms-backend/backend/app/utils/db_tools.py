from sqlalchemy import inspect
from app.db.target_db import target_engine
from app.db.source_db import source_engine

def log_all_tables(engine):
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tables in the database:")
    for table in tables:
        print(f"- {table}")

# Để log bảng trong Postgres

def log_postgres_tables():
    log_all_tables(target_engine)

# Để log bảng trong SQLite

def log_sqlite_tables():
    log_all_tables(source_engine)