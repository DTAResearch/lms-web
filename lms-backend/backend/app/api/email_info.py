from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import logging
from typing import Optional
from ..db.target_db import get_target_session
from ..services.i18 import translate, get_request_language
from ..constants.email_list import email_list
from ..services.get_email_info import EmailService

# TODO: Tạo class hoặc 1 folder riêng để xử lý lỗi và response
# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def get_email_service(db: Session = Depends(get_target_session)) -> EmailService:
    return EmailService(db)

@router.get("/email-info", response_model=dict)
async def fetch_email_info(
    email: Optional[str] = Query(None, description="Email cần lấy thông tin"),
    email_service: EmailService = Depends(get_email_service)
):
    """Endpoint lấy thông tin email"""
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    logger.info(f"Received request for email: {email}")
    try:
        return email_service.get_email_info(email)
    except HTTPException as e:
        logger.error(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/export-emails-excel")
def export_emails_excel(
    email_service: EmailService = Depends(get_email_service)
):
    """Endpoint xuất file Excel thông tin email"""
    return email_service.export_emails_excel()

@router.get("/export-emails-excel-default")
def export_default_emails_excel(
    email_service: EmailService = Depends(get_email_service)
):
    """Endpoint xuất file Excel cho danh sách email mặc định"""
    return email_service.export_default_emails_excel()
