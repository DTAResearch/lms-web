from fastapi import HTTPException

class DatabaseError(HTTPException):
    def __init__(self, detail: str = "Database Error"):
        super().__init__(status_code=500, detail=detail)


class ChatProcessingError(HTTPException):
    def __init__(self, chat_id: str, detail: str = "Chat Processing Error"):
        super().__init__(status_code=500, detail=f"Chat Processing Error: {chat_id} : {detail}")