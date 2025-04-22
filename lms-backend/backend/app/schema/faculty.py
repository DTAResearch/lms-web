from pydantic import BaseModel  # type: ignore


class RequestCreateFaculty(BaseModel):
    name: str


class RequestUpdateFaculty(BaseModel):
    name: str
