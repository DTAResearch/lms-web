"""
Module for managing data synchronization between source and target databases.
"""
import os
import sys
import time
import json
import threading
import asyncio
import logging
import traceback
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional

from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import Table, MetaData, inspect, select, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.engine import Engine

# Lấy đường dẫn tuyệt đối của thư mục cha
parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
# Thêm thư mục cha vào sys.path
sys.path.append(parent_directory)

from app.model.base import Base
from app.model.user import User
from app.model.model import Model
from app.model.chat import Chat
from app.model.group_user import GroupUser
from app.model.model_group import ModelGroup
from app.model.group import Group
from app.utils.telegram_bot import TelegramBot

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
BATCH_SIZE = 150  # Adjusted batch size for stability
THREAD_POOL_SIZE = 8  # Number of parallel threads

# Lock for synchronizing access to last_id
lock = threading.Lock()
class DataSyncManager:
    """Class to manage data synchronization between source and target databases."""
    def __init__(
        self,
        source_engine: Engine,
        target_engine: Engine,
        bot: Optional[TelegramBot] = None,
        batch_size: int = BATCH_SIZE,
        thread_pool_size: int = THREAD_POOL_SIZE
    ) -> None:
        self.source_engine = source_engine
        self.target_engine = target_engine
        self.bot = bot
        self.batch_size = batch_size
        self.thread_pool_size = thread_pool_size
        self.lock = threading.Lock()    
    def ensure_table_exists(self, base, table_name: str):
        """Ensure table exists in the target database."""
        inspector = inspect(self.target_engine)
        if table_name not in inspector.get_table_names():
            logging.info("Table '%s' not found. Creating...", table_name)
            base.metadata.create_all(self.target_engine, tables=[base.metadata.tables[table_name]])
            logging.info("Table '%s' created successfully.", table_name)
        else:
            logging.info("Table '%s' already exists.", table_name)
    def fetch_batch_data(self ,session: Session, table: Table, last_id: str, delta_time_epoch: Optional[int] = None) -> List[Dict]:
        """Fetch a batch of data from the source table."""
        query = (
            select(table).
            where(table.c.id > str(last_id)).
            order_by(table.c.id).
            limit(self.batch_size)
        )
        if delta_time_epoch:
            query = query.where(table.c.updated_at >= int(delta_time_epoch))
        result = session.execute(query).fetchall()  # Execute query and fetch the data
        return result

    # Fetch a batch of data from the source table
    # def fetch_batch_data_all(self ,session: Session, table: Table, last_id: str, batch_size: int) -> List[Dict]:
    #     """Fetch a batch of data from the source table when data is empty."""
    #     query = select(table).where(table.c.id > str(last_id)).order_by(table.c.id).limit(self.batch_size)
    #     return session.execute(query).fetchall()
    
    def fetch_batch_data_all(self, session: Session, table: Table, last_key: tuple, batch_size: int) -> List[Dict]:
        """Fetch a batch of data from the source table when data is empty, supporting composite keys."""
        pk_columns = list(table.primary_key.columns)  # Lấy danh sách cột khóa chính
        if len(pk_columns) == 1:  # Trường hợp khóa chính đơn
            pk_col = pk_columns[0]
            query = (
                select(table)
                .where(pk_col > str(last_key[0]))
                .order_by(pk_col)
                .limit(self.batch_size)
            )
        else:  # Trường hợp khóa chính composite (như model_group)
            model_id_col, group_id_col = pk_columns  # Giả sử thứ tự là model_id, group_id
            last_model_id, last_group_id = last_key
            query = (
                select(table)
                .where(
                    (model_id_col > last_model_id) |
                    ((model_id_col == last_model_id) & (group_id_col > last_group_id))
                )
                .order_by(model_id_col, group_id_col)
                .limit(self.batch_size)
            )
        return session.execute(query).fetchall()

    # Perform batch upserts into the target table
    def insert_or_update_data(self ,session: Session, table: Table, data: List[Dict]) -> None:
        """Perform batch upserts into the target table."""
        if not data:
            return 
        try:
            # Danh sách các cột trong bảng đích
            target_columns = {col.name for col in table.columns}
            # Chuyển đổi dữ liệu
            transformed_data = []
            for row in data:
                transformed_row = {}
                for col in table.columns:
                    if col.name in row and col.name in target_columns:
                        value = row[col.name]
                        # Chuyển đổi các cột JSONField sang chuỗi JSON
                        if isinstance(value, dict):
                            value = json.dumps(value)
                        transformed_row[col.name] = value
                transformed_data.append(transformed_row)
            stmt = pg_insert(table).values(transformed_data)
            upsert_stmt = stmt.on_conflict_do_update(
                index_elements=["id"],
                set_={col: stmt.excluded[col] for col in target_columns if col != "id"})
            result = session.execute(upsert_stmt)
            session.commit()
            logging.info(f"Batch processed: {len(transformed_data)} rows inserted/updated.")
            # Log số lượng bản ghi được thêm hoặc cập nhật
            added = result.rowcount
            logging.info(f"Batch processed: {added} rows inserted/updated.")
            # Gửi thông báo qua bot nếu có
            if self.bot:
                self.bot.add_message(f"✅ Đã xử lý {added} bản ghi trong batch này.")
        except Exception as e:
            session.rollback()
            logging.error(f"Error during upsert: {e}")
            # Optional: Send failure notification to bot
            if self.bot:
                self.bot.add_message(f"❌ Xảy ra lỗi khi xử lý batch: {e}")

    def process_batch(self, source_session: Session, target_session: Session, source_table: Table, target_table: Table, last_id: str, delta_time_epoch: int, max_retries: int = 3, bot: Optional[TelegramBot] = None) -> Optional[str]:
        """Process batch"""
        logging.info(f"Fetching batch starting from ID: {last_id}")
        batch_data = self.fetch_batch_data(source_session, source_table, last_id, delta_time_epoch)
        if not batch_data:
            logging.info(f"No more data to fetch after ID: {last_id}.")
            if self.bot:
                self.bot.add_message(f"✅ Không có dữ liệu mới cần đồng bộ sau ID: {last_id}.")
            return None
        logging.info(f"Fetched {len(batch_data)} rows in the batch.")
        target_columns = {col.name for col in target_table.columns}
        transformed_data = [
            {
                col.name: (
                    json.dumps(row._mapping[col.name]) 
                    if col.name in row._mapping and isinstance(row._mapping[col.name], dict) 
                    else row._mapping[col.name] 
                    if col.name in row._mapping 
                    else None
                )
                for col in source_table.columns
                if col.name in target_columns
            }
            for row in batch_data
        ]

        logging.info(f"Transformed {len(transformed_data)} rows for insertion/update.")

        if self.bot:
            self.bot.add_message(f"🔄 Đã chuyển đổi {len(transformed_data)} dòng dữ liệu để chèn/cập nhật.")

        self.insert_or_update_data(target_session, target_table, transformed_data)
        logging.info(f"Inserted/updated {len(transformed_data)} rows in the target table.")

        if bot:
            bot.add_message(f"✅ Đã chèn/cập nhật {len(transformed_data)} dòng dữ liệu vào bảng `{target_table.name}`.")

        last_row = batch_data[-1]  
        last_id = str(last_row._mapping["id"])

        logging.info(f"Processed batch up to ID: {last_id}.")
        return last_id

    # Synchronize data between source and target tables using parallel processing
    def process_sync(
        self,
        source_session: Session,
        target_session: Session,
        source_table: Table,
        target_table: Table,
        delta_days: int,
        bot: Optional[TelegramBot] = None
) -> None:
        retry_count = int(os.getenv('RETRY_COUNT', 0))
        max_retries = int(os.getenv('MAX_RETRIES', 3))
        retry_interval = int(os.getenv('RETRY_INTERVAL', 30))

        while retry_count < max_retries:
            try:
                # Chuyển datetime về BigInt (seconds)
                current_timestamp_ms = int(datetime.now().timestamp())  # UNIX timestamp dạng seconds
                delta_seconds = int(timedelta(days=delta_days).total_seconds())  # Lấy số giây

                # Tính delta_time
                delta_time = current_timestamp_ms - delta_seconds

                print("Datetime (ms):", current_timestamp_ms)  # Dạng BIGINT
                print("Timedelta (ms):", delta_seconds)  # Số mili giây
                print("Delta Time (ms):", delta_time)  # Kết quả dạng BIGINT

                delta_time_epoch = delta_time  # Lưu giá trị dạng BIGINT
                print("delta_time_epoch:", delta_time_epoch)  # In ra timestamp dưới dạng số nguyên
                last_id = "0"
                logging.info(f"Starting sync with delta time: {delta_time}.")

                with ThreadPoolExecutor(max_workers=self.thread_pool_size) as executor:
                    futures = []
                    while True:
                        # Schedule batch processing in parallel
                        future = executor.submit(
                            self.process_batch,
                            source_session,
                            target_session,
                            source_table,
                            target_table,
                            last_id,
                            delta_time_epoch,
                            # bot  # Truyền bot vào hàm process_batch
                        )
                        futures.append(future)

                        # Wait for any completed future
                        completed_futures = []
                        for completed_future in as_completed(futures):
                            try:
                                new_last_id = completed_future.result()
                                if not new_last_id:
                                    logging.info("No more data to process. Stopping sync.")
                                    # No more data to process
                                    for f in futures:
                                        f.cancel()
                                    return

                                # Update last_id with thread-safe lock
                                with self.lock:
                                    last_id = new_last_id

                            except Exception as e:
                                logging.error(f"Error in batch processing: {e}")
                            finally:
                                completed_futures.append(completed_future)

                        # Remove completed futures from the list
                        for completed_future in completed_futures:
                            futures.remove(completed_future)

                logging.info("Data synchronization completed.")
                return  # Thoát khỏi vòng lặp nếu đồng bộ thành công

            except OperationalError as e:
                logging.error(f"Lỗi kết nối: {e}. Thử lại sau 45 giây...")
                if self.bot:
                    self.bot.add_message(f"⚠️ Lỗi kết nối đến DB. Thử lại sau 45 giây...")
                source_session.rollback()
                target_session.rollback()
                retry_count += 1
                time.sleep(retry_interval)  # Chờ 45 giây rồi thử lại

            except Exception as e:
                logging.error(f"Error during synchronization: {e}")
                source_session.rollback()
                target_session.rollback()
                

        logging.error("Max retries reached. Synchronization failed.")
        if self.bot:
            self.bot.add_message("❌ Đã hết số lần thử lại, đồng bộ thất bại.")

    # Check if target table is empty
    def is_table_empty(self ,session: Session, table: Table) -> bool:
            result = session.execute(select(func.count()).select_from(table)).scalar()
            return result == 0

    # Main synchronization function
    async def sync_data(self, table_name: str, delta_days: int = 1) -> None:
        retry_count = int(os.getenv('RETRY_COUNT', 0))
        max_retries = int(os.getenv('MAX_RETRIES', 3))
        retry_interval = int(os.getenv('RETRY_INTERVAL', 30))

        while retry_count < max_retries:
            source_session = Session(bind=self.source_engine)
            target_session = Session(bind=self.target_engine)

            start_time = datetime.now()
            if self.bot:
                self.bot.add_message(f"🔄 Đồng bộ dữ liệu cho bảng `{table_name}` bắt đầu lúc {start_time.strftime('%Y-%m-%d %H:%M:%S')}.")

            try:
                logging.info("Starting data synchronization.")

                self.ensure_table_exists(Base, table_name)

                # Initialize MetaData
                source_metadata = MetaData()
                target_metadata = MetaData()

                # Bind engines to metadata
                source_metadata.bind = self.source_engine
                target_metadata.bind = self.target_engine

                source_table = Table(table_name, source_metadata, autoload_with=self.source_engine)
                target_table = Table(table_name, target_metadata, autoload_with=self.target_engine)

                total_records = 0
                if self.is_table_empty(target_session, target_table):
                    logging.info("Target table is empty. Transferring all data from source table.")
                    last_id = 0

                    while True:
                        batch_data = self.fetch_batch_data_all(source_session, source_table, last_id, self.batch_size)
                        if not batch_data:
                            break

                        # Lấy danh sách cột của bảng đích
                        target_columns = {col.name for col in target_table.columns}

                        # Chuyển đổi dữ liệu
                        transformed_data = [
                            {
                                col.name: (
                                    # Nếu giá trị là dict, chuyển đổi thành chuỗi JSON
                                    json.dumps(row._mapping[col.name])
                                    if col.name in row._mapping and isinstance(row._mapping[col.name], dict)
                                    else row._mapping[col.name]
                                    if col.name in row._mapping
                                    else None
                                )
                                for col in source_table.columns
                                if col.name in target_columns  # Chỉ lấy các cột có trong bảng đích
                            }
                            for row in batch_data
                        ]

                        self.insert_or_update_data(target_session, target_table, transformed_data)
                        total_records += len(batch_data)
                        last_row = batch_data[-1]  # Get the last row in the batch
                        last_id = str(last_row._mapping["id"])

                    logging.info("Initial data transfer completed.")
                else:
                    self.process_sync(source_session, target_session, source_table, target_table, delta_days, self.bot)

                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                if self.bot:
                    if total_records == 0:  # Nếu không có bản ghi mới
                        self.bot.add_message(f"✅ Không có bản ghi mới để đồng bộ cho bảng `{table_name}`.")
                    else:
                        self.bot.add_message(f"✅ Tổng cộng {total_records} bản ghi được đồng bộ cho bảng `{table_name}`.")
                    self.bot.add_message(f"✅ Đồng bộ bảng `{table_name}` hoàn thành lúc {end_time.strftime('%Y-%m-%d %H:%M:%S')} sau {duration:.2f} giây.")

                logging.info("Data synchronization completed successfully.")
                return  # Thoát khỏi vòng lặp nếu đồng bộ thành công

            except OperationalError as e:
                logging.error(f"Lỗi kết nối: {e}. Thử lại sau 30 giây...")
                if self.bot:
                    self.bot.add_message(f"⚠️ Lỗi kết nối đến DB. Thử lại sau 30 giây...")
                source_session.rollback()
                target_session.rollback()
                retry_count += 1
                await asyncio.sleep(retry_interval)  # Chờ 30 giây rồi thử lại

            except SQLAlchemyError as e:
                error_message = f"❌ Lỗi cơ sở dữ liệu: {e}"
                if self.bot:
                    self.bot.add_message(error_message)
                logging.error(f"Database error: {e}")
                source_session.rollback()
                target_session.rollback()

            except Exception as e:
                # Lấy traceback chi tiết
                error_traceback = traceback.format_exc()

                # Tạo thông báo lỗi
                error_message = f"❌ Lỗi nghiêm trọng trong quá trình đồng bộ bảng `{table_name}`: {e}\nTraceback:\n{error_traceback}"
                if self.bot:
                    self.bot.add_message(error_message)
                logging.error(f"Critical error: {e}\nTraceback:\n{error_traceback}")
                source_session.rollback()
                target_session.rollback()

            finally:
                source_session.close()
                target_session.close()
                logging.info("Database sessions closed.")
                if self.bot:
                    await self.bot.send_combined_message()

        logging.error("Max retries reached. Synchronization failed.")
        if self.bot:
            self.bot.add_message("❌ Đã hết số lần thử lại, đồng bộ thất bại.")

      
