"""
Module handle_chat: Xử lý các yêu cầu và trả lời trong hệ thống chat.

Module này chứa các hàm và lớp để xử lý các cuộc trò chuyện giữa người dùng và hệ thống,
bao gồm việc phân tích yêu cầu và trả lời tự động.
"""

import traceback
import time
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status  # type: ignore
from sqlalchemy import select  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from sqlalchemy.exc import SQLAlchemyError  # type: ignore
from ..services.handle_chat import HandleChat
# from ..db.target_db import get_target_session
from ..db.source_db import get_source_session
from ..model.chat import Chat
from ..utils.telegram_bot import TelegramBot
from ..exceptions.custom_exceptions import ChatProcessingError
from ..services.i18 import translate, get_request_language


router = APIRouter()
handle_chat = HandleChat()
bot = TelegramBot()


@router.post("/detect-knowledge/{chat_id}")
async def detect_single_knowledge(
    request: Request,
    chat_id: str,
):
    """
    API để xử lý việc phân loại dữ liệu từ chat
    """
    lang = get_request_language(request)
    try:
        async with request.state.postgres_pool as session:
            # Xử lý detect knowledge
            await handle_chat.detect_knowledge(
                chat_id=chat_id, target_db=session, lang=lang, check_time=time.time()
            )

    except ChatProcessingError as e:
        bot.add_message(f"Custom Error: {e.detail}")
        await bot.send_combined_message()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)

    except ValueError as e:
        bot.add_message(f"ValueError in chat_id {chat_id}: {str(e)}")
        await bot.send_combined_message()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate("invalid_request_data", lang=lang),
        )

    except Exception as e:
        print(f"Unexpected Error in chat_id {chat_id}: {str(e)}")
        bot.add_message(f"Unexpected Error in chat_id {chat_id}: {str(e)}")
        await bot.send_combined_message()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=translate("internal_server_error", lang=lang),
        )
    return {
        "code": status.HTTP_200_OK,
        "message": translate("chat_updated_successfully", lang=lang),
    }


@router.post("/sync-and-calculate-scores")
async def sync_and_calculate_scores(
    request: Request,
    source_db: Session = Depends(get_source_session),
):
    """
    API để đồng bộ và tính toán điểm số cho tất cả các chat ID.
    """
    lang = get_request_language(request)
    try:
        check_time = time.time()
        async with request.state.postgres_pool as session:
            errors = await handle_chat.handle_score_all(
                target_db=session, source_db=source_db, check_time=check_time
            )
            if errors:
                for error in errors:
                    err_msg = (
                        "Error in chat_id: "
                        + error["chat_id"]
                        + "\nTraceback: "
                        + error["traceback"]
                    )
                    bot.add_message(err_msg)
                await bot.send_combined_message()
                return {
                    "code": status.HTTP_207_MULTI_STATUS,
                    "message": translate("processed_with_errors", lang=lang),
                    "data": None,
                }
    except (SQLAlchemyError, RuntimeError) as e:
        error_details = traceback.format_exc()  # Lấy toàn bộ stack trace
        bot.add_message(f"Exception details: {str(e)}")
        bot.add_message(f"Unexpected Error when handle chat: {error_details}")
        traceback.print_exc()  # In lỗi trực tiếp ra terminal
        await bot.send_combined_message()

    return {
        "code": status.HTTP_200_OK,
        "message": translate("scores_calculated_successfully", lang=lang),
        "data": None,
    }


