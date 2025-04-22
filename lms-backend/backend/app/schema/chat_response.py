from pydantic import BaseModel  
from typing import Optional, Any

class ChatResponse(BaseModel):
    id: str
    email: str
    user_name: str
    user_id: str
    title: str
    chat: dict
    updated_at: int  # timestamp in epoch
    created_at: int  # timestamp in epoch
    share_id: Optional[str] = None  # id of the chat to be shared
    archived: bool
    pinned: Optional[bool] = False
    meta: dict = {}
    folder_id: Optional[str] = None

class BaseResponse(BaseModel):
    code: str
    message: str
    data: Any