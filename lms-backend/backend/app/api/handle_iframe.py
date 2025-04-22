from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from app.services.handle_iframe import IframeService
from app.services.auth.base_auth import get_current_user
from app.db.target_db import get_target_session
from app.constants.roles import Role

router = APIRouter()
iframe_service = IframeService()

@router.get("/dashboard")
async def get_role_dashboard(
    group_id: Optional[str] = Query(None),
    groups: Optional[List[str]] = Query(None),
    db: Session = Depends(get_target_session),
    current_user: dict = Depends(get_current_user)
):
    try:
        role = current_user["role"]
        user_id = current_user["id"]
        
        if not role or not user_id:
            raise HTTPException(status_code=400, detail="Missing user info")

        if group_id:
            groups = [group_id]
        elif not groups:
           
            if role == Role.ADMIN.value:
                groups = iframe_service.get_admin_groups(db)
            elif role == Role.TEACHER.value:
                groups = iframe_service.get_teacher_groups(db, user_id)
            else:  # student
                groups = iframe_service.get_user_groups(db, user_id)
        
        if role == Role.ADMIN.value:
            url = iframe_service.get_admin_dashboard_url(user_id=user_id, groups=groups)
        elif role == Role.TEACHER.value:
            url = iframe_service.get_teacher_dashboard_url(
                db=db,
                user_id=user_id,
                custom_groups=groups
            )
        else:  # student
            url = iframe_service.get_student_dashboard_url(
                db=db,
                user_id=user_id,
                custom_groups=groups
            )
            
        return {"code": "200", "message": "Success", "data": url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/group-stats")
async def get_group_stats_dashboard(
    group_id: str = Query(..., description="Group ID"),
    db: Session = Depends(get_target_session),
    current_user: dict = Depends(get_current_user)
):
    try:
        url = iframe_service.get_group_stats_url(
            db=db,
            user_id=current_user["id"],
            role=current_user["role"],
            group_id=group_id
        )
        return {"code": "200", "message": "Success", "data": url}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/teacher-dashboard")
async def get_teacher_dashboard(
    group_id: str = Query(..., description="Group ID"),
    db: Session = Depends(get_target_session)
):
    try:
        url = iframe_service.get_teacher_dashboard_by_group(group_id)
        return {"code": "200", "message": "Success", "data": url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))