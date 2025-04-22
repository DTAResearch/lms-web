"""
Kết nối đến target db.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from ..core.config import settings
# Ket noi SQLite
target_engine = create_engine(settings.TARGET_DATABASE_URL, pool_size=10, max_overflow=20, pool_timeout=30, pool_recycle=1800)
TargetSessionLocal  = sessionmaker(autocommit= False, autoflush=False, bind=target_engine)

def get_target_session():
    """
    Tạo session kết nối source db.
    """
    db_target = TargetSessionLocal()
    try:
        yield db_target
    finally:
        db_target.close()

# Kiểm tra kết nối PostgreSQL
try:
    with target_engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Target DB connected successfully.")
except SQLAlchemyError as e:
    print(f"Error connecting target DB : {e}")
