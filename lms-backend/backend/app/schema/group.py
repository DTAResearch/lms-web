from pydantic import BaseModel   # type: ignore
from typing import List, Optional, Dict, Any

class WorkspacePermission(BaseModel):
    models: bool
    knowledge: bool
    prompts: bool
    tools: bool
    
class ChatPermission(BaseModel):
    controls: bool
    file_upload: bool
    delete: bool
    edit: bool
    temporary: bool
    
class FeaturesPermission(BaseModel):
    web_search: bool
    image_generation: bool
    code_interpreter: bool

class GroupPermission(BaseModel):
    workspace: WorkspacePermission
    chat: ChatPermission
    features: FeaturesPermission

class RequestCreateGroup(BaseModel):
    name: str
    description: str
    user_ids: List[str]
    model_ids: List[str]
    
class RequestUpdateGroup(BaseModel):
    id: str
    name: str
    description: str
    permissions: GroupPermission
    # permissions: Optional[Dict[str, Any]] = None  # Cho phép null hoặc dict
    user_ids: List[str]
    model_ids: List[str]

class RequestUpdateModelsGroup(BaseModel):
    read: List[str]
    write: List[str]
