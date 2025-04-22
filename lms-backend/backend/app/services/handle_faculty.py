from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy import select, update, delete  # type: ignore
from sqlalchemy.exc import IntegrityError  # type: ignore
from fastapi import HTTPException  # type: ignore
from app.model.faculty import Faculty
from app.model.department import Department
from app.schema.faculty import RequestCreateFaculty, RequestUpdateFaculty
import time
import uuid
from collections import defaultdict


class HandleFaculty:
    async def get_all_faculties(self, target_db: AsyncSession):
        result = await target_db.execute(select(Faculty))
        faculties = result.fetchall()
        faculties_data = [faculty[0].get_detail() for faculty in faculties]
        return faculties_data

    async def get_faculty_info(self, faculty_id: str, target_db: AsyncSession):
        result = await target_db.execute(
            select(Faculty).where(Faculty.id == faculty_id)
        )
        faculty = result.fetchone()
        if not faculty:
            raise HTTPException(status_code=404, detail="Faculty not found")
        faculty_data = faculty[0].get_detail()
        return faculty_data

    async def check_valid_faculty(
        self, target_db: AsyncSession, data, faculty_id: str = None
    ):
        if data.name is not None:
            is_existing_result = await target_db.execute(
                select(Faculty.id).where(Faculty.name == data.name)
            )
            is_existing = is_existing_result.fetchone()

            if is_existing:
                if faculty_id != is_existing.id:
                    raise HTTPException(
                        status_code=500,
                        detail=("Existing faculty with name : " + data.name),
                    )
        return True

    async def create_faculty(self, data: RequestCreateFaculty, target_db: AsyncSession):
        await self.check_valid_faculty(target_db=target_db, data=data)
        now = int(time.time())

        faculty = Faculty(
            id=str(uuid.uuid4()),
            name=data.name,
            created_at=now,
            updated_at=now,
        )
        try:
            target_db.add(faculty)
            faculty_data = faculty.get_detail()
            await target_db.commit()
            return faculty_data
        except IntegrityError as e:
            await target_db.rollback()
            raise Exception(f"Integrity error: {str(e)}")
        except Exception as e:
            await target_db.rollback()
            raise e

    async def update_faculty(
        self, faculty_id: str, data: RequestUpdateFaculty, target_db: AsyncSession
    ):
        await self.check_valid_faculty(
            target_db=target_db, data=data, faculty_id=faculty_id
        )
        now = int(time.time())
        stmt = (
            update(Faculty)
            .where(Faculty.id == faculty_id)
            .values(name=data.name, updated_at=now)
            .execution_options(synchronize_session="fetch")
        )
        await target_db.execute(stmt)
        await target_db.commit()
        return await self.get_faculty_info(faculty_id, target_db)

    async def delete_faculty(self, faculty_id: str, target_db: AsyncSession):
        stmt = delete(Faculty).where(Faculty.id == faculty_id)
        await target_db.execute(stmt)
        await target_db.commit()
        return True

    async def get_all_faculties_departments(self, target_db: AsyncSession):
        faculties_departments_query = select(
            Faculty.id.label("faculty_id"),
            Faculty.name.label("faculty_name"),
            Department.id.label("department_id"),
            Department.name.label("department_name"),
        ).join(Department, Faculty.id == Department.faculty_id)
        faculties_departments_result = await target_db.execute(
            faculties_departments_query
        )
        faculties_departments = faculties_departments_result.fetchall()
        print(faculties_departments)
        faculty_department_dict = defaultdict(
            lambda: {"faculty_id": None, "faculty_name": None, "departments": []}
        )
        for faculty_department in faculties_departments:
            faculty_id = faculty_department.faculty_id
            if faculty_department_dict[faculty_id]["faculty_id"] is None:
                faculty_department_dict[faculty_id]["faculty_id"] = faculty_id
                faculty_department_dict[faculty_id][
                    "faculty_name"
                ] = faculty_department.faculty_name
            faculty_department_dict[faculty_id]["departments"].append(
                {
                    "id": faculty_department.department_id,
                    "name": faculty_department.department_name,
                }
            )
        return list(faculty_department_dict.values())
