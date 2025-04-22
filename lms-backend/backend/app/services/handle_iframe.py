import time
import jwt
from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from app.core.config import settings
from app.model.group_user import GroupUser
from app.model.user import User
from app.constants.roles import Role
from app.model.group import Group
class IframeService:
    @staticmethod
    def generate_token(
        dashboard_id: int,
        params: Optional[Dict] = None,
        expiration_minutes: Optional[int] = None
    ) -> str:
        """Generate JWT token for Metabase embedding"""
        minutes = expiration_minutes or settings.TIME_EXPIRATION
        exp = time.time() + minutes * 60  # chuyển phút sang giây
        
        payload = {
            "resource": {"dashboard": dashboard_id},
            "params": params or {},
            "exp": round(exp)
        }
        
        return jwt.encode(payload, settings.METABASE_SECRET_KEY, algorithm="HS256")

    @staticmethod
    def get_user_groups(db: Session, user_id: str) -> List[str]:
        """Get list of group IDs for a user"""
        groups = db.query(GroupUser.group_id).filter(
            GroupUser.user_id == user_id
        ).all()
        return [g.group_id for g in groups if g.group_id]
    
    @staticmethod
    def get_teacher_groups(db: Session, user_id: str) -> List[str]:
        """Lấy danh sách group_id nếu người dùng là giáo viên"""
        user = db.query(User).filter(User.id == user_id).first()

        if user and user.role == Role.TEACHER.value:
            groups = db.query(GroupUser.group_id).filter(
                GroupUser.user_id == user_id
            ).all()
            return [g.group_id for g in groups if g.group_id]
        
        return []

    @staticmethod
    def get_admin_groups(db: Session) -> List[str]:
        """Lấy tất cả nhóm cho admin"""
        groups = db.query(Group.id).distinct().all()
        return [g.id for g in groups if g.id]

    @staticmethod
    def build_iframe_url(token: str, extra_params: Optional[Dict] = None) -> str:
        """Construct the final iframe URL"""
        base_url = f"{settings.METABASE_SITE_URL}/embed/dashboard/{token}"
        query_string = "#bordered=true&titled=false"
        
        if extra_params:
            for key, value in extra_params.items():
                if isinstance(value, list):
                    for item in value:
                        query_string += f"&{key}={item}" if item else ""
                else:
                    query_string += f"&{key}={value}"
                    
        return base_url + query_string

    def get_admin_dashboard_url(self, user_id: str, groups: List[str]) -> str:
        token = self.generate_token(
            dashboard_id=settings.ADMIN_DASHBOARD_ID,
            params={
                "user_id": user_id,  "groups": groups
                
            }
        )
        url = self.build_iframe_url(
            token,
            {
            }
        )
        print(f"[ADMIN DASHBOARD URL] {url}")
        return url

    def get_teacher_dashboard_url(self, db: Session, user_id: str, custom_groups: Optional[List[str]] = None) -> str:
        groups = custom_groups or self.get_teacher_groups(db, user_id)
        if not groups:
            groups = []
        
        token = self.generate_token(
            dashboard_id=settings.TEACHER_DASHBOARD_ID,
            params={"user_id": user_id, "groups": groups}
        )
# day
        return self.build_iframe_url(
            token,
            {
       
            }
        )

    def get_student_dashboard_url(self, db: Session, user_id: str, custom_groups: Optional[List[str]] = None) -> str:
        groups = custom_groups or self.get_user_groups(db, user_id)
        token = self.generate_token(
            dashboard_id=settings.STUDENT_DASHBOARD_ID,
            params={ "user_id": user_id,  "groups": groups}
        )

        return self.build_iframe_url(
            token,
            {
            }
        )

    def get_group_stats_url(self, db: Session, user_id: str, role: str, group_id: str) -> str:
        """Get group statistics dashboard URL"""

        # Generate token and URL
        token = self.generate_token(
            settings.GROUP_STATS_DASHBOARD_ID,
            {"groups": [group_id]}
        )
        return self.build_iframe_url(token, {"groups": [group_id]})
    
    # backend\app\services\handle_iframe.py
    def get_teacher_dashboard_by_group(self, user_id: str) -> str:
        """Get teacher dashboard URL for a specific group without user authentication"""
       
        
        # Generate token with group_id as param
        token = self.generate_token(
            settings.TEACHER_DASHBOARD_ID,
            {"user_id": user_id}  
        )
        
        # Build URL with group_id as query param
        url = self.build_iframe_url(
            token,
           {"user_id": user_id}  
        )
        
        print(f"[TEACHER DASHBOARD BY GROUP URL] {url}")
        return url