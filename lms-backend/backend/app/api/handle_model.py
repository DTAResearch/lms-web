from fastapi import APIRouter, Depends, HTTPException, Request, status as status_code  # type: ignore
from typing import Optional
from app.schema.chat_response import BaseResponse
from app.services.handle_model import HandleModel
from app.schema.model import RequestCreateModel, RequestUpdateModel
from app.services.auth.base_auth import get_current_user

router = APIRouter()
handle_model = HandleModel()


@router.get("", response_model=BaseResponse)
async def get_all_models(
    request: Request, current_user: dict = Depends(get_current_user)
):
    """
    API lấy thông tin các models.
    """
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_model.get_all_models_info(
                target_db=target_db,
                user_id=current_user["id"],
                user_role=current_user["role"],
            )
        return {
            "code": str(status_code.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/private", response_model=BaseResponse)
async def get_all_private_models(request: Request,):
    """
    API lấy thông tin các models riêng tư.
    """
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_model.get_all_private_models_info(target_db=target_db)
        return {
            "code": str(status_code.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("", response_model=BaseResponse)
async def create_model(
    request: Request, rq_create_data: RequestCreateModel,
):
    """
    API tạo model.
    """
    try:
        async with request.state.postgres_pool as target_db:
                result = await handle_model.create_model(
                    payload=rq_create_data, target_db=target_db
                )
        return {
            "code": str(status_code.HTTP_201_CREATED),
            "message": "Successfully",
            "data": result,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e)) from e



@router.put("/{model_id}", response_model=BaseResponse)
async def update_model(
    request: Request,
    model_id: str,
    rq_update_data: RequestUpdateModel,
):
    """
    API cập nhật model.
    """
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_model.update_model(
                target_db=target_db, model_id=model_id, payload=rq_update_data
            )
        return {
            "code": str(status_code.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/{model_id}", response_model=BaseResponse)
async def delete_model(request: Request, model_id: str,):
    """
    API xóa model.
    """
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_model.delete_model(model_id=model_id, target_db=target_db)
        return {
            "code": str(status_code.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/base", response_model=BaseResponse)
async def get_all_base_models():
    """
    API lấy thông tin các models.
    """
    try:
        result = await handle_model.get_all_base_models()
        return {
            "code": str(status_code.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/toggle/is-active/{model_id}", response_model=BaseResponse)
async def toggle_is_active_status(
    request: Request,
    model_id: str,
):
    """
    API cập nhật is active model.
    """
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_model.toggle_status(
                target_db=target_db, model_id=model_id
            )
        return {
            "code": str(status_code.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{model_id}", response_model=BaseResponse)
async def get_model_by_id(
    request: Request,
    model_id: str,
):
    """
    API lấy thông tin model theo id.
    """
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_model.get_model_by_id(
                target_db=target_db, model_id=model_id
            )
        return {
            "code": str(status_code.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
