from pydantic import BaseModel  # type: ignore


class RequestCreateDepartment(BaseModel):
    name: str
    faculty_id: str


class RequestUpdateDepartment(BaseModel):
    name: str
    faculty_id: str

