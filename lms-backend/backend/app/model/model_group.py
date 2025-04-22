"""
    Model Group model: Thông tin nhóm học với người dùng
"""

from sqlalchemy import BigInteger, Column, String, Boolean, ForeignKey  # type: ignore
from sqlalchemy.sql import func  # type: ignore
from .base import Base


class ModelGroup(Base):
    """
    Group User class
    """

    __tablename__ = "model_group"

    model_id = Column(
        String, ForeignKey("model.id", ondelete="CASCADE"), nullable=False, index=True, primary_key=True
    )
    group_id = Column(
        String, ForeignKey("group.id", ondelete="CASCADE"), nullable=False, index=True, primary_key=True
    )
    can_write = Column(Boolean)

    updated_at = Column(BigInteger, default=func.now(), nullable=False)
    created_at = Column(BigInteger, default=func.now(), nullable=False)
