"""
Module thực hiện đồng bộ tin nhắn giữa source database và target database.
"""

import sys
import os
import asyncio
import contextlib

# Lấy đường dẫn tuyệt đối của thư mục cha
PARENT_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PARENT_DIRECTORY)

from app.jobs.sync_job_management import DataSyncManager
from app.db.source_db import source_engine, get_source_session
from app.db.target_db import target_engine, get_target_session
from app.utils.telegram_bot import TelegramBot
from app.api.handle_chat import handle_all_chat_data


async def sync_chat():
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
        
        # Khởi tạo target db
        with contextlib.closing(next(get_target_session())) as target_db:
            with contextlib.closing(next(get_source_session())) as source_db:
                await sync_manager.sync_data("chat", delta_days=1)
                await handle_all_chat_data(target_db=target_db, source_db=source_db)
    except Exception as e:
        print(f"Error during synchronization: {e}")

if __name__ == "__main__":
    asyncio.run(sync_chat())
