import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException, Request, Depends, status
from sqlalchemy.orm import Session
from app.model.user import User
from app.db.target_db import get_target_session

# Cấu hình JWT
SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 90

# Blacklist để lưu token đã logout
TOKEN_BLACKLIST = set()

def create_access_token(data: dict, login_type: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Tạo access token với thông tin người dùng và loại đăng nhập.
    
    Args:
        data (dict): Dữ liệu để mã hóa (ví dụ: {"sub": email, "role": role})
        login_type (str): Loại đăng nhập ("google" hoặc "ldap")
        expires_delta (Optional[timedelta]): Thời gian hết hạn tùy chỉnh
    
    Returns:
        str: JWT access token
    """
    to_encode = data.copy()
    to_encode["login_type"] = login_type  # Thêm loại đăng nhập vào payload
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    request: Request,
    db: Session = Depends(get_target_session),
    require_db: bool = True
) -> Dict[str, str]:
    """
    Xác thực người dùng từ access token trong cookie.
    
    Args:
        request (Request): Request từ FastAPI để lấy cookie
        db (Session): Phiên database (tùy chọn, chỉ cần cho Google)
        require_db (bool): Yêu cầu kiểm tra user trong DB hay không (False cho LDAP)
    
    Returns:
        dict: Thông tin người dùng {"email": ..., "role": ..., "login_type": ...}
    
    Raises:
        HTTPException: Nếu token không hợp lệ hoặc hết hạn
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,  # Thay 401
            detail="No access token found"
        )
    if token in TOKEN_BLACKLIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,  # Thay 401 bằng 403
            detail="Token blacklisted"
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        login_type = payload.get("login_type")
        role = payload.get("role")  # Mặc định role là "user" nếu không có
        user_id = payload.get("id")  # Lấy user_id từ payload
        avatar = payload.get("avatar")  # Lấy profile_image_url từ payload
        
        if not email or not login_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,  # Thay 401
                detail="Invalid token"
            )
        
        # Nếu yêu cầu kiểm tra DB (Google OAuth)
        if require_db:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,  # Thay 401
                    detail="User not found"
                )
            print(f"User Email: {user.email}, Role: {user.role}, Login Type: {login_type}, User ID: {user.id}, avatar: {avatar}" )
            return {"email": user.email, "role": user.role, "login_type": login_type, "id": user.id, "avatar": avatar }
        
        # Trường hợp LDAP không dùng DB
        print(f"User Email: {email}, Role: {role}, Login Type: {login_type}, User ID: {user_id}, avatar: {avatar}")
        return {"email": email, "role": role, "login_type": login_type, "id": user_id, "avatar": avatar }
    
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,  # Thay 401
            detail="Access token expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,  # Thay 401
            detail="Invalid token"
        )