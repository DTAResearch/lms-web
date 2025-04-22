"""
Group model: Thông tin nhóm học
"""

from sqlalchemy import BigInteger, Column, String, Text, JSON  # type: ignore
from .base import Base


class Group(Base):
    """
    Group class
    """

    __tablename__ = "group"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    name = Column(String)
    description = Column(Text)

    data = Column(JSON, nullable=True)
    meta = Column(JSON, nullable=True)
    permissions = Column(JSON, nullable=True)
    user_ids = Column(JSON, nullable=True)

    updated_at = Column(BigInteger, index=True)
    created_at = Column(BigInteger)

    def get_detail(self):
        """Lấy đối tượng JSON"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "data": self.data,
            "meta": self.meta,
            "permissions": self.permissions,
            "user_ids": self.user_ids,
            "updated_at": self.updated_at,
            "created_at": self.created_at,
        }
