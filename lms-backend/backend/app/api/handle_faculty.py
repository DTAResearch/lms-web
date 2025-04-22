from fastapi import APIRouter, Request, Depends, HTTPException, status  # type: ignore
from app.services.handle_faculty import HandleFaculty
from app.schema.faculty import RequestCreateFaculty, RequestUpdateFaculty
from app.schema.chat_response import BaseResponse

router = APIRouter()
handle_faculty = HandleFaculty()


@router.get("", response_model=BaseResponse)
async def get_all_faculties(request: Request):
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_faculty.get_all_faculties(target_db=target_db)
        return {
            "code": str(status.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{faculty_id}", response_model=BaseResponse)
async def get_faculty_detail(request: Request, faculty_id: str):
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_faculty.get_faculty_info(
                faculty_id, target_db=target_db
            )
        return {
            "code": str(status.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=BaseResponse)
async def create_faculty(request: Request, data: RequestCreateFaculty):
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_faculty.create_faculty(data=data, target_db=target_db)
        return {
            "code": str(status.HTTP_201_CREATED),
            "message": "Successfully",
            "data": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{faculty_id}", response_model=BaseResponse)
async def update_faculty(request: Request, faculty_id: str, data: RequestUpdateFaculty):
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_faculty.update_faculty(
                faculty_id=faculty_id, data=data, target_db=target_db
            )
        return {
            "code": str(status.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{faculty_id}", response_model=BaseResponse)
async def delete_faculty(request: Request, faculty_id: str):
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_faculty.delete_faculty(
                faculty_id, target_db=target_db
            )
        return {
            "code": str(status.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all/departments", response_model=BaseResponse)
async def get_all_faculties_departments(request: Request):
    try:
        print(1)
        async with request.state.postgres_pool as target_db:
            result = await handle_faculty.get_all_faculties_departments(
                target_db=target_db
            )
        return {
            "code": str(status.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
