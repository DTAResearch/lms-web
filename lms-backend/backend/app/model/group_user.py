"""
    Group User model: Thông tin nhóm học với người dùng
"""

from sqlalchemy import BigInteger, Column, String, Boolean, ForeignKey  # type: ignore
from sqlalchemy.sql import func  # type: ignore
from sqlalchemy.dialects.postgresql import UUID  # type: ignore
from .base import Base


class GroupUser(Base):
    """
    Group User class
    """

    __tablename__ = "group_user"

    user_id = Column(
        String, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True, primary_key=True
    )
    group_id = Column(
        String, ForeignKey("group.id", ondelete="CASCADE"), nullable=False, index=True, primary_key=True
    )

    updated_at = Column(BigInteger, default=func.now(), nullable=False)
    created_at = Column(BigInteger, default=func.now(), nullable=False)
