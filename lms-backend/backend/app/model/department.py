"""
Department model: Thông tin các phòng ban
"""

from sqlalchemy import BigInteger, Column, String, ForeignKey  # type: ignore
from .base import Base


class Department(Base):
    """
    Model class
    """

    __tablename__ = "department"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    faculty_id = Column(
        String, ForeignKey("faculty.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(BigInteger, nullable=False)
    updated_at = Column(BigInteger, nullable=False)

    def get_detail(self):
        """Lấy đối tượng JSON"""
        return {
            "id": self.id,
            "name": self.name,
            "faculty_id": self.faculty_id,
            "updated_at": self.updated_at,
            "created_at": self.created_at,
        }
