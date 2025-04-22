"""
    Model chat: Thông tin chat
"""

from .base import Base
from sqlalchemy import BigInteger, Boolean, Column, String, Text, JSON, DOUBLE_PRECISION



class Chat(Base):
    """
        Chat class.
    """
    __tablename__ = "chat"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    title = Column(Text)
    chat = Column(JSON)

    created_at = Column(BigInteger)
    updated_at = Column(BigInteger, index=True)

    share_id = Column(Text, unique=True, nullable=True)
    archived = Column(Boolean, default=False)
    pinned = Column(Boolean, default=False, nullable=True)

    meta = Column(JSON, server_default="{}")
    folder_id = Column(Text, nullable=True)

    # Các cột chỉ có trong target_db
    result = Column(JSON, nullable=True)  # Lưu kết quả (JSON)
    total_result = Column(DOUBLE_PRECISION, nullable=True)  # Tổng kết quả
    total_messages = Column(BigInteger, nullable=True) # Tổng độ dài của chat

     # Thêm cột start_time và finish_time
    start_time = Column(BigInteger, nullable=True)  # Thời gian bắt đầu chat
    finish_time = Column(BigInteger, nullable=True)  # Thời gian kết thúc chat

    model = Column(Text, nullable=True)  # Model dự đoán chat
