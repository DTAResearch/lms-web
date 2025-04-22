"""
RateLimitFilter model: Thông tin các các giới hạn
"""

from sqlalchemy import BigInteger, Column, String, Integer  # type: ignore
from .base import Base


class RateLimitFilter(Base):
    """
    RateLimitFilter class
    """

    __tablename__ = "rate_limit_filter"

    group_id = Column(String, nullable=False, index=True, primary_key=True)
    model_id = Column(String, nullable=False, index=True, primary_key=True)
    token_limit = Column(BigInteger, nullable=True)
    request_limit = Column(Integer, nullable=False)
    created_at = Column(BigInteger, nullable=False)
    updated_at = Column(BigInteger, nullable=False)
    reset_hours_value = Column(Integer, nullable=True, server_default='24')
