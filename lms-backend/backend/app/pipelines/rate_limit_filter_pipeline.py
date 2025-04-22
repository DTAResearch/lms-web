import os
from typing import List, Optional
import time
import logging
from datetime import datetime, timezone
import tiktoken  # type: ignore
import httpx  # type: ignore
from pydantic import BaseModel  # type: ignore
from fastapi import HTTPException, status  # type: ignore
from aiocache import cached  # type: ignore


class Pipeline:
    class Valves(BaseModel):
        # List target pipeline ids (models) that this filter will be connected to.
        # If you want to connect this filter to all pipelines, you can set pipelines to ["*"]
        pipelines: List[str] = []

        # Assign a priority level to the filter pipeline.
        # The priority level determines the order in which the filter pipelines are executed.
        # The lower the number, the higher the priority.
        priority: int = 0

        # Valves for rate limiting
        requests_per_day: Optional[int] = None
        tokens_per_day: Optional[int] = None

    def __init__(self):
        # Pipeline filters are only compatible with Open WebUI
        # You can think of filter pipeline as a middleware that can be used to edit the form data before it is sent to the OpenAI API.
        self.type = "filter"

        # Optionally, you can set the id and name of the pipeline.
        # Best practice is to not specify the id so that it can be automatically inferred from the filename, so that users can install multiple versions of the same pipeline.
        # The identifier must be unique across all pipelines.
        # The identifier must be an alphanumeric string that can include underscores or hyphens. It cannot contain spaces, special characters, slashes, or backslashes.
        # self.id = "rate_limit_filter_pipeline"
        self.name = "Rate Limit Filter"

        # Initialize rate limits
        self.valves = self.Valves(
            **{
                "pipelines": os.getenv("RATE_LIMIT_PIPELINES", "*").split(","),
                "requests_per_day": int(os.getenv("RATE_LIMIT_REQUESTS_PER_DAY", 100)),
                "tokens_per_day": int(os.getenv("RATE_LIMIT_TOKENS_PER_DAY", 1000)),
            }
        )

        # Tracking data - user_id -> (timestamps of requests)
        self.user_requests = {}
        self.backend_url = os.getenv("BACKEND_URL")

    async def on_startup(self):
        # This function is called when the server is started.
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        # This function is called when the server is stopped.
        print(f"on_shutdown:{__name__}")
        pass

    def prune_requests(self, user_id: str, model_id: str, start: float):
        """Prune old requests that are outside of the sliding window period."""
        if user_id in self.user_requests:
            self.user_requests[user_id] = [
                req
                for req in self.user_requests[user_id]
                if (not (req["model_id"] == model_id and req["time"] < start))
            ]

    def log_request(
        self, user_id: str, content: str, model_id: str, base_model_id: str
    ):
        """Log a new request for a user."""
        now = time.time()
        tokens = self.cal_token(content=content, model=base_model_id)
        print("token: " + str(tokens))
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []
        self.user_requests[user_id].append(
            {"tokens": tokens, "time": now, "model_id": model_id}
        )

    @staticmethod
    def cal_token(content: str, model: str = "gpt-4o"):
        if not isinstance(content, str) or not content.strip():
            return 0
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(content))

    @cached(ttl=600)
    async def get_limit_and_base_model(self, user_id: str, model_id: str):
        url = self.backend_url + "/rate-limit/user_detail"
        params = {"user_id": user_id, "model_id": model_id}
        headers = {
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=100,
                )
                response.raise_for_status()
                data = response.json()["data"]
                limit_data = data["rate_limit"]
                base_model = data["base_model"]
                return limit_data[0], limit_data[1], limit_data[2], base_model

        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: " + str(e))
            return [
                self.valves.requests_per_day,
                self.valves.tokens_per_day,
                None,
                None,
            ]

    async def rate_limited(self, user_id: str, model_id: str, message: str) -> bool:
        """Check if a user is rate limited."""

        requests_limit, tokens_limit, reset_value_hours, base_model = (
            await self.get_limit_and_base_model(user_id=user_id, model_id=model_id)
        )
        if reset_value_hours is None:
            if (requests_limit is None) or (tokens_limit is None):
                return False
            start = 0
        else:
            now = datetime.now(timezone.utc).timestamp()
            start = now - reset_value_hours * 60 * 60
        self.prune_requests(user_id=user_id, model_id=model_id, start=start)

        user_reqs = self.user_requests.get(user_id, [])

        if (requests_limit is not None) or (tokens_limit is not None):
            requests_last_day = sum(
                1
                for req in user_reqs
                if (int(req["time"]) >= start and req["model_id"] == model_id)
            )
            tokens_last_day = sum(
                req["tokens"]
                for req in user_reqs
                if (int(req["time"]) >= start and req["model_id"] == model_id)
            )
            if requests_last_day >= requests_limit or tokens_last_day >= tokens_limit:
                return True
        self.log_request(
            user_id=user_id,
            content=message,
            model_id=model_id,
            base_model_id=base_model,
        )
        return False

    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        print(f"pipe:{__name__}")
        print(body)
        print(user)
        if user.get("role", "admin") == "user":
            user_id = user["id"] if user and "id" in user else "default_user"
            model_id = body["model"]
            last_content = body["messages"][-1]["content"]
            if await self.rate_limited(
                user_id, model_id=model_id, message=last_content
            ):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later.",
                )

        return body

    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        print(f"pipe:{__name__}")
        print(body)
        print(user)

        # if user.get("role", "admin") == "user":
        #     user_id = user["id"] if user and "id" in user else "default_user"
        #     last_content = body["messages"][-1]["content"]
        #     base_model = await self.get_base_model(model=body["model"])
        #     print("Base: " + base_model)
        #     self.log_request(user_id=user_id, content=last_content, model=base_model)

        return body
