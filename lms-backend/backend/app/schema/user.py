from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any

class User(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str = Field(..., description="role of user, e.g., 'admin' or 'user'")
    profile_image_url: Optional[str]
    last_active_at: Optional[int]
    updated_at: Optional[int]
    created_at: Optional[int]
    api_key: Optional[str]
    settings: Optional[Dict[str, Any]]
    info: Optional[Dict[str, Any]]
    oauth_sub: Optional[str]

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    