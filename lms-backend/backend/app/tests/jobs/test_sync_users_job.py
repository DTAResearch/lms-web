# python -m unittest discover -s backend/app/tests/jobs -p "*.py"

import sys
import os

# Đường dẫn tới các module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
import unittest

from app.model.base import Base
from app.jobs.sync_job_management import DataSyncManager

from sqlalchemy import MetaData, Table, Column, String, BigInteger, Text, func, create_engine
from sqlalchemy.orm import sessionmaker

import time
import logging
from datetime import datetime

import asyncio

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestSyncUsersJob(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Connection URLs for both databases
        cls.source_engine = create_engine("sqlite:///test.db")  # SQLite connection
        cls.target_engine = create_engine("postgresql://postgres:ndc132@localhost:5432/test_db")  # PostgreSQL connection

        cls.source_metadata = MetaData()
        cls.target_metadata = MetaData()

        # Define the User table schema for both databases
        cls.user_table = Table(
            "user", cls.source_metadata,
            Column("id", String, primary_key=True),
            Column("name", String),
            Column("email", String),
            Column("role", String),
            Column("profile_image_url", Text),
            Column("last_active_at", BigInteger),
            Column("updated_at", BigInteger),
            Column("created_at", BigInteger),
            Column("api_key", String, unique=True),
            Column("settings", Text),
            Column("info", Text),
            Column("oauth_sub", Text, unique=True),
        )

        # Create tables in both engines
        cls.source_metadata.create_all(cls.source_engine)
        cls.target_metadata.create_all(cls.target_engine)

        cls.SourceSession = sessionmaker(bind=cls.source_engine)
        cls.TargetSession = sessionmaker(bind=cls.target_engine)

        cls.sync_manager = DataSyncManager(
             source_engine=cls.source_engine,
             target_engine=cls.target_engine,
             bot=None,
        )
    def setUp(self):
        # Initialize sessions for both source and target databases
        self.source_session = self.SourceSession()
        self.target_session = self.TargetSession()

    def tearDown(self):
        self.source_session.execute(self.user_table.delete())
        self.target_session.execute(self.user_table.delete())
        self.source_session.commit()
        self.target_session.commit()
        self.source_session.close()
        self.target_session.close()

    def insert_data_if_not_exists(self, session, table, data):
        """Inserts data into the table if the id does not already exist."""
        for entry in data:
            existing_entry = session.execute(
                table.select().where(table.c.id == entry["id"])
            ).fetchone()
            if not existing_entry:
                session.execute(table.insert().values(entry))
        session.commit()

    def test_empty_target_table(self):
        # Insert sample data into the source SQLite database
        now = int(datetime.now().timestamp())
        source_data = [
            {"id": "1", "name": "User1", "email": "user1@example.com", "role": "admin", 
             "profile_image_url": "http://example.com/old_user.png", "last_active_at": now, 
             "updated_at": now, "created_at": now, "api_key": "api_key_1", "settings": "{}", 
             "info": "User info 1", "oauth_sub": "oauth_sub_1"},
            {"id": "2", "name": "User2", "email": "user2@example.com", "role": "user", 
             "profile_image_url": "http://example.com/old_user.png", "last_active_at": now, 
             "updated_at": now, "created_at": now, "api_key": "api_key_2", "settings": "{}", 
             "info": "User info 2", "oauth_sub": "oauth_sub_2"},
        ]
        self.insert_data_if_not_exists(self.source_session, self.user_table, source_data)

        target_data_count_before = self.target_session.execute(
            func.count().select().select_from(self.user_table)
        ).scalar()
        logger.info(f"Số lượng người dùng trước khi đồng bộ: {target_data_count_before}")

         # Run the sync function to sync data from SQLite to PostgreSQL
        asyncio.run(self.sync_manager.sync_data("user", delta_days=1))

        # Query the target PostgreSQL database to check if data was synced
        target_data = self.target_session.execute(self.user_table.select()).fetchall()

        # Assert that the target data was correctly inserted
        self.assertEqual(target_data[0][2], "user1@example.com")  # Email of the first user
        self.assertEqual(target_data[1][2], "user2@example.com")  # Email of the second user

    def test_update_existing_data(self):
        # Insert data into both databases
        now = int(datetime.now().timestamp())
        old_timestamp = now - 10000
        source_data = [
            {"id": "1", "name": "Updated User", "email": "user1@example.com", "role": "admin", 
             "profile_image_url": "http://example.com/old_user.png", "last_active_at": now, 
             "updated_at": now, "created_at": old_timestamp, "api_key": "updated_api_key_1", 
             "settings": "{}", "info": "Updated User info", "oauth_sub": "updated_oauth_sub_1"}
        ]
        self.insert_data_if_not_exists(self.source_session, self.user_table, source_data)

        target_data = [
            {"id": "1", "name": "Old User", "email": "user1@example.com", "role": "admin", 
             "profile_image_url": "http://example.com/old_user.png", "last_active_at": old_timestamp, 
             "updated_at": old_timestamp, "created_at": old_timestamp, "api_key": "old_api_key", 
             "settings": "{}", "info": "Old User info", "oauth_sub": "old_oauth_sub_1"}
        ]
        self.insert_data_if_not_exists(self.target_session, self.user_table, target_data)

        # Run the sync function to sync data from SQLite to PostgreSQL
        asyncio.run(self.sync_manager.sync_data("user", delta_days=1))

        target_data = self.target_session.execute(self.user_table.select()).fetchall()
        self.assertEqual(target_data[0][1], "Updated User")  # Sử dụng index thay vì ["name"]
        self.assertEqual(target_data[0][8], "updated_api_key_1")  # Index của `api_key`

    def test_no_changes_needed(self):
        # Insert identical data into both databases
        now = int(datetime.now().timestamp())
        source_data = [
            {"id": "1", "name": "User", "email": "user@example.com", "role": "user", 
             "profile_image_url": "http://example.com/old_user.png", "last_active_at": now, 
             "updated_at": now, "created_at": now, "api_key": "api_key_1", "settings": "{}", 
             "info": "User info", "oauth_sub": "oauth_sub_1"}
        ]
        self.insert_data_if_not_exists(self.source_session, self.user_table, source_data)

        target_data = [
            {"id": "1", "name": "User", "email": "user@example.com", "role": "user", 
             "profile_image_url": "http://example.com/old_user.png", "last_active_at": now, 
             "updated_at": now, "created_at": now, "api_key": "api_key_1", "settings": "{}", 
             "info": "User info", "oauth_sub": "oauth_sub_1"}
        ]
        self.insert_data_if_not_exists(self.target_session, self.user_table, target_data)

        # Run the sync function and ensure no changes are made
         # Run the sync function to sync data from SQLite to PostgreSQL
        asyncio.run(self.sync_manager.sync_data("user", delta_days=1))

        # Assert that no changes were made in the target database
        target_data = self.target_session.execute(self.user_table.select()).mappings().all()

        self.assertEqual(len(target_data), 1)
        self.assertEqual(target_data[0]["name"], "User")
        self.assertEqual(target_data[0]["api_key"], "api_key_1")  # Ensure API key remains unchanged

    def test_empty_source_table(self):
            # Bảng nguồn trống bảng đích không thay đổi
            now = int(datetime.now().timestamp())
            target_data = [
                {"id": "1", "name": "User1", "email": "user1@example.com", "role": "admin",
                "profile_image_url": "http://example.com/user1.png", "last_active_at": now,
                "updated_at": now, "created_at": now, "api_key": "api_key_1", "settings": "{}",
                "info": "User info 1", "oauth_sub": "oauth_sub_1"}
            ]       
            self.insert_data_if_not_exists(self.target_session, self.user_table, target_data)

             # Run the sync function to sync data from SQLite to PostgreSQL
            asyncio.run(self.sync_manager.sync_data("user", delta_days=1))

            # Kiểm tra bảng đích không thay đổi
            target_data = self.target_session.execute(self.user_table.select()).mappings().all()
            self.assertEqual(len(target_data), 1)
            self.assertEqual(target_data[0]["name"], "User1")
    def test_new_data_in_source(self):
    # Bảng nguồn có dữ liệu mới, bảng đích cần được thêm
        now = int(datetime.now().timestamp())
        source_data = [
            {"id": "3", "name": "New User", "email": "new_user@example.com", "role": "user",
            "profile_image_url": "http://example.com/new_user.png", "last_active_at": now,
            "updated_at": now, "created_at": now, "api_key": "api_key_3", "settings": "{}",
            "info": "New User info", "oauth_sub": "oauth_sub_3"}
        ]
        self.insert_data_if_not_exists(self.source_session, self.user_table, source_data)

         # Run the sync function to sync data from SQLite to PostgreSQL
        asyncio.run(self.sync_manager.sync_data("user", delta_days=1))

        # Kiểm tra dữ liệu mới đã được thêm vào bảng đích
        target_data = self.target_session.execute(self.user_table.select()).mappings().all()
        self.assertEqual(len(target_data), 1)
        self.assertEqual(target_data[0]["name"], "New User")

    def test_conflict_primary_key(self):
        # Dữ liệu với khóa chính trùng lặp trong bảng nguồn và bảng đích
        now = int(datetime.now().timestamp())
        source_data = [
            {"id": "1", "name": "Conflicting User", "email": "conflict@example.com", "role": "admin",
            "profile_image_url": "http://example.com/conflict.png", "last_active_at": now,
            "updated_at": now, "created_at": now, "api_key": "conflict_api_key", "settings": "{}",
            "info": "Conflict User info", "oauth_sub": "conflict_oauth_sub"}
        ]
        self.insert_data_if_not_exists(self.source_session, self.user_table, source_data)

        target_data = [
            {"id": "1", "name": "Original User", "email": "original@example.com", "role": "admin",
            "profile_image_url": "http://example.com/original.png", "last_active_at": now,
            "updated_at": now, "created_at": now, "api_key": "original_api_key", "settings": "{}",
            "info": "Original User info", "oauth_sub": "original_oauth_sub"}
        ]
        self.insert_data_if_not_exists(self.target_session, self.user_table, target_data)

        # Đồng bộ dữ liệu
         # Run the sync function to sync data from SQLite to PostgreSQL
        asyncio.run(self.sync_manager.sync_data("user", delta_days=1))

        # Kiểm tra dữ liệu bảng đích đã được cập nhật
        target_data = self.target_session.execute(self.user_table.select()).mappings().all()
        self.assertEqual(len(target_data), 1)
        self.assertEqual(target_data[0]["name"], "Conflicting User")

    def test_multiple_updates(self):
        # Cập nhật nhiều bản ghi cùng lúc
        now = int(datetime.now().timestamp())
        source_data = [
            {"id": "1", "name": "Updated User1", "email": "user1@example.com", "role": "admin",
            "profile_image_url": "http://example.com/updated_user1.png", "last_active_at": now,
            "updated_at": now, "created_at": now, "api_key": "updated_api_key_1", "settings": "{}",
            "info": "Updated User info 1", "oauth_sub": "updated_oauth_sub_1"},
            {"id": "2", "name": "Updated User2", "email": "user2@example.com", "role": "user",
            "profile_image_url": "http://example.com/updated_user2.png", "last_active_at": now,
            "updated_at": now, "created_at": now, "api_key": "updated_api_key_2", "settings": "{}",
            "info": "Updated User info 2", "oauth_sub": "updated_oauth_sub_2"}
        ]
        self.insert_data_if_not_exists(self.source_session, self.user_table, source_data)

         # Run the sync function to sync data from SQLite to PostgreSQL
        asyncio.run(self.sync_manager.sync_data("user", delta_days=1))

        # Kiểm tra bảng đích
        target_data = self.target_session.execute(self.user_table.select()).mappings().all()
        self.assertEqual(len(target_data), 2)
        self.assertEqual(target_data[0]["name"], "Updated User1")
        self.assertEqual(target_data[1]["name"], "Updated User2")

    def test_large_scale_sync(self):
            # Số lượng người dùng cần đồng bộ
            num_users = 10

            # Tạo dữ liệu giả trong cơ sở dữ liệu nguồn
            now = int(datetime.now().timestamp())
            source_data = [
                {
                    "id": str(i),
                    "name": f"User{i}",
                    "email": f"user{i}@example.com",
                    "role": "user" if i % 2 == 0 else "admin",
                    "profile_image_url": f"http://example.com/user{i}.png",
                    "last_active_at": now - (i % 1000),
                    "updated_at": now - (1000000),# trừ khoảng 1 ngàyngày
                    "created_at": now - (i % 10000),
                    "api_key": f"api_key_{i}",
                    "settings": "{}",
                    "info": f"User info {i}",
                    "oauth_sub": f"oauth_sub_{i}"
                }
                for i in range(1, num_users + 1)
            ]
            logger.info("Hoàn thành tạo dữ liệu giả. Số lượng người dùng: %d", num_users)
             # Thời gian thêm dữ liệu vào source_db
            logger.info("Bắt đầu thêm dữ liệu vào cơ sở dữ liệu nguồn.")
            start_insert_time = time.time()
            logger.info("Chèn dữ liệu vào cơ sở dữ liệu nguồn nếu chưa tồn tại.")
            self.insert_data_if_not_exists(self.source_session, self.user_table, source_data)
            end_insert_time = time.time()
            logger.info("Hoàn thành chèn dữ liệu vào cơ sở dữ liệu nguồn.")
            logger.info("Thời gian thêm dữ liệu vào cơ sở dữ liệu nguồn: %.2f giây", end_insert_time - start_insert_time)

            
            # Thực hiện đồng bộ hóa
            logger.info("Bắt đầu đồng bộ hóa dữ liệu người dùng.")
            start_time = time.time()
             # Run the sync function to sync data from SQLite to PostgreSQL
            asyncio.run(self.sync_manager.sync_data("user", delta_days=1))
            end_time = time.time()
            logger.info("Hoàn thành đồng bộ hóa dữ liệu người dùng.")
            # Truy vấn cơ sở dữ liệu đích để kiểm tra kết quả
            logger.info("Kiểm tra số lượng dữ liệu trong cơ sở dữ liệu đích.")
            target_data_count = self.target_session.execute(
                func.count().select().select_from(self.user_table)
            ).scalar()
            logger.info(f"Số lượng người dùng sau đồng bộ: {target_data_count}")

            logger.info("So sánh số lượng dữ liệu đồng bộ với số lượng người dùng ban đầu.")
            self.assertEqual(target_data_count, num_users)

            # In ra thời gian thực hiện để kiểm tra hiệu suất
            logger.info("Thời gian thực hiện để đồng bộ %d người dùng: %.2f giây", num_users, end_time - start_time)

if __name__ == "__main__":
    unittest.main()