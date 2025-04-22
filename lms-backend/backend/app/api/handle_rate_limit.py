from fastapi import APIRouter, Depends, HTTPException  # type: ignore
from app.schema.chat_response import BaseResponse
from app.services.handle_rate_limit import HandleRateLimit
from app.services.handle_model import HandleModel
from app.db.target_db import get_target_session
from sqlalchemy.orm import Session  # type: ignore

router = APIRouter()
handle_rate_limit = HandleRateLimit()
handle_model = HandleModel()

@router.get("/user_detail", response_model=BaseResponse)
async def get_limit_for_user(
    user_id: str, model_id: str, target_db: Session = Depends(get_target_session)
):
    """
    API lấy thông tin limit cho người dùng.
    """
    try:
        result = await handle_rate_limit.get_limit_for_user(target_db=target_db, user_id=user_id, model_id=model_id)
        base_model = await handle_model.get_base_model_id(model_id=model_id)
        return {
            "code": "200",
            "message": "Successfully",
            "data": {
                "user_id": user_id,
                "rate_limit": result,
                "base_model": base_model
            },
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
