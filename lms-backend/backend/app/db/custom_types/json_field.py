# pylint: disable=too-many-ancestors

"""
Module chứa JSONField - một kiểu dữ liệu tùy chỉnh cho SQLAlchemy.
"""

import json
from typing import Any, Optional
from sqlalchemy.types import TypeDecorator, Text
from sqlalchemy.engine.interfaces import Dialect

class JSONField(TypeDecorator):
    """
    JSONField là một kiểu dữ liệu tùy chỉnh của SQLAlchemy, 
    giúp lưu trữ dữ liệu JSON dưới dạng text.
    """
    impl = Text
    cache_ok = True

    def process_bind_param(self, value: Optional[Any], dialect: Dialect) -> Any:
        """
        Chuyển đổi giá trị Python thành chuỗi JSON trước khi lưu vào database.
        """
        return json.dumps(value) if value is not None else None

    def process_result_value(self, value: Optional[Any], dialect: Dialect) -> Any:
        """
        Chuyển đổi chuỗi JSON từ database thành object Python.
        """
        return json.loads(value) if value is not None else None

    def process_literal_param(self, value: Any, dialect: Dialect) -> Any:
        """
        Cần thiết để tránh lỗi abstract-method của pylint.
        """
        return json.dumps(value) if value is not None else None

    def copy(self, **kw: Any) -> "JSONField":
        """
        Tạo một bản sao của JSONField.
        """
        return JSONField(self.impl.length)

    def db_value(self, value: Any) -> str:
        """
        Chuyển đổi giá trị Python thành JSON string.
        """
        return json.dumps(value) if value is not None else None

    def python_value(self, value: Any) -> Any:
        """
        Chuyển đổi JSON string thành object Python.
        """
        return json.loads(value) if value is not None else None

    @property
    def python_type(self) -> type:
        """
        Xác định kiểu dữ liệu trả về cho SQLAlchemy.
        """
        return dict
