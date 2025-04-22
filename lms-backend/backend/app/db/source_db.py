"""
Kết nối đến source database với retry logic.
"""

import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from ..core.config import settings
# Tạo kết nối tới source database (SQLite)
source_engine = create_engine(settings.SOURCE_DATABASE_URL)
SourceSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=source_engine)

def get_source_session():
    """
    Tạo session kết nối tới source database.
    
    Yields:
        sqlalchemy.orm.Session: Đối tượng session để thao tác database.
    """
    db = SourceSessionLocal()
    try:
        yield db
    finally:
        db.close()

#Kiểm tra kết nối đến source database với retry logic.
#Thử kết nối tối đa `MAX_RETRIES` lần, mỗi lần cách nhau `RETRY_INTERVAL` giây.
max_retries = settings.MAX_RETRIES
retry_interval = settings.RETRY_INTERVAL
def check_source_db_connection():
    """
    Kiểm tra kết nối đến source database với retry logic
    """
    retry_count = 0

    while retry_count < max_retries:
        try:
            with source_engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    print("✅ Source DB connected successfully.")
                    return
        except SQLAlchemyError as error:
            print(f"⚠️ Lỗi kết nối source DB: {error}. Thử lại sau {retry_interval} giây...")
            retry_count += 1
            time.sleep(retry_interval)

    print("❌ Không thể kết nối với source DB sau nhiều lần thử.")
check_source_db_connection()
