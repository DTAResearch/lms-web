from pydantic import BaseModel  # type: ignore
from typing import Optional, List
from .model import AccessControl


class DataKnowledge(BaseModel):
    file_ids: Optional[List[str]]


class RequestCreateKnowledge(BaseModel):
    name: str
    description: str
    data: Optional[DataKnowledge] = None
    access_control: Optional[AccessControl] = None
