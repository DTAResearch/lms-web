"""
Model model: Thông tin các mô hình
"""

from sqlalchemy import BigInteger, Column, String, Boolean, ForeignKey  # type: ignore
from .base import Base
from app.db.custom_types.json_field import JSONField


class Model(Base):
    """
    Model class
    """

    __tablename__ = "model"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    base_model_id = Column(String, nullable=True)
    name = Column(String, nullable=False)
    meta = Column(JSONField, nullable=True)
    params = Column(JSONField, nullable=True)
    created_at = Column(BigInteger, nullable=False)
    updated_at = Column(BigInteger, nullable=False)
    access_control = Column(JSONField, nullable=True)
    is_active = Column(Boolean, nullable=False)
    default_limit = Column(JSONField, nullable=True)
    department_id = Column(String, ForeignKey("department.id"), nullable=True)
