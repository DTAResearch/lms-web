"""
Faculty model: Thông tin các mô hình
"""

from sqlalchemy import BigInteger, Column, String, ForeignKey  # type: ignore
from .base import Base


class Faculty(Base):
    """
    Faculty class
    """

    __tablename__ = "faculty"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(BigInteger, nullable=False)
    updated_at = Column(BigInteger, nullable=False)

    def get_detail(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
