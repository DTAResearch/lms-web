import json
import asyncio
from typing import Tuple, List, Dict, Any
from sqlalchemy import text
from fastapi import HTTPException
from functools import lru_cache
from ...model.model import Model
from sqlalchemy.ext.asyncio import AsyncSession


class GetMessageService:
    """Service to get chat messages by chat_id with pagination and extreme optimization"""

    def __init__(self):
        self._model_cache = {}

    async def get_chat_messages(
        self,
        chat_id: str,
        db_session: AsyncSession,
        page: int,
        page_size: int,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Retrieve paginated chat messages by chat_id with extreme optimization

        Args:
            chat_id (str): The ID of the chat
            target_db (Session): The database session
            page (int): Page number
            page_size (int): Number of messages per page

        Returns:
            Tuple[List[Dict], int]: List of chat messages and total count
        """
        async with db_session.begin():
            result = await db_session.execute(
                    text("SELECT chat FROM chat WHERE id = :chat_id"),
                    {"chat_id": chat_id},
                )
            chat = result.fetchone()
        
        if not chat:
            raise HTTPException(status_code=404, detail=f"Chat {chat_id} not found")

        # Parse JSON trong thread riêng để không block event loop
        chat_content = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self._safe_json_loads(chat.chat)
        )
        if not isinstance(chat_content, dict):
            raise HTTPException(status_code=400, detail="Invalid chat content format")

        chat_messages = chat_content.get("messages", [])
        total_messages = len(chat_messages)
        if not chat_messages:
            return [], 0

        # Tính toán phân trang
        start_idx = max(0, (page - 1) * page_size)
        end_idx = min(start_idx + page_size, total_messages)
        paginated_messages = chat_messages[start_idx:end_idx]

        if not paginated_messages:
            return [], total_messages

        # Tối ưu truy vấn model với batch processing
        model_ids = set()
        for msg in paginated_messages:
            if model_id := msg.get("model"):  # Sử dụng walrus operator
                model_ids.add(model_id)
            model_ids.update(msg.get("models", []))

        # Truy vấn models bất đồng bộ với caching
        model_dict = await self._get_models(db_session, model_ids)

        # Xử lý tin nhắn với list comprehension thay vì vòng lặp append
        filtered_messages = [
            self._process_message(msg, model_dict)
            for msg in paginated_messages
        ]

        return filtered_messages, total_messages

    async def _get_models(self, db_session: AsyncSession, model_ids: set) -> Dict[str, Model]:
        """Get models with caching and async optimization"""
        if not model_ids:
            return {}

        # Check cache trước
        cached_models = {mid: self._model_cache[mid] for mid in model_ids if mid in self._model_cache}
        missing_ids = model_ids - set(cached_models.keys())

        if missing_ids:
            async with db_session.begin():
                result = await db_session.execute(
                    text("SELECT id, meta FROM model WHERE id = ANY(:ids)"),
                    {"ids": tuple(missing_ids)}
                )
                models = result.fetchall()
        
            new_models = {model.id: model for model in models}
            self._model_cache.update(new_models)  # Update cache
            cached_models.update(new_models)

        return cached_models

    @staticmethod
    def _process_message(msg: Dict[str, Any], model_dict: Dict[str, Model]) -> Dict[str, Any]:
        """Process individual message with optimization"""
        message_data = {
            "id": msg.get("id"),
            "role": msg.get("role"),
            "content": msg.get("content"),
            "timestamp": msg.get("timestamp"),
        }

        role = message_data["role"]
        if role in {"user", "admin"}:
            if models := msg.get("models", []):
                message_data["models"] = [
                    {"id": mid}  # Chỉ lấy id để giảm payload
                    for mid in models if mid in model_dict
                ]
        elif role == "assistant":
            if model_id := msg.get("model"):
                if model_id in model_dict:
                    message_data["modelName"] = msg.get("modelName")
                    message_data["model"] = {"id": model_id}

        return message_data

    @staticmethod
    @lru_cache(maxsize=1024)
    def _safe_json_loads(data: str) -> Any:
        """Cached safe JSON parsing"""
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return data if not isinstance(data, str) else {}