@router.post("/recalculate-scores")
async def recalculate_scores(
    request: Request,
):
    """
    API tính toán lại điểm số cho tất cả các chat ID.
    """
    lang = get_request_language(request)
    try:
        bot.add_message(
            "Bắt đầu chấm điểm lại lúc: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        await bot.send_combined_message()
        async with request.state.postgres_pool as session:
            errors = await handle_chat.handle_score_all(target_db=session, source_db=None, check_time=1)
            if errors:
                for error in errors:
                    err_msg = (
                        "Error in chat_id: "
                        + error["chat_id"]
                        + "\nTraceback: "
                        + error["traceback"]
                    )
                    bot.add_message(err_msg)
                await bot.send_combined_message()
                return {
                    "code": status.HTTP_207_MULTI_STATUS,
                    "message": translate("processed_with_errors", lang=lang),
                    "data": None,
                }
    except Exception as e:
        error_details = traceback.format_exc()  # Lấy toàn bộ stack trace
        bot.add_message(f"Exception details: {str(e)}")
        bot.add_message(f"Unexpected Error when handle chat: {error_details}")
        traceback.print_exc()  # In lỗi trực tiếp ra terminal
        await bot.send_combined_message()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=translate("internal_server_error", lang=lang),
        ) from e
    bot.add_message(
        translate("score_recalculation_completed", lang=lang)
        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    await bot.send_combined_message()

    return {
        "code": status.HTTP_200_OK,
        "message": translate("scores_recalculated_successfully", lang=lang),
        "data": None,
    }


@router.post("/recalculate-score/{chat_id}")
async def recalculate_score_by_id(
    request: Request,
    chat_id: str,
):
    """
    API tính toán lại điểm số cho chat ID.
    """
    lang = get_request_language(request)
    try:
        async with request.state.postgres_pool as session:
            await handle_chat.detect_knowledge(
                chat_id=chat_id, target_db=session, lang=lang, check_time=1
            )
    except ChatProcessingError as e:
        bot.add_message(f"Custom Error: {e.detail}")
        await bot.send_combined_message()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
    except ValueError as e:
        bot.add_message(f"ValueError: {str(e)}")
        await bot.send_combined_message()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=translate("invalid_request_data", lang=lang),
        ) from e
    except Exception as e:
        error_details = traceback.format_exc()  # Lấy toàn bộ stack trace
        bot.add_message(f"Unexpected Error for chat_id {chat_id}: {error_details}")
        traceback.print_exc()  # In lỗi trực tiếp ra terminal
        await bot.send_combined_message()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=translate("internal_server_error", lang=lang),
        ) from e

    return {
        "code": status.HTTP_200_OK,
        "message": translate("score_recalculated_successfully", lang=lang),
        "data": chat_id,
    }


@router.post("/sync-chat-metadata")
async def sync_chat_metadata(
    request: Request,
):
    """
    API để đồng bộ dữ liệu của tất cả các chat ID
    (chỉ cập nhật total_messages, start_time, finish_time).
    """
    lang = get_request_language(request)
    async with request.state.postgres_pool as session:
        try:
            chat_ids = await session.execute(select(Chat.id)).scalars().all()
        except Exception as e:
            bot.add_message(f"Database error: {str(e)}")
            await bot.send_combined_message()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=translate("database_error", lang=lang),
            ) from e

        processed_results = []
        for chat_id in chat_ids:
            try:
                await handle_chat.chat_metadata(chat_id=chat_id, target_db=session)
                processed_results.append({"chat_id": chat_id, "status": "success"})
            except Exception as e:
                bot.add_message(f"Error processing chat_id {chat_id}: {str(e)}")
                await bot.send_combined_message()
                processed_results.append(
                    {"chat_id": chat_id, "status": "error", "message": str(e)}
                )

    return {
        "code": status.HTTP_200_OK,
        "message": translate("chat_metadata_processed", lang=lang),
        "data": processed_results,
    }


@router.put("/chats/{chat_id}/metadata")
async def update_chat_metadata_api(
    request: Request,
    chat_id: str,
):
    """
    API cập nhật metadata của một chat_id cụ thể.
    """

    lang = get_request_language(request)
    chat_service = HandleChat()  # Khởi tạo dịch vụ xử lý chat
    async with request.state.postgres_pool as session:
        try:
            result = await chat_service.chat_metadata(chat_id, session)
            return {
                "status": "success",
                "message": translate("chat_metadata_updated", lang=lang),
                "data": result,
            }
        except ChatProcessingError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.detail)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=translate("internal_server_error", lang=lang),
            ) from e


@router.post("/handle-chat-data")
async def handle_all_chat_data(
    request: Request, source_db: Session = Depends(get_source_session)
):
    """
    API để đồng bộ dữ liệu của tất cả các chat.
    """
    lang = get_request_language(request)
    bot.add_message(
        "Bắt đầu xử lý dữ liệu chat lúc: "
        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    await bot.send_combined_message()
    async with request.state.postgres_pool as session:
        try:
            errors = await handle_chat.handle_update_all_chat_data(
                target_db=session, source_db=source_db
            )

            if errors:
                for error in errors:
                    err_msg = (
                        "Error in chat_id: "
                        + error["chat_id"]
                        + "\nTraceback: "
                        + error["traceback"]
                    )
                    bot.add_message(err_msg)
                await bot.send_combined_message()

                return {
                    "code": status.HTTP_207_MULTI_STATUS,
                    "message": translate("processed_with_errors", lang=lang),
                    "data": None,
                }
        except Exception as e:
            bot.add_message(f"{str(e)}")
            await bot.send_combined_message()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=translate("internal_server_error", lang=lang),
            ) from e
    bot.add_message(
        "Hoàn thành xử lý dữ liệu chat lúc: "
        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    await bot.send_combined_message()

    return {
        'code': "200",
        'message': "Processed chat metadata",
        'data': None
    }


