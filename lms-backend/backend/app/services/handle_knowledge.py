from datetime import datetime
import logging
import asyncio
import json
from app.core.config import settings
from app.schema.knowledge import RequestCreateKnowledge
import httpx  # type: ignore
from fastapi import HTTPException, UploadFile  # type: ignore
from typing import List


class HandleKnowledge:

    def __init__(self):
        """Initialize the handle group"""
        self.token = settings.HOC_TIEP_KEY
        self.retries = settings.MAX_RETRIES
        self.hoc_tiep_be_url = settings.HOC_TIEP_BE_URL

    def __get_headers(self):
        """Get the headers"""
        return {
            "Authorization": "Bearer " + self.token,
            "Accept": "application/json",
        }

    async def get_all_knowledges(self):
        headers = self.__get_headers()
        url = self.hoc_tiep_be_url + "/api/v1/knowledge/"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=100)
                response.raise_for_status()
                knowledges = response.json()
                return knowledges
        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: ", e)

    async def get_knowledge_by_id(self, knowledge_id: str):
        headers = self.__get_headers()
        url = self.hoc_tiep_be_url + "/api/v1/knowledge/" + knowledge_id

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=100)
                response.raise_for_status()
                knowledge = response.json()
                return knowledge
        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: ", e)

    async def create_knowledge(self, payload: RequestCreateKnowledge):
        headers = self.__get_headers()
        url = self.hoc_tiep_be_url + "/api/v1/knowledge/create"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json=payload.dict(), headers=headers, timeout=100
                )
                response.raise_for_status()
                if response.status_code != 200:
                    raise HTTPException(status_code=400, detail=str(response.text))
                knowledge = response.json()
                return knowledge
        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: ", e)

    async def update_knowledge(
        self, knowledge_id: str, payload: RequestCreateKnowledge
    ):
        headers = self.__get_headers()
        url = self.hoc_tiep_be_url + "/api/v1/knowledge/" + knowledge_id + "/update"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json=payload.dict(), headers=headers, timeout=100
                )
                response.raise_for_status()
                if response.status_code != 200:
                    raise HTTPException(status_code=400, detail=str(response.text))
                knowledge = response.json()
                return knowledge
        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: ", e)

    async def delete_knowledge(self, knowledge_id: str):
        headers = self.__get_headers()
        url = self.hoc_tiep_be_url + "/api/v1/knowledge/" + knowledge_id + "/delete"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(url, headers=headers, timeout=100)
                response.raise_for_status()
                if response.status_code != 200:
                    raise HTTPException(status_code=400, detail=str(response.text))
                result = response.json()
                return result
        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: ", e)

    async def process_file(
        self,
        file: UploadFile,
        client: httpx.AsyncClient,
        headers: dict,
        upload_url: str,
        add_file_url: str,
    ) -> dict:
        """
        Xử lý một file: tải lên OpenWebUI và thêm vào bộ sưu tập kiến thức.
        """
        try:
            # upload file
            file_content = await file.read()
            files_payload = {"file": (file.filename, file_content, file.content_type)}

            response = await client.post(
                upload_url, headers=headers, files=files_payload, timeout=100
            )
            response.raise_for_status()
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=str(response.text))

            file_id = response.json().get("id")
            if not file_id:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to get file_id for {file.filename}",
                )

            add_payload = {"file_id": file_id}
            add_response = await client.post(
                add_file_url, json=add_payload, headers=headers, timeout=100
            )
            add_response.raise_for_status()

            if add_response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to add "
                    + file.filename
                    + " to knowledge base: "
                    + add_response.texts,
                )

            return {"filename": file.filename, "file_id": file_id}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="Error processing " + file.filename + str(e)
            )

    async def upload_file(self, knowledge_id: str, files: List[UploadFile]) -> dict:
        headers = self.__get_headers()
        upload_url = self.hoc_tiep_be_url + "/api/v1/files/"
        add_file_url = (
            self.hoc_tiep_be_url + "/api/v1/knowledge/" + knowledge_id + "/file/add"
        )

        try:
            uploaded_files = []
            async with httpx.AsyncClient() as client:
                for file in files:

                    file_data = await self.process_file(
                        file=file,
                        client=client,
                        headers=headers,
                        upload_url=upload_url,
                        add_file_url=add_file_url,
                    )
                    uploaded_files.append(file_data)
                    await asyncio.sleep(0.5)

            return uploaded_files
        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: ", e)

    async def remove_file(self, knowledge_id: str, file_id: str):
        headers = self.__get_headers()
        url = (
            self.hoc_tiep_be_url + "/api/v1/knowledge/" + knowledge_id + "/file/remove"
        )
        payload = {"file_id": file_id}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json=payload, headers=headers, timeout=100
                )
                response.raise_for_status()
                if response.status_code != 200:
                    raise HTTPException(status_code=400, detail=str(response.text))
                result = response.json()
                return result

        except httpx.HTTPStatusError as http_err:
            logging.error(
                "Lỗi HTTP: "
                + str(http_err.response.status_code)
                + " - "
                + http_err.response.text
            )
        except Exception as e:
            logging.error("An error occurred: ", e)
