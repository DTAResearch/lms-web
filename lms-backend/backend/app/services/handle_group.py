"""Hanel Group class"""

import asyncio
import logging
import json
import uuid
from datetime import datetime
from typing import List
from app.core.config import settings
from app.schema.group import (
    RequestCreateGroup,
    RequestUpdateModelsGroup,
)
from app.services.handle_model import HandleModel
from app.model.group import Group
from app.model.user import User
from app.model.model import Model
from app.model.group_user import GroupUser
from app.constants.roles import Role
from app.model.model_group import ModelGroup
from app.db.connection import PostgresConnection
from fastapi import BackgroundTasks, HTTPException  # type: ignore
import httpx  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy import and_, or_, select, func  # type: ignore
from sqlalchemy.sql import text  # type: ignore

handle_model = HandleModel()


class HandleGroup:

    def __init__(self):
        """Initialize the handle group"""
        self.token = settings.HOC_TIEP_KEY
        self.retries = settings.MAX_RETRIES
        self.hoc_tiep_be_url = settings.HOC_TIEP_BE_URL
        self.db_connection = PostgresConnection()
        asyncio.run_coroutine_threadsafe(
            self.db_connection.connect_db(), asyncio.get_event_loop()
        )

    async def initialize(self):
        await self.db_connection.connect_db()

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

    async def __get_default_permissions(self):
        """Default permissions"""
        headers = self.__get_headers()
        url = self.hoc_tiep_be_url + "/api/v1/users/default/permissions"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=100)
                response.raise_for_status()
                permissions = response.json()
        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: ", str(e))
        return permissions

    async def get_all_groups(
        self, target_db: AsyncSession, user_id: str, user_role: str
    ):
        """Get all the groups"""

        try:
            base_query = select(
                Group.id, Group.name, Group.description, User.name.label("user_name")
            ).join(User, Group.user_id == User.id)
            if user_role == Role.ADMIN.value:  # admin
                result = await target_db.execute(base_query)
            else:
                result = await target_db.execute(
                    base_query.join(GroupUser, GroupUser.group_id == Group.id).where(
                        GroupUser.user_id == user_id
                    )
                )
            groups = result.fetchall()
            groups_list = [
                {
                    "id": group[0],
                    "name": group[1],
                    "description": group[2],
                    "creator": group[3],
                }
                for group in groups
            ]
            return groups_list
        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: ", str(e))

    async def get_group_info(self, group_id: str, target_db: AsyncSession):
        group_result = await target_db.execute(
            select(
                Group.id,
                Group.name,
                Group.description,
                User.name.label("user_name"),
                Group.user_ids,
                Group.permissions,
            )
            .join(User, Group.user_id == User.id)
            .where(Group.id == group_id)
        )
        group = group_result.fetchone()
        if not group:
            raise ValueError(f"Group with id {group_id} not found")
        user_ids = group.user_ids or []
        members_result = await target_db.execute(
            select(User.id, User.name, User.email, User.role).where(
                User.id.in_(user_ids)
            )
        )
        members = members_result.fetchall()
        models_result = await target_db.execute(
            select(Model.id, Model.name)
            .join(ModelGroup, Model.id == ModelGroup.model_id)
            .where(ModelGroup.group_id == group_id)
        )
        models = models_result.fetchall()

        student_list = []
        teachers_list = []

        for member in members:
            member_info = {
                "id": member.id,
                "name": member.name,
                "email": member.email,
            }
            if member.role == Role.TEACHER.value:
                teachers_list.append(member_info)
            elif member.role == Role.STUDENT.value:
                student_list.append(member_info)

        models_list = [
            {
                "id": model.id,
                "name": model.name,
            }
            for model in models
        ]
        return {
            "id": group_id,
            "name": group.name,
            "description": group.description,
            "creator": group.user_name,
            "students": student_list,
            "teachers": teachers_list,
            "models": models_list,
            "permissions": group.permissions,
        }

    async def update_group_target_db(
        self,
        target_db: AsyncSession,
        # old_group_id: str,
        group,
    ):
        updated_group = {
            "id": group.get("id"),
            "user_id": group.get("user_id"),
            "name": group.get("name"),
            "description": group.get("description"),
            "data": group.get("data"),
            "meta": group.get("meta"),
            "permissions": group.get("permissions"),
            "user_ids": group.get("user_ids"),
            "updated_at": datetime.now().timestamp(),
        }
        try:
            update_stmt = text(
                """
                UPDATE "group"
                SET
                    id = :id,
                    user_id = :user_id,
                    name = :name,
                    description = :description,
                    data = :data,
                    meta = :meta,
                    permissions = :permissions,
                    user_ids = :user_ids,
                    updated_at = :updated_at
                WHERE id = :id
                """
            )

            await target_db.execute(
                update_stmt,
                {
                    "id": updated_group["id"],
                    # "old_id": old_group_id,
                    "user_id": updated_group["user_id"],
                    "name": updated_group["name"],
                    "description": updated_group["description"],
                    "data": json.dumps(updated_group["data"]),
                    "meta": json.dumps(updated_group["meta"]),
                    "permissions": json.dumps(updated_group["permissions"]),
                    "user_ids": json.dumps(updated_group["user_ids"]),
                    "updated_at": updated_group["updated_at"],
                },
            )

            await target_db.commit()

            # Update group_user
            result = await target_db.execute(
                select(GroupUser.user_id).where(
                    GroupUser.group_id == updated_group["id"]
                )
            )
            old_user_ids = [row.user_id for row in result.fetchall()]
            user_ids = updated_group["user_ids"] or []
            uids_added = set(user_ids) - set(old_user_ids)
            uids_removed = set(old_user_ids) - set(user_ids)

            tasks = [
                self.create_group_user_target_db(
                    target_db=target_db, group_id=updated_group["id"], user_id=user_id
                )
                for user_id in uids_added
            ]
            tasks.extend(
                [
                    self.delete_group_user_target_db(
                        target_db=target_db,
                        group_id=updated_group["id"],
                        user_id=user_id,
                    )
                    for user_id in uids_removed
                ]
            )
            await asyncio.gather(*tasks)
        except Exception as e:
            await target_db.rollback()
            raise e

    async def update_group_models(
        self,
        group_id: str,
        data: dict,
    ):
        """Update models associated with a group"""
        async with self.db_connection.get_session() as target_db:
            if data.get("model_ids", []) != []:
                update_model_group = {
                    "read": data.get("model_ids", []),
                    "write": [],
                }
                await self.update_models_of_group(
                    target_db=target_db,
                    group_id=group_id,
                    data=update_model_group,
                )

    async def update_group(
        self,
        target_db: AsyncSession,
        group_id: str,
        data,
        background_tasks: BackgroundTasks,
        # old_group_id: str = None
    ):
        """Update a group"""
        headers = self.__get_headers()
        update_url = self.hoc_tiep_be_url + "/api/v1/groups/id/" + group_id + "/update"

        new_group = None
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    update_url,
                    json=data.dict() if not isinstance(data, dict) else data,
                    headers=headers,
                    timeout=100,
                )
                response.raise_for_status()
                new_group = response.json()
                await self.update_group_target_db(target_db=target_db, group=new_group)

                background_tasks.add_task(
                    self.update_group_models,
                    group_id=group_id,
                    data=data.dict() if not isinstance(data, dict) else data,
                )

        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: ", str(e))

        # if old_group_id is None:
        # else:
        #     await self.update_group_target_db(
        #         target_db=target_db, old_group_id=old_group_id, group=new_group
        #     )
        if new_group is None:
            raise ValueError(
                "Failed to update group. No response received from the server."
            )
        return new_group

    async def delete_group_teacher_target_db(
        self, target_db: AsyncSession, group_id: str, user_id: str
    ):
        try:
            delete_stmt = text(
                """
                DELETE FROM "group_teacher"
                WHERE user_id = :user_id AND group_id = :group_id
                """
            )

            await target_db.execute(
                delete_stmt,
                {
                    "user_id": user_id,
                    "group_id": group_id,
                },
            )

            await target_db.commit()
        except Exception as e:
            await target_db.rollback()
            raise e

    async def delete_group_user_target_db(
        self, target_db: AsyncSession, group_id: str, user_id: str
    ):
        try:
            delete_stmt = text(
                """
                DELETE FROM "group_user"
                WHERE user_id = :user_id AND group_id = :group_id
                """
            )

            await target_db.execute(
                delete_stmt,
                {
                    "user_id": user_id,
                    "group_id": group_id,
                },
            )

            await target_db.commit()
        except Exception as e:
            raise e

    async def create_group_user_target_db(
        self, target_db: AsyncSession, group_id: str, user_id: str
    ):
        try:
            insert_stmt = text(
                """
                INSERT INTO "group_user" (
                    user_id,
                    group_id,
                    updated_at,
                    created_at
                ) VALUES (
                    :user_id,
                    :group_id,
                    :updated_at,
                    :created_at
                )
                """
            )

            await target_db.execute(
                insert_stmt,
                {
                    "user_id": user_id,
                    "group_id": group_id,
                    "updated_at": datetime.now().timestamp(),
                    "created_at": datetime.now().timestamp(),
                },
            )

            await target_db.commit()
        except Exception as e:
            await target_db.rollback()
            raise e

    async def create_group_target_db(self, target_db: AsyncSession, group):
        new_group = {
            "id": group.get("id"),
            "user_id": group.get("user_id", ""),
            "name": group.get("name"),
            "description": group.get("description"),
            "data": group.get("data", None),
            "meta": group.get("meta", None),
            "permissions": group.get("permissions", None),
            "user_ids": group.get("user_ids", []),
            "updated_at": datetime.now().timestamp(),
            "created_at": datetime.now().timestamp(),
        }
        try:
            # insert group
            insert_group_stmt = text(
                """
                INSERT INTO "group" (
                    id,
                    user_id,
                    name,
                    description,
                    data,
                    meta,
                    permissions,
                    user_ids,
                    updated_at,
                    created_at
                ) VALUES (
                    :id,
                    :user_id,
                    :name,
                    :description,
                    :data,
                    :meta,
                    :permissions,
                    :user_ids,
                    :updated_at,
                    :created_at
                )
            """
            )

            await target_db.execute(
                insert_group_stmt,
                {
                    "id": new_group["id"],
                    "user_id": new_group["user_id"],
                    "name": new_group["name"],
                    "description": new_group["description"],
                    "data": json.dumps(new_group["data"]),
                    "meta": json.dumps(new_group["meta"]),
                    "permissions": json.dumps(new_group["permissions"]),
                    "user_ids": json.dumps(new_group["user_ids"]),
                    "updated_at": new_group["updated_at"],
                    "created_at": new_group["created_at"],
                },
            )

            # Insert group_user
            for user_id in group.get("user_ids", []):
                await self.create_group_user_target_db(
                    target_db=target_db, group_id=new_group["id"], user_id=user_id
                )
            await target_db.commit()
        except Exception as e:
            await target_db.rollback()
            raise e
        return new_group

    async def process_group_creation(
        self,
        # temp_group_id: str,
        data: RequestCreateGroup,
        background_tasks: BackgroundTasks,
    ):
        """Xử lý background task cho việc tạo group"""
        async with self.db_connection.get_session() as target_db:
            try:
                updated_group_data = {
                    "id": data.get("id"),
                    "name": data.get("name", ""),
                    "user_id": data.get("user_id", ""),
                    "description": data.get("description", ""),
                    "data": data.get("data", None),
                    "meta": data.get("meta", None),
                    "user_ids": data.get("user_ids", []),
                    "model_ids": data.get("model_ids", []),
                    "permissions": await self.__get_default_permissions(),
                }
                await self.update_group(
                    target_db=target_db,
                    group_id=data.get("id"),
                    data=updated_group_data,
                    background_tasks=background_tasks,
                    # old_group_id=temp_group_id,
                )
                await target_db.commit()
            except httpx.HTTPStatusError as http_err:
                logging.error(
                    "HTTP Error: "
                    + str(http_err.response.status_code)
                    + "-"
                    + http_err.response.text
                )
            except Exception as e:
                logging.error("An error occurred: " + str(e))

    async def create_group(
        self,
        target_db: AsyncSession,
        data: RequestCreateGroup,
        background_tasks: BackgroundTasks,
    ):
        """Create a group"""
        try:
            headers = self.__get_headers()
            create_url = self.hoc_tiep_be_url + "/api/v1/groups/create"

            create_payload = {
                "name": data.name,
                "description": data.description,
                "user_ids": data.user_ids,
            }

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        create_url, json=create_payload, headers=headers, timeout=100
                    )
                    response.raise_for_status()
                    new_group = response.json()
                    new_group["user_ids"] = data.user_ids
                    new_group["model_ids"] = data.model_ids
                    await self.create_group_target_db(
                        target_db=target_db, group=new_group
                    )
                    background_tasks.add_task(
                        self.process_group_creation,
                        # temp_group_id=temp_group_id,
                        data=new_group,
                        background_tasks=background_tasks,
                    )

                    return new_group
            except httpx.HTTPStatusError as http_err:
                logging.error(
                    "HTTP Error: "
                    + str(http_err.response.status_code)
                    + "-"
                    + http_err.response.text
                )
            except Exception as e:
                logging.error("An error occurred: " + str(e))

        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: ", str(e))

    async def delete_group_access_model(
        self, group_id: str, model_id: str, target_db: AsyncSession
    ):
        try:
            model_query = select(
                Model.id,
                Model.base_model_id,
                Model.name,
                Model.params,
                Model.meta,
                Model.access_control,
            ).where(Model.id == model_id)
            model_result = await target_db.execute(model_query)
            model = model_result.fetchone()
            access_control = model.access_control or {}
            if access_control is not None:
                read_g_access = access_control.get("read", {}).get("group_ids", [])
                read_u_access = access_control.get("read", {}).get("user_ids", [])
                write_g_access = access_control.get("write", {}).get("group_ids", [])
                write_u_access = access_control.get("write", {}).get("user_ids", [])
                if group_id in read_g_access:
                    read_g_access.remove(group_id)

                if group_id in write_g_access:
                    write_g_access.remove(group_id)
                new_access_control = {
                    "read": {"group_ids": read_g_access, "user_ids": read_u_access},
                    "write": {
                        "group_ids": write_g_access,
                        "user_ids": write_u_access,
                    },
                }
                model_payload = {
                    "id": model.id,
                    "base_model_id": model.base_model_id,
                    "name": model.name,
                    "params": model.params,
                    "meta": model.meta,
                    "access_control": new_access_control,
                }
                await handle_model.update_model(
                    target_db=target_db, model_id=model_id, payload=model_payload
                )
        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: " + str(e))

    async def delete_group_target_db(self, group_id: str):
        try:
            async with self.db_connection.get_session() as target_db:
                models = await handle_model.get_models_for_group(
                    target_db=target_db, group_id=group_id
                )
                model_ids = set(model for model in models.get("read", [])) | set(
                    model for model in models.get("write", [])
                )
                for model_id in model_ids:
                    await self.delete_group_access_model(
                        group_id=group_id, model_id=model_id, target_db=target_db
                    )

                delete_model_group_stmt = text(
                    """
                    DELETE FROM "model_group"
                    WHERE group_id = :group_id
                    """
                )

                await target_db.execute(
                    delete_model_group_stmt,
                    {
                        "group_id": group_id,
                    },
                )

                delete_group_user_stmt = text(
                    """
                    DELETE FROM "group_user"
                    WHERE group_id = :group_id
                    """
                )

                await target_db.execute(
                    delete_group_user_stmt,
                    {
                        "group_id": group_id,
                    },
                )

                delete_group_stmt = text(
                    """
                    DELETE FROM "group"
                    WHERE id = :group_id
                    """
                )

                await target_db.execute(
                    delete_group_stmt,
                    {
                        "group_id": group_id,
                    },
                )

                await target_db.commit()
        except Exception as e:
            await target_db.rollback()
            logging.info(e)
            raise e

    async def delete_group(self, group_id: str, background_tasks: BackgroundTasks):
        """Delete a group"""
        headers = self.__get_headers()
        delete_url = self.hoc_tiep_be_url + "/api/v1/groups/id/" + group_id + "/delete"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(delete_url, headers=headers, timeout=100)
                response.raise_for_status()
        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: ", str(e))
        background_tasks.add_task(self.delete_group_target_db, group_id=group_id)
        return response.json() if response.status_code == 200 else response.text

    async def update_models_of_group(
        self, target_db: AsyncSession, group_id: str, data: RequestUpdateModelsGroup
    ):
        models, old_models = await asyncio.gather(
            handle_model.get_all_models(),
            handle_model.get_models_for_group(target_db=target_db, group_id=group_id),
        )

        old_read_model_ids = [model for model in old_models.get("read", [])]
        old_write_model_ids = [model for model in old_models.get("write", [])]

        new_read_model_ids = data.get("read", [])
        new_write_model_ids = data.get("write", [])

        read_models_added = list(set(new_read_model_ids) - set(old_read_model_ids))
        read_models_removed = list(set(old_read_model_ids) - set(new_read_model_ids))
        write_models_added = list(set(new_write_model_ids) - set(old_write_model_ids))
        write_models_removed = list(set(old_write_model_ids) - set(new_write_model_ids))

        diff_update_models = list(
            set(read_models_added)
            | set(read_models_removed)
            | set(write_models_added)
            | set(write_models_removed)
        )
        updated_models = []
        for model_id in diff_update_models:
            model = next(
                (md for md in models if md["id"] == model_id),
                None,
            )
            if model is None:
                continue
            access_control = model.get("access_control", None)
            if access_control is None:
                continue
            read_group_ids = access_control.get("read", {}).get("group_ids", [])
            read_user_ids = access_control.get("read", {}).get("user_ids", [])
            write_group_ids = access_control.get("write", {}).get("group_ids", [])
            write_user_ids = access_control.get("write", {}).get("user_ids", [])
            if group_id in write_group_ids:
                write_group_ids.remove(group_id)
                if model_id in read_models_removed:
                    read_group_ids.remove(group_id)
            elif group_id in read_group_ids:
                if model_id in write_models_added:
                    write_group_ids.append(group_id)
                else:
                    read_group_ids.remove(group_id)
            else:
                if model_id in write_models_added:
                    write_group_ids.append(group_id)
                read_group_ids.append(group_id)

            update_access_control = {
                "read": {"group_ids": read_group_ids, "user_ids": read_user_ids},
                "write": {"group_ids": write_group_ids, "user_ids": write_user_ids},
            }

            update_model_data = {**model, "access_control": update_access_control}
            updated_model = await handle_model.update_model(
                target_db=target_db, model_id=model_id, payload=update_model_data
            )
            updated_models.append(updated_model)

        return updated_models

    async def get_members_page(
        self,
        group_id: str,
        page: int,
        limit: int,
        query: str,
        search_by: str,
        target_db: AsyncSession,
    ):
        try:
            if page < 1 or limit < 1:
                raise ValueError("Page and limit must be positive integers")
            offset = (page - 1) * limit
            group_result = await target_db.execute(
                select(Group.user_ids).where(Group.id == group_id)
            )
            group = group_result.fetchone()

            if not group or not group.user_ids:
                return {"users": [], "total": 0}

            members_list = group.user_ids

            users_query = select(User).where(
                User.role == Role.STUDENT.value, User.id.in_(members_list)
            )
            if query:
                search_form = f"%{query}%"
                if search_by == "email":
                    users_query = users_query.where(User.email.ilike(search_form))
                else:
                    users_query = users_query.where(User.name.ilike(search_form))
            count_query = select(func.count()).select_from(users_query.subquery())
            total_result = await target_db.execute(count_query)
            total = total_result.scalar_one()

            users_result = await target_db.execute(
                users_query.offset(offset).limit(limit)
            )
            users = users_result.scalars().fetchall()
            users_list = [
                {
                    "name": u.name,
                    "email": u.email,
                    "role": u.role,
                    "created_at": self.__format_datetime(u.created_at),
                }
                for u in users
            ]

            return {"users": users_list, "total": total}
        except ValueError as ve:
            logging.error(f"Validation error: {str(ve)}")
            raise
        except Exception as e:
            logging.error(
                f"Error fetching group members for group {group_id}: {str(e)}"
            )
            raise

    async def get_models_for_group(self, target_db: AsyncSession, group_id: str):
        """Get all models for the group by id"""

        try:
            models_query = (
                select(
                    Model.id,
                    Model.name,
                    Model.meta,
                    User.name.label("user_name"),
                    Model.is_active,
                    Model.created_at,
                )
                .join(User, Model.user_id == User.id)
                .outerjoin(ModelGroup, Model.id == ModelGroup.model_id)
                .where(
                    and_(
                        ~Model.id.startswith("@"),
                        Model.is_active.is_(True),
                        ModelGroup.group_id == group_id,
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
            logging.error("An error occurred: ", str(e))

    async def get_teachers_page(
        self,
        group_id: str,
        page: int,
        limit: int,
        query: str,
        search_by: str,
        target_db: AsyncSession,
    ):
        try:
            if page < 1 or limit < 1:
                raise ValueError("Page and limit must be positive integers")
            offset = (page - 1) * limit
            group_result = await target_db.execute(
                select(Group.user_ids).where(Group.id == group_id)
            )
            group = group_result.fetchone()

            if not group or not group.user_ids:
                return {"users": [], "total": 0}

            members_list = group.user_ids

            users_query = select(User).where(
                User.role == Role.TEACHER.value, User.id.in_(members_list)
            )
            if query:
                search_form = f"%{query}%"
                if search_by == "email":
                    db_query = users_query.where(User.email.ilike(search_form))
                else:
                    db_query = users_query.where(User.name.ilike(search_form))
            count_query = select(func.count()).select_from(db_query.subquery())
            total_result = await target_db.execute(count_query)
            total = total_result.scalar_one()

            users_result = await target_db.execute(db_query.offset(offset).limit(limit))
            users = users_result.scalars().fetchall()
            users_list = [
                {
                    "name": u.name,
                    "email": u.email,
                    "role": u.role,
                    "created_at": self.__format_datetime(u.created_at),
                }
                for u in users
            ]

            return {"users": users_list, "total": total}
        except ValueError as ve:
            logging.error(f"Validation error: {str(ve)}")
            raise
        except Exception as e:
            logging.error(
                f"Error fetching group members for group {group_id}: {str(e)}"
            )
            raise
        
    async def delete_model_group(self, target_db: AsyncSession, group_id: str, model_id: str):
        """Delete a model in group"""

        try:
            old_model_ids_query = select(ModelGroup.model_id).where(ModelGroup.group_id == group_id)
            old_model_ids_result = await target_db.execute(old_model_ids_query)
            old_model_ids = [old_model_id[0] for old_model_id in old_model_ids_result.fetchall()]
            if not (model_id in old_model_ids):
                raise HTTPException(status_code=404, detail="Model with id: " + model_id + " not in group")
            else:
                new_model_ids = old_model_ids.remove(model_id)
                update_data = {
                    "read": new_model_ids,
                    "write": []
                }
                await self.update_models_of_group(target_db=target_db, group_id=group_id, data=update_data)
        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: ", str(e))
        return True
