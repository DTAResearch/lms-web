from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy import select, update, delete  # type: ignore
from sqlalchemy.exc import IntegrityError  # type: ignore
from fastapi import HTTPException  # type: ignore
from app.model.department import Department
from app.model.faculty import Faculty
from app.schema.department import (
    RequestCreateDepartment,
    RequestUpdateDepartment,
)
import json
import time
import uuid


class HandleDepartment:
    async def get_all_departments(self, target_db: AsyncSession):
        result = await target_db.execute(
            select(Department.id, Department.name, Faculty.id, Faculty.name).join(
                Faculty, Department.faculty_id == Faculty.id
            )
        )
        departments = result.fetchall()
        departments_data = [
            {
                "department_id": department[0],
                "department_name": department[1],
                "faculty_id": department[2],
                "faculty_name": department[3],
            }
            for department in departments
        ]
        return departments_data

    async def get_department_info(self, department_id: str, target_db: AsyncSession):
        result = await target_db.execute(
            select(Department, Faculty)
            .join(Faculty, Faculty.id == Department.faculty_id)
            .where(Department.id == department_id)
        )
        department = result.fetchone()
        if not department:
            raise Exception("Department not found")
        department_data = department[0].get_detail()
        department_data["faculty_name"] = department[1].name
        return department_data

    async def check_valid_department(
        self, target_db: AsyncSession, data, department_id: str = None
    ):
        if data.faculty_id is not None:
            faculty = await target_db.get(Faculty, data.faculty_id)
            if not faculty:
                raise HTTPException(status_code=404, detail="Faculty ID not found.")
        if data.name is not None:
            is_existing_result = await target_db.execute(
                select(Department.id).where(Department.name == data.name)
            )
            is_existing = is_existing_result.fetchone()

            if is_existing:
                if department_id != is_existing.id:
                    raise HTTPException(
                        status_code=404,
                        detail=("Existing department with name : " + data.name),
                    )
        return faculty

    async def create_department(
        self, data: RequestCreateDepartment, target_db: AsyncSession
    ):
        faculty = await self.check_valid_department(target_db=target_db, data=data)
        now = int(time.time())
        department = Department(
            id=str(uuid.uuid4()),
            name=data.name,
            faculty_id=data.faculty_id,
            created_at=now,
            updated_at=now,
        )
        try:
            target_db.add(department)
            department_data = department.get_detail()
            department_data["faculty_name"] = faculty.name
            await target_db.commit()
            return department_data
        except IntegrityError as e:
            await target_db.rollback()
            raise Exception(f"Integrity error: {str(e)}")
        except Exception as e:
            await target_db.rollback()
            raise e

    async def update_department(
        self, department_id: str, data: RequestUpdateDepartment, target_db: AsyncSession
    ):
        await self.check_valid_department(
            target_db=target_db, data=data, department_id=department_id
        )
        now = int(time.time())
        stmt = (
            update(Department)
            .where(Department.id == department_id)
            .values(name=data.name, faculty_id=data.faculty_id, updated_at=now)
            .execution_options(synchronize_session="fetch")
        )
        await target_db.execute(stmt)
        await target_db.commit()
        return await self.get_department_info(department_id, target_db)

    async def delete_department(self, department_id: str, target_db: AsyncSession):
        stmt = delete(Department).where(Department.id == department_id)
        await target_db.execute(stmt)
        await target_db.commit()
        return True
