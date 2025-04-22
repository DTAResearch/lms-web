from datetime import datetime
import logging
from sqlalchemy.orm import Session  # type: ignore
from fastapi.encoders import jsonable_encoder  # type: ignore
import httpx  # type: ignore
from app.model.user import User
from app.constants.roles import Role  # Thêm import này để kiểm tra role hợp lệ
from app.core.config import settings


class HandleUser:

    def __init__(self):
        """Initialize the handle group"""
        self.token = settings.HOC_TIEP_KEY
        self.retries = settings.MAX_RETRIES
        self.hoc_tiep_be_url = settings.HOC_TIEP_BE_URL

    def __get_headers(self):
        """Get the headers"""
        return {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json",
        }

    @staticmethod
    def __format_datetime(timestamp: int):
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%d/%m/%Y")

    async def get_users_page(
        self,
        page: int,
        limit: int,
        query: str,
        
        target_db: Session,
        role: str = None,  # Thêm tham số role
    ):
        offset = (page - 1) * limit
        db_query = target_db.query(User)

        # Lọc theo role nếu được cung cấp
        if role:
            if role not in [Role.STUDENT.value, Role.TEACHER.value, Role.ADMIN.value]:
                raise ValueError("Invalid role")
            db_query = db_query.filter(User.role == role)

         # Lọc theo query tìm kiếm (email hoặc tên)
        if query:
            search_form = f"%{query}%"
            db_query = db_query.filter(
                User.email.ilike(search_form) | User.name.ilike(search_form)
            )

        total = db_query.count()
        users = db_query.offset(offset).limit(limit).all()
        users_list = [
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "role": u.role,
                "avatar": u.profile_image_url,
                "created_at": self.__format_datetime(u.created_at),
            }
            for u in users
        ]

        return {"users": users_list, "total": total}

    async def get_all_users(
        self,
        target_db: Session,
        role: str = None,  # Thêm tham số role
    ):
        db_query = target_db.query(User)
        if role:
            if role not in [Role.STUDENT.value, Role.TEACHER.value, Role.ADMIN.value]:
                raise ValueError("Invalid role")
            db_query = db_query.filter(User.role == role)

        users = db_query.all()
        users_list = [
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
            }
            for u in users
        ]
        return users_list

    async def sync_role(self, user_id: str, role: str):
        headers = self.__get_headers()
        url = self.hoc_tiep_be_url + "/api/v1/users/update/role"

        payload = {"id": user_id, "role": role}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json=payload, headers=headers, timeout=100
                )
                response.raise_for_status()

                return response.json()
        except httpx.HTTPStatusError as http_err:
            logging.error(
                "HTTP Error: "
                + str(http_err.response.status_code)
                + "-"
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: " + str(e))
