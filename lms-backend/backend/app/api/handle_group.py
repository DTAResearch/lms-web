"""
Module handle_group: Xử lý các yêu cầu liên quan đến nhóm.
"""

from fastapi import APIRouter, Depends, HTTPException, status as status_code, BackgroundTasks, Request  # type: ignore
from app.services.handle_group import HandleGroup
from app.services.handle_model import HandleModel
from app.schema.chat_response import BaseResponse
from app.schema.group import (
    RequestCreateGroup,
    RequestUpdateGroup,
    RequestUpdateModelsGroup,
)
from app.services.auth.base_auth import get_current_user
from typing import List

router = APIRouter()
handle_group = HandleGroup()
handle_model = HandleModel()


@router.get("", response_model=BaseResponse)
async def get_all_groups(
    request: Request, current_user: dict = Depends(get_current_user)
):
    """
    API lấy thông tin các group của người dùng.
    """
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_group.get_all_groups(
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


@router.get("/{group_id}", response_model=BaseResponse)
async def get_group_detail(
    request: Request,
    group_id: str,
):
    """
    API lấy thông tin group.
    """
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_group.get_group_info(
                group_id=group_id, target_db=target_db
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


@router.post("", response_model=BaseResponse)
async def create_group(
    request: Request,
    rq_create_data: RequestCreateGroup,
    background_tasks: BackgroundTasks,
):
    """
    API tạo thông tin các group của người dùng.
    """
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_group.create_group(
                target_db=target_db,
                data=rq_create_data,
                background_tasks=background_tasks,
            )
        return {
            "code": str(status_code.HTTP_201_CREATED),
            "message": "Successfully",
            "data": result,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/{group_id}", response_model=BaseResponse)
async def update_group(
    request: Request,
    group_id: str,
    rq_update_data: RequestUpdateGroup,
    background_tasks: BackgroundTasks,
):
    """
    API cập nhật thông tin các group của người dùng.
    """
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_group.update_group(
                group_id=group_id,
                data=rq_update_data,
                target_db=target_db,
                background_tasks=background_tasks,
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


@router.delete("/{group_id}", response_model=BaseResponse)
async def delete_group(
    group_id: str,
    background_tasks: BackgroundTasks,
):
    """
    API lấy thông tin các group của người dùng.
    """
    try:
        result = await handle_group.delete_group(
            group_id=group_id, background_tasks=background_tasks
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


@router.post("/{group_id}/update-models", response_model=BaseResponse)
async def update_group_models(
    request: Request,
    group_id: str,
    rq_update_data: RequestUpdateModelsGroup,
):
    """
    API cập nhật thông tin các model của group.
    """
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_group.update_models_of_group(
                target_db=target_db, group_id=group_id, data=rq_update_data.dict()
            )
        return {
            "code": str(status_code.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except HTTPException as e:
        print(e)
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/members/{group_id}", response_model=BaseResponse)
async def get_group_members(
    request: Request,
    group_id: str,
    page: int = 1,
    limit: int = 10,
    query: str = "",
    searchBy: str = "",
):
    """
    API lấy thông tin thành viên trong group.
    """
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_group.get_members_page(
                group_id=group_id,
                page=page,
                limit=limit,
                query=query,
                search_by=searchBy,
                target_db=target_db,
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


@router.get("/{group_id}/models", response_model=BaseResponse)
async def get_models_group(
    request: Request,
    group_id: str,
):
    """
    API lấy thông tin các model của group.
    """
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_group.get_models_for_group(
                target_db=target_db, group_id=group_id
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


@router.get("/teachers/{group_id}", response_model=BaseResponse)
async def get_group_teachers(
    request: Request,
    group_id: str,
    page: int = 1,
    limit: int = 10,
    query: str = "",
    searchBy: str = "",
):
    """
    API lấy thông tin giáo viên trong group.
    """
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_group.get_teachers_page(
                group_id=group_id,
                page=page,
                limit=limit,
                query=query,
                search_by=searchBy,
                target_db=target_db,
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
    
@router.delete("/{group_id}/model/{model_id}", response_model=BaseResponse)
async def delete_model_group(
    request: Request,
    group_id: str,
    model_id: str,
):
    """
    API xóa model khỏi lớp.
    """
    try:
        async with request.state.postgres_pool as target_db:
            result = await handle_group.delete_model_group(
                target_db=target_db, group_id=group_id, model_id=model_id
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

# Test
@router.get("/{group_id}/all-models", response_model=BaseResponse)
async def get_all_models_with_assignment(
    request: Request,
    group_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    API lấy thông tin tất cả các model, với trạng thái đã gán cho group.
    """
    try:
        async with request.state.postgres_pool as target_db:
            # Verify group exists
            # group_exists = await target_db.execute(
            #     select(Group.id).where(Group.id == group_id)
            # )
            # if not group_exists.fetchone():
            #     raise HTTPException(status_code=404, detail=f"Group {group_id} not found")

            # Fetch all models accessible to the user
            all_models = await handle_model.get_all_models_info(
                target_db=target_db,
                user_id=current_user["id"],
                user_role=current_user["role"]
            )
            # Fetch models assigned to the group
            group_models = await handle_model.get_models_for_group(  # Changed to handle_model
                target_db=target_db,
                group_id=group_id
            )
            # Safely access read and write lists
            assigned_model_ids = set(
                group_models.get("read", []) + group_models.get("write", [])
            )
            
            # Combine data, marking assigned models
            result = [
                {
                    **model,
                    "is_assigned": model["id"] in assigned_model_ids
                }
                for model in all_models
            ]
            
            return {
                "code": str(status_code.HTTP_200_OK),
                "message": "Successfully",
                "data": result
            }
    except HTTPException as e:
        raise e
    except Exception as e:
        # logging.error("Error in get_all_models_with_assignment: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e