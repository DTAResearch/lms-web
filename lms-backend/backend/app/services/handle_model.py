"""Model Service"""

import logging
import json
from datetime import datetime
import asyncio
from app.core.config import settings
from app.schema.model import RequestCreateModel, RequestUpdateModel
from app.model.model import Model
from app.model.user import User
from app.model.model_group import ModelGroup
from app.model.group_user import GroupUser
from app.model.department import Department
from app.model.faculty import Faculty
from app.constants.roles import Role
from typing import List, Optional
import httpx  # type: ignore
from fastapi import HTTPException  # type: ignore
from sqlalchemy import not_, and_, or_, select  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy.sql import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from sqlalchemy.exc import SQLAlchemyError  # type: ignore
from aiocache import cached  # type: ignore


class HandleModel:

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

    async def get_all_models(self):
        headers = self.__get_headers()
        url = self.hoc_tiep_be_url + "/api/v1/models/"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=100)
                response.raise_for_status()
                models = response.json()
                return models
        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: " + str(e))

    async def get_all_private_models_info(self, target_db: AsyncSession):
        try:
            models_query = select(Model.id, Model.name).where(
                and_(
                    ~(Model.id.startswith("@")),
                    (Model.access_control.isnot(None)),
                    (Model.is_active.is_(True)),
                )
            )
            models_result = await target_db.execute(models_query)
            models = models_result.fetchall()
            models_list = [
                {
                    "id": model[0],
                    "name": model[1],
                }
                for model in models
            ]
            return models_list
        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: " + str(e))

    async def get_all_models_info(
        self, target_db: AsyncSession, user_id: str, user_role: str
    ):
        try:
            if user_role == Role.ADMIN.value:  # admin
                models_query = (
                    select(
                        Model.id,
                        Model.name,
                        Model.meta,
                        User.name.label("user_name"),
                        Model.is_active,
                        Model.department_id.label("department_id"),
                        Department.name.label("department_name"),
                        Faculty.name.label("faculty_name"),
                        Model.created_at,
                    )
                    .where(~Model.id.startswith("@"))
                    .join(User, Model.user_id == User.id)
                    .outerjoin(Department, Model.department_id == Department.id)
                    .outerjoin(Faculty, Department.faculty_id == Faculty.id)
                    .order_by(Model.created_at.desc())
                )
            else:  # student
                group_query = select(GroupUser.group_id).where(
                    GroupUser.user_id == user_id
                )
                group_ids = [
                    row[0] async for row in await target_db.stream(group_query)
                ]
                models_query = (
                    select(
                        Model.id,
                        Model.name,
                        Model.meta,
                        User.name.label("user_name"),
                        Model.is_active,
                        Model.department_id,
                        Department.name.label("department_name"),
                        Faculty.name.label("faculty_name"),
                        Model.created_at,
                    )
                    .join(User, Model.user_id == User.id)
                    .outerjoin(ModelGroup, Model.id == ModelGroup.model_id)
                    .outerjoin(Department, Model.department_id == Department.id)
                    .outerjoin(Faculty, Department.faculty_id == Faculty.id)
                    .filter(
                        and_(
                            ~Model.id.startswith("@"),
                            Model.is_active.is_(True),
                            or_(
                                Model.access_control.is_(None),
                                ModelGroup.group_id.in_(group_ids),
                            ),
                        )
                    )
                    .order_by(Model.created_at.desc())
                    .distinct()
                )
            result = await target_db.execute(models_query)
            models = result.fetchall()
            models_list = [
                {
                    "id": model[0],
                    "title": model[1],
                    "description": model[2].get("description", ""),
                    "image_url": model[2].get("profile_image_url", ""),
                    "author": model[3],
                    "is_active": model[4],
                    "department_id": model[5],
                    "department_name": model[6],
                    "faculty_name": model[7],
                }
                for model in models
            ]
            return models_list
        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: " + str(e))

    @cached(ttl=86400)
    async def get_base_model_id(self, model_id: str):
        headers = self.__get_headers()
        url = self.hoc_tiep_be_url + "/api/v1/models/model?id=" + model_id
        params = {"id": model_id}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=100,
                )
                if response.status_code != 200:
                    return "gpt-4o"
                base_model = response.json()["base_model_id"]
                return base_model
        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: " + str(e))

    async def get_models_for_group(self, target_db: AsyncSession, group_id: str):
        result = await target_db.execute(
            select(ModelGroup.model_id, ModelGroup.can_write).where(
                ModelGroup.group_id == group_id
            )
        )
        access_controls = result.fetchall()
        read_rs = []
        write_rs = []
        if not access_controls:
            return {"read": [], "write": []}
        for access_control in access_controls:
            read_rs.append(access_control.model_id)
            if access_control.can_write:
                write_rs.append(access_control.model_id)
        return {
            "read": read_rs,
            "write": write_rs,
        }

    async def delete_model_group_target_db(
        self, target_db: AsyncSession, model_id: str, group_id: str
    ):
        try:
            delete_stmt = text(
                """
                DELETE FROM model_group
                WHERE model_id = :model_id AND group_id = :group_id
            """
            )

            await target_db.execute(
                delete_stmt, {"model_id": model_id, "group_id": group_id}
            )

            await target_db.commit()
        except SQLAlchemyError as e:
            raise e
        except Exception as e:
            raise e

    async def create_model_group_target_db(
        self, target_db: AsyncSession, model_id: str, group_id: str, can_write: bool
    ):
        try:
            insert_stmt = text(
                """
                INSERT INTO model_group (model_id, group_id, can_write, created_at, updated_at)
                VALUES (:model_id, :group_id, :can_write, :created_at, :updated_at)
            """
            )

            await target_db.execute(
                insert_stmt,
                {
                    "model_id": model_id,
                    "group_id": group_id,
                    "can_write": can_write,
                    "created_at": int(datetime.now().timestamp()),
                    "updated_at": int(datetime.now().timestamp()),
                },
            )

            await target_db.commit()
        except Exception as e:
            raise e

    async def update_model_group_target_db(
        self, target_db: AsyncSession, model_id: str, group_id: str, can_write: bool
    ):
        try:
            update_stmt = text(
                """
                UPDATE model_group
                SET
                    can_write = :can_write,
                    updated_at = :updated_at
                WHERE model_id = :model_id AND group_id = :group_id
            """
            )

            await target_db.execute(
                update_stmt,
                {
                    "model_id": model_id,
                    "group_id": group_id,
                    "can_write": can_write,
                    "updated_at": int(datetime.now().timestamp()),
                },
            )

            await target_db.commit()
        except Exception as e:
            raise e

    async def create_model_target_db(self, target_db: AsyncSession, model: dict):
        new_model = {
            "id": model.get("id"),
            "user_id": model.get("user_id"),
            "base_model_id": model.get("base_model_id"),
            "name": model.get("name"),
            "meta": model.get("meta", {}),
            "params": model.get("params", {}),
            "access_control": model.get("access_control"),
            "is_active": model.get("is_active", True),
            "created_at": datetime.now().timestamp(),
            "updated_at": datetime.now().timestamp(),
        }
        try:
            insert_stmt = text(
                """
                INSERT INTO "model" (
                    id,
                    user_id,
                    base_model_id,
                    name,
                    meta,
                    params,
                    access_control,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES (
                    :id,
                    :user_id,
                    :base_model_id,
                    :name,
                    :meta,
                    :params,
                    :access_control,
                    :is_active,
                    :created_at,
                    :updated_at
                )
                """
            )

            await target_db.execute(
                insert_stmt,
                {
                    "id": new_model["id"],
                    "user_id": new_model["user_id"],
                    "base_model_id": new_model["base_model_id"],
                    "name": new_model["name"],
                    "meta": json.dumps(new_model["meta"]),
                    "params": json.dumps(new_model["params"]),
                    "access_control": (
                        json.dumps(new_model["access_control"])
                        if new_model["access_control"]
                        else None
                    ),
                    "is_active": new_model["is_active"],
                    "created_at": new_model["created_at"],
                    "updated_at": new_model["updated_at"],
                },
            )

            await target_db.commit()
            if new_model["access_control"] is None:
                return
            read_group_access = new_model["access_control"].get("read").get("group_ids")
            write_group_access = (
                new_model["access_control"].get("write").get("group_ids")
            )
            read_only_group = list(set(read_group_access) - set(write_group_access))
            tasks = [
                self.create_model_group_target_db(
                    target_db=target_db,
                    model_id=new_model["id"],
                    group_id=group_id,
                    can_write=(group_id in write_group_access),
                )
                for group_id in (read_only_group) + (write_group_access)
            ]
            await asyncio.gather(*tasks)
        except Exception as e:
            raise e

    async def update_access_control(
        self, target_db: AsyncSession, model_id: str, access_control: dict
    ):
        try:
            result = await target_db.execute(
                text(
                    "SELECT group_id, can_write FROM model_group WHERE model_id = :model_id"
                ),
                {"model_id": model_id},
            )
            old_groups_access = [r for r in result.fetchall()]
            old_read_group_access = [
                group_access[0] for group_access in old_groups_access
            ]

            old_write_group_access = [
                group_access[0]
                for group_access in old_groups_access
                if group_access[1] == True
            ]
            if access_control is None:
                await target_db.execute(
                    text("DELETE FROM model_group WHERE model_id = :model_id"),
                    {"model_id": model_id},
                )
            else:
                read_group_access = access_control.get("read", {}).get("group_ids", [])
                write_group_access = access_control.get("write", {}).get(
                    "group_ids", []
                )

                added_read_access = set(read_group_access) - set(old_read_group_access)
                added_write_access = set(write_group_access) - set(
                    old_write_group_access
                )

                removed_read_access = set(old_read_group_access) - set(
                    read_group_access
                )
                removed_write_access = set(old_write_group_access) - set(
                    write_group_access
                )

                added_read_only_group = set(added_read_access) - set(added_write_access)
                write_to_read_access = set(removed_write_access) - set(
                    removed_read_access
                )
                read_to_write_access = set(added_write_access) - set(added_read_access)
                tasks = [
                    self.create_model_group_target_db(
                        target_db=target_db,
                        model_id=model_id,
                        group_id=group_id,
                        can_write=(group_id in added_write_access),
                    )
                    for group_id in set(added_read_only_group | added_write_access)
                    - set(read_to_write_access)
                ]

                tasks.extend(
                    [
                        self.update_model_group_target_db(
                            target_db=target_db,
                            model_id=model_id,
                            group_id=group_id,
                            can_write=(group_id in read_to_write_access),
                        )
                        for group_id in write_to_read_access | read_to_write_access
                    ]
                )

                tasks.extend(
                    [
                        self.delete_model_group_target_db(
                            target_db=target_db,
                            model_id=model_id,
                            group_id=group_id,
                        )
                        for group_id in removed_read_access
                    ]
                )
                await asyncio.gather(*tasks)
            await target_db.commit()
        except Exception as e:
            raise e

    async def update_model_target_db(
        self, target_db: AsyncSession, updated_model: dict
    ):
        updated_model_data = {
            "id": updated_model.get("id"),
            "base_model_id": updated_model.get("base_model_id"),
            "name": updated_model.get("name"),
            "meta": updated_model.get("meta"),
            "params": updated_model.get("params"),
            "access_control": updated_model.get("access_control"),
            "is_active": updated_model.get("is_active"),
            "updated_at": datetime.now().timestamp(),
        }

        try:
            update_stmt = text(
                """
                UPDATE "model"
                SET
                    base_model_id = :base_model_id,
                    name = :name,
                    meta = :meta,
                    params = :params,
                    access_control = :access_control,
                    is_active = :is_active,
                    updated_at = :updated_at
                WHERE id = :id
                """
            )

            await target_db.execute(
                update_stmt,
                {
                    "id": updated_model_data["id"],
                    "base_model_id": updated_model_data["base_model_id"],
                    "name": updated_model_data["name"],
                    "meta": json.dumps(updated_model_data["meta"]),
                    "params": json.dumps(updated_model_data["params"]),
                    "access_control": json.dumps(updated_model_data["access_control"]),
                    "is_active": updated_model_data["is_active"],
                    "updated_at": updated_model_data["updated_at"],
                },
            )

            await target_db.commit()
            await self.update_access_control(
                target_db=target_db,
                model_id=updated_model_data["id"],
                access_control=updated_model_data["access_control"],
                
            )
        except Exception as e:
            raise e

    async def delete_model_target_db(self, target_db: AsyncSession, model_id: str):
        try:
            delete_model_group_stmt = text(
                """
                DELETE FROM model_group
                WHERE model_id = :model_id
                """
            )
            await target_db.execute(delete_model_group_stmt, {"model_id": model_id})

            delete_model_stmt = text(
                """
                DELETE FROM model
                WHERE id = :model_id
                """
            )
            await target_db.execute(delete_model_stmt, {"model_id": model_id})

            await target_db.commit()

        except Exception as e:
            raise e

    async def create_model(self, target_db: AsyncSession, payload: RequestCreateModel):
        model_id = payload.id
        model_name = payload.name
        if not model_id or not model_name:
            raise HTTPException(
                status_code=400, detail="Model ID and name are required."
            )
        try:
            model_query = select(Model.id, Model.name).where(
                or_(Model.id == model_id, Model.name == model_name)
            )
            result = await target_db.execute(model_query)
            existing_model = result.fetchone()
            if existing_model:
                if existing_model[0] == model_id:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Môn học với ID '{model_id}' đã tồn tại.",
                    )
                raise HTTPException(
                    status_code=400,
                    detail=f"Môn học với tên '{model_name}' đã tồn tại.",
                )

            headers = self.__get_headers()
            url = self.hoc_tiep_be_url + "/api/v1/models/create"
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json=payload.dict(), headers=headers, timeout=100
                )
                response.raise_for_status()
                if response.status_code != 200:
                    raise HTTPException(status_code=400, detail=str(response.text))
                model = response.json()
                await self.create_model_target_db(model=model, target_db=target_db)
                return model
        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: " + str(e))

    async def update_model(
        self, target_db: AsyncSession, model_id: str, payload: RequestUpdateModel
    ):
        headers = self.__get_headers()
        url = self.hoc_tiep_be_url + "/api/v1/models/model/update?id=" + model_id
        update_data = {
            **(payload.dict() if hasattr(payload, "dict") else payload),
            "updated_at": int(datetime.now().timestamp()),
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json=update_data, headers=headers, timeout=100
                )
                response.raise_for_status()
                if response.status_code != 200:
                    raise HTTPException(status_code=400, detail=str(response.text))
                updated_model = response.json()
                await self.update_model_target_db(target_db, updated_model)
                return updated_model
        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: " + str(e))

    async def delete_model(self, model_id: str, target_db: AsyncSession):
        headers = self.__get_headers()
        url = self.hoc_tiep_be_url + "/api/v1/models/model/delete?id=" + model_id

        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(url, headers=headers, timeout=100)
                response.raise_for_status()
                result = response.json()
                if response.status_code != 200:
                    raise HTTPException(status_code=400, detail=str(response.text))
                await self.delete_model_target_db(
                    target_db=target_db, model_id=model_id
                )
                return result
        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: " + str(e))

    async def get_all_base_models(self):
        models = await self.get_all_models()
        base_models = list(
            {model["base_model_id"] for model in models if model["is_active"]}
        )
        return base_models

    async def toggle_status(self, model_id: str, target_db: AsyncSession):
        headers = self.__get_headers()
        url = self.hoc_tiep_be_url + "/api/v1/models/model/toggle?id=" + model_id
        payload = {"id": model_id}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json=payload, headers=headers, timeout=100
                )
                response.raise_for_status()
                if response.status_code != 200:
                    raise HTTPException(status_code=400, detail=str(response.text))
                updated_model = response.json()
                await self.update_model_target_db(target_db, updated_model)
                return updated_model
        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: " + str(e))

    async def get_model_by_id(self, model_id: str, target_db: AsyncSession):

        try:
            model_query = select(
                Model.id,
                Model.name,
                Model.base_model_id,
                Model.meta,
                Model.params,
                Model.access_control,
            ).where((Model.id == model_id))
            model_result = await target_db.execute(model_query)
            existing_model = model_result.fetchone()
            if not existing_model:
                raise HTTPException(
                    status_code=404, detail="Model id: " + model_id + " not found!"
                )

            return {
                "model_id": existing_model.id,
                "name": existing_model.name,
                "base_model_id": existing_model.base_model_id,
                "description": (
                    existing_model.meta.get("description", "")
                    if existing_model.meta
                    else ""
                ),
                "system_prompt": (
                    existing_model.params.get("system", "")
                    if existing_model.params
                    else ""
                ),
                "access_control": existing_model.access_control,
                "capabilities": (
                    existing_model.meta.get("capabilities", "")
                    if existing_model.meta
                    else None
                ),
                "knowledge": (
                    existing_model.meta.get("knowledge", [])
                    if existing_model.meta
                    else None
                ),
            }
        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: " + str(e))
            raise
