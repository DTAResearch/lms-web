# backend\app\core\config.py
import json
import os

from dotenv import load_dotenv
load_dotenv()

class Settings:
    """
    Lớp Settings chứa các biến môi trường cần thiết cho ứng dụng.
    Dữ liệu được lấy từ biến môi trường của docker-compose hoặc giá trị mặc định.
    """

    def __init__(self):
        print("==== DEBUG ENVIRONMENT VARIABLES ====")
        print("PATH:", os.getenv("PATH"))
        print("SOURCE_DATABASE_URL:", os.getenv("SOURCE_DATABASE_URL"))
        print("PYTHONPATH:", os.getenv("PYTHONPATH"))

        # Debug và lấy biến môi trường từ docker-compose
        self.SOURCE_DATABASE_URL = os.getenv("SOURCE_DATABASE_URL")
        if not self.SOURCE_DATABASE_URL:
            raise ValueError("SOURCE_DATABASE_URL is not set in environment variables")
        print(f"DEBUG: SOURCE_DATABASE_URL = {self.SOURCE_DATABASE_URL}")

        self.TARGET_DATABASE_URL = os.getenv("TARGET_DATABASE_URL")
        if not self.TARGET_DATABASE_URL:
            raise ValueError("TARGET_DATABASE_URL is not set in environment variables")
        print(f"DEBUG: TARGET_DATABASE_URL = {self.TARGET_DATABASE_URL}")

        # RETRY CONNECT DATABASE
        self.MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
        print(f"DEBUG: MAX_RETRIES = {self.MAX_RETRIES}")
        self.RETRY_INTERVAL = int(os.getenv("RETRY_INTERVAL", "30"))
        # Các biến khác giữ nguyên
        self.HOC_TIEP_BE_URL = os.getenv("HOC_TIEP_BE_URL")
        self.HOC_TIEP_KEY = os.getenv("HOC_TIEP_KEY")
        self.BATCH_HANDLE_CHAT = int(os.getenv("BATCH_HANDLE_CHAT", "100"))
        self.METABASE_SECRET_KEY = os.getenv("METABASE_SECRET_KEY")
        self.METABASE_SITE_URL = os.getenv("METABASE_SITE_URL")
        self.TIME_EXPIRATION = int(os.getenv("TIME_EXPIRATION", "90"))
        # self.TIME_EXPIRATION_UNIT = os.getenv("TIME_EXPIRATION_UNIT", "minutes")
        self.RESOURCE_IFRAME_URL = json.loads(os.getenv("RESOURCE_IFRAME_URL", "{}"))
        self.REQUEST_LIMIT_DEFAULT = int(os.getenv("REQUEST_LIMIT_DEFAULT", "1000"))
        self.TOKEN_LIMT_DEFAULT = int(os.getenv("TOKEN_LIMT_DEFAULT", "10000"))
        self.ADMIN_DASHBOARD_ID = int(os.getenv("ADMIN_DASHBOARD_ID", "3"))
        self.TEACHER_DASHBOARD_ID = int(os.getenv("TEACHER_DASHBOARD_ID", "6"))
        self.STUDENT_DASHBOARD_ID = int(os.getenv("STUDENT_DASHBOARD_ID", "5"))
        self.GROUP_STATS_DASHBOARD_ID = int(os.getenv("GROUP_STATS_DASHBOARD_ID", "9"))

    def get(self, key: str, default=None):
        """Lấy giá trị biến môi trường từ lớp Settings"""
        return getattr(self, key, default)

settings = Settings()