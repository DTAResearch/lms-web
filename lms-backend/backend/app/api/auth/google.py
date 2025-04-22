from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from google.oauth2 import id_token
from google.auth.transport import requests as grequests

from ...model.user import User
from ...db.target_db import get_target_session
from ...services.auth.base_auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from ...services.i18 import translate, get_request_language

load_dotenv()

router = APIRouter(prefix="/auth/google")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

class TokenData(BaseModel):
    id_token: str

@router.post("/verify-id-token")
async def verify_id_token(token_data: TokenData, request: Request, db: Session = Depends(get_target_session)):
    lang = get_request_language(request)

    if not request.headers.get("X-Requested-With"):
        raise HTTPException(status_code=403, detail=translate("csrf_failed", lang=lang))

    try:
        # Xác thực id_token
        idinfo = id_token.verify_oauth2_token(token_data.id_token, grequests.Request(), GOOGLE_CLIENT_ID)

        email = idinfo.get("email")
        avatar = idinfo.get("picture")

        if not email:
            raise HTTPException(status_code=422, detail=translate("no_email", lang=lang))

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail={
                    "message": translate("user_not_found", lang=lang),
                    "action": translate("register_action", lang=lang)
                }
            )

        app_access_token = create_access_token(data={
            "sub": email,
            "role": user.role,
            "id": user.id,
            "avatar": avatar
        }, login_type="google")
        print(f"Set cookie: {app_access_token}")


        response = JSONResponse(
            content={
                "status": "success", 
                "message": translate("login_success", lang=lang), 
                "email": email,
                "token": app_access_token  # Add the token to the response body
            },
            status_code=200
        )

        # Thiết lập cookie
        secure = os.getenv("ENV") != "development"
        samesite = "lax" if not secure else "None"
        domain = "" if not secure else ".hoctiep.com"

        response.set_cookie(
            key="access_token",
            value=app_access_token,
            httponly=True,
            secure=secure,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite=samesite,
            path="/",
            domain=domain
        )
        
       
        return response

    except ValueError:
        raise HTTPException(status_code=401, detail=translate("invalid_id_token", lang=lang))


# @router.get("/user/{user_id}")
# async def get_user_by_id(user_id: str, db: Session = Depends(get_target_session)):
#     """
#     Truy vấn tất cả thông tin của user dựa trên user_id.
    
#     Args:
#         user_id (str): ID của user (ví dụ: 30de9ef6-a9fd-41a9-8420-74064da4d7d5)
#         db (Session): Phiên database
    
#     Returns:
#         dict: Tất cả thông tin của user
    
#     Raises:
#         HTTPException: Nếu user không tồn tại
#     """
#     # Truy vấn user từ database
#     user = db.query(User).filter(User.id == user_id).first()
    
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     # Trả về tất cả thông tin của user dưới dạng dictionary
#     return {column.name: getattr(user, column.name) for column in user.__table__.columns}