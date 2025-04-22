"""
    User model: Thông tin người dùng
"""

from sqlalchemy import BigInteger, Column, String, Text
from .base import Base
from app.db.custom_types.json_field import JSONField

class User(Base):
    """
        User class
    """
    __tablename__ = "user"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    role = Column(String)
    profile_image_url = Column(Text)

    last_active_at = Column(BigInteger)
    updated_at = Column(BigInteger, index=True)
    created_at = Column(BigInteger)

    api_key = Column(String, nullable=True, unique=True)
    settings = Column(JSONField, nullable=True)
    info = Column(JSONField, nullable=True)

    oauth_sub = Column(Text, unique=True)
