"""HandleRateLimit Service"""

import logging
import json
from datetime import datetime
import asyncio
from app.core.config import settings
from ..model.model import Model
from sqlalchemy.sql import text  # type: ignore
from sqlalchemy.orm import Session  # type: ignore


class HandleRateLimit:
    def __init__(self):
        self.default_request_limit = settings.REQUEST_LIMIT_DEFAULT
        self.default_token_limit = settings.TOKEN_LIMT_DEFAULT

    async def get_limit_for_user(self, target_db: Session, user_id: str, model_id: str):
        try:
            stmt = text(
                """
                    SELECT 
                        rate_limit_filter.request_limit,
                        rate_limit_filter.token_limit,
                        rate_limit_filter.reset_hours_value
                    FROM 
                        rate_limit_filter
                    LEFT JOIN 
                        group_user ON group_user.group_id = rate_limit_filter.group_id
                    WHERE 
                        group_user.user_id = :user_id 
                        AND rate_limit_filter.model_id = :model_id
                    """
            )

            result = target_db.execute(
                stmt, {"user_id": user_id, "model_id": model_id}
            ).fetchone()
            if not result:
                default_limit = (
                    target_db.query(Model.default_limit)
                    .filter(Model.id == model_id)
                    .first()
                )

                if not default_limit:
                    return None, None, None
                return (
                    default_limit[0].get("request_limit", self.default_request_limit),
                    default_limit[0].get("token_limit", self.default_token_limit),
                    None,
                )
            return result[0], result[1], result[2]

        except Exception as e:
            logging.error(
                f"Error fetching limits for user {user_id} from {target_db}: {str(e)}"
            )
            return None, None, None
