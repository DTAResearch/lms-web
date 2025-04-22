import sys, os
# Lấy đường dẫn tuyệt đối của thư mục cha
parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
# Thêm thư mục cha vào sys.path
sys.path.append(parent_directory)
import asyncio
from app.jobs.sync_job_management import DataSyncManager
from app.db.source_db import source_engine
from app.db.target_db import target_engine
from app.utils.telegram_bot import TelegramBot

if __name__ == "__main__":
    try:
        # Khởi tạo Telegram Bot
        bot = TelegramBot(
            token=os.getenv("TELEGRAM_BOT_TOKEN"),
            chat_id=os.getenv("TELEGRAM_CHAT_ID")
        )

        # Khởi tạo DataSyncManager
        sync_manager = DataSyncManager(
            source_engine=source_engine,
            target_engine=target_engine,
            bot=bot,
            batch_size=100,  # Tùy chỉnh batch size
            thread_pool_size=4  # Tùy chỉnh số luồng
        )

        # Thực hiện đồng bộ dữ liệu
        asyncio.run(sync_manager.sync_data("group", delta_days=1))
    except Exception as e:
        print(f"Error during synchronization: {e}")
