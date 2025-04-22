from fastapi import APIRouter, Depends, HTTPException, status as status_code, BackgroundTasks  # type: ignore
from app.schema.chat_response import BaseResponse
from app.services.handle_user import HandleUser
from app.db.target_db import get_target_session
from sqlalchemy.orm import Session  # type: ignore
from app.services.auth.base_auth import get_current_user
from app.constants.roles import Role
from app.model.user import User
from pydantic import BaseModel
from typing import Optional  # Thêm import này

router = APIRouter()
handle_user = HandleUser()


# Định nghĩa Pydantic model cho body request
class UpdateRoleRequest(BaseModel):
    new_role: str


@router.get("", response_model=BaseResponse)
async def get_users_page(
    page: int = 1,
    limit: int = 10,
    query: str = "",
    
    role: Optional[str] = None,  # Thêm tham số query role
    target_db: Session = Depends(get_target_session),
):
    """
    API lấy thông tin người dùng.
    """
    try:
        result = await handle_user.get_users_page(
            page=page,
            limit=limit,
            query=query,
            role=role,  # Truyền role vào service
            target_db=target_db,
        )
        return {
            "code": str(status_code.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.patch("/update-role/{user_id}", response_model=BaseResponse)
async def update_user_role(
    user_id: str,
    request: UpdateRoleRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    target_db: Session = Depends(get_target_session),
):
    """
    API cho phép admin thay đổi role của người dùng.
    """
    if current_user.get("role") != Role.ADMIN.value:
        raise HTTPException(status_code=403, detail="Only admin can update roles")

    new_role = request.new_role
    if new_role not in [Role.ADMIN.value, Role.STUDENT.value, Role.TEACHER.value]:
        raise HTTPException(status_code=400, detail="Invalid role")

    user = target_db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = new_role
    target_db.commit()
    target_db.refresh(user)

    background_tasks.add_task(
        handle_user.sync_role,
        user_id=user_id,
        role=(Role.ADMIN.value if new_role == Role.ADMIN.value else Role.STUDENT.value),
    )

    return {
        "code": str(status_code.HTTP_200_OK),
        "message": f"Role updated to {new_role} successfully",
        "data": {"id": user.id, "role": user.role},
    }
