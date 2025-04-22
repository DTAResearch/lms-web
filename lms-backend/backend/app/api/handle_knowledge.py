from fastapi import APIRouter, UploadFile, File, HTTPException, status as status_code  # type: ignore
from app.schema.chat_response import BaseResponse
from app.services.handle_knowledge import HandleKnowledge
from app.db.target_db import get_target_session
from app.schema.knowledge import RequestCreateKnowledge
from sqlalchemy.orm import Session  # type: ignore
from typing import List

router = APIRouter()
handle_knowledge = HandleKnowledge()


@router.get("", response_model=BaseResponse)
async def get_all_knowledges():
    """
    API lấy thông tin các knowledge.
    """
    try:
        result = await handle_knowledge.get_all_knowledges()
        return {
            "code": str(status_code.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{knowledge_id}", response_model=BaseResponse)
async def get_knowledge(knowledge_id: str):
    """
    API lấy thông tin knowledge theo id.
    """
    try:
        result = await handle_knowledge.get_knowledge_by_id(knowledge_id=knowledge_id)
        return {
            "code": str(status_code.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("", response_model=BaseResponse)
async def create_knowledge(rq_create_data: RequestCreateKnowledge):
    """
    API tạo knowledge.
    """
    try:
        result = await handle_knowledge.create_knowledge(payload=rq_create_data)
        return {
            "code": str(status_code.HTTP_201_CREATED),
            "message": "Successfully",
            "data": result,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/{knowledge_id}", response_model=BaseResponse)
async def update_knowledge(knowledge_id: str, rq_update_data: RequestCreateKnowledge):
    """
    API tạo knowledge.
    """
    try:
        result = await handle_knowledge.update_knowledge(
            knowledge_id=knowledge_id, payload=rq_update_data
        )
        return {
            "code": str(status_code.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/{knowledge_id}", response_model=BaseResponse)
async def delete_knowledge(knowledge_id: str):
    """
    API xóa knowledge.
    """
    try:
        result = await handle_knowledge.delete_knowledge(knowledge_id=knowledge_id)
        return {
            "code": str(status_code.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/{knowledge_id}/attachments", response_model=BaseResponse)
async def upload_files(knowledge_id: str, files: List[UploadFile] = File(...)):
    """
    API thêm file vào knowledge.
    """
    try:
        result = await handle_knowledge.upload_file(
            knowledge_id=knowledge_id, files=files
        )
        return {
            "code": str(status_code.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/{knowledge_id}/attachments/{file_id}", response_model=BaseResponse)
async def upload_files(knowledge_id: str, file_id: str):
    """
    API xóa file khỏi knowledge.
    """
    try:
        result = await handle_knowledge.remove_file(
            knowledge_id=knowledge_id, file_id=file_id
        )
        return {
            "code": str(status_code.HTTP_200_OK),
            "message": "Successfully",
            "data": result,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
