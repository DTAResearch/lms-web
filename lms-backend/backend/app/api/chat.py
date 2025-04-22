from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
# from sqlalchemy.orm import Session
# from ..db.target_db import get_target_session
from ..services.chat.get_message import GetMessageService
from ..services.i18 import translate


router = APIRouter()
get_chat_messages_service = GetMessageService()

@router.get("/chat/messages")
async def get_chat_messages(
    request: Request,
    chat_id: str = Query(..., description="Chat ID to fetch messages"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of messages per page"),
    # target_db: Session = Depends(get_target_session),
) -> JSONResponse:
    """API to get paginated chat messages by chat_id"""
    try:
        lang = request.state.lang
        # postgres_pool = request.state.postgres_pool
        async with request.state.postgres_pool as session:
            chat_messages, total_messages = await get_chat_messages_service.get_chat_messages(
                chat_id=chat_id,
                db_session=session,
                page=page,
                page_size=page_size
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "message": translate("get_chat_messages_success", lang=lang),
                "data": {
                    "messages": chat_messages,
                    "pagination": {
                        "current_page": page,
                        "page_size": page_size,
                        "total_messages": total_messages,
                        "total_pages": (total_messages + page_size - 1) // page_size
                    }
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": translate("internal_server_error", lang=lang),
                "error": str(e)
            }
        )