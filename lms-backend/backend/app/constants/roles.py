from enum import Enum


class Role(Enum):
    ADMIN = "admin"
    STUDENT = "user"
    TEACHER = "teacher"