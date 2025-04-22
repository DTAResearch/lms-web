from pydantic import BaseModel  # type: ignore
from typing import List, Optional


class GroupUserIds(BaseModel):
    group_ids: List[str]
    user_ids: List[str]


class AccessControl(BaseModel):
    read: GroupUserIds
    write: GroupUserIds


class Capabilities(BaseModel):
    vision: bool
    usage: bool
    citations: bool


class Meta(BaseModel):
    capabilities: Capabilities
    description: str
    profile_image_url: str
    suggestion_prompts: list[str]
    tags: List[str]
    knowledge: Optional[list[dict]] = None


class RequestCreateModel(BaseModel):
    id: str
    name: str
    base_model_id: str
    params: dict
    access_control: Optional[AccessControl] = None
    meta: Meta


class RequestUpdateModel(BaseModel):
    id: str
    base_model_id: str
    name: str
    params: dict
    meta: Meta
    access_control: Optional[AccessControl] = None
