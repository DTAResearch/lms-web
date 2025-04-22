from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from app.services.auth.base_auth import get_current_user, TOKEN_BLACKLIST

router = APIRouter(prefix="/users")

@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    Lấy thông tin người dùng hiện tại từ access token.
    Hỗ trợ cả Google (require_db=True) và LDAP (require_db=False).
    """
    return {
        "email": current_user["email"],
        "role": current_user["role"],
        "login_type": current_user["login_type"],
        "avatar": current_user.get("avatar", ""),  # Thêm avatar nếu có
        }

@router.post("/logout")
async def logout(request: Request):
    """
    Đăng xuất người dùng, xóa cookie và thêm token vào blacklist.
    Chung cho mọi phương thức đăng nhập.
    """
    access_token = request.cookies.get("access_token")
    if access_token:
        TOKEN_BLACKLIST.add(access_token)
    response = JSONResponse(
        content={"message": "Đăng xuất thành công"},
        status_code=status.HTTP_200_OK  # Thay 200
    )
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")  # Nếu dùng refresh token
    return response