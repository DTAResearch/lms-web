from fastapi import APIRouter, Request, Depends, HTTPException, status  # type: ignore
from app.services.handle_department import HandleDepartment
from app.schema.department import RequestCreateDepartment, RequestUpdateDepartment
from app.schema.chat_response import BaseResponse

router = APIRouter()
handle_department = HandleDepartment()


@router.get("", response_model=BaseResponse)
async def get_all_departments(request: Request):
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_department.get_all_departments(target_db=target_db)
        return {
            "code": str(status.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{department_id}", response_model=BaseResponse)
async def get_department_detail(request: Request, department_id: str):
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_department.get_department_info(
                department_id, target_db=target_db
            )
        return {
            "code": str(status.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=BaseResponse)
async def create_department(request: Request, data: RequestCreateDepartment):
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_department.create_department(
                data=data, target_db=target_db
            )
        return {
            "code": str(status.HTTP_201_CREATED),
            "message": "Successfully",
            "data": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{department_id}", response_model=BaseResponse)
async def update_department(
    request: Request, department_id: str, data: RequestUpdateDepartment
):
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_department.update_department(
                department_id=department_id, data=data, target_db=target_db
            )
        return {
            "code": str(status.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{department_id}", response_model=BaseResponse)
async def delete_department(request: Request, department_id: str):
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_department.delete_department(
                department_id, target_db=target_db
            )
        return {
            "code": str(status.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
