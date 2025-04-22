"""
    Service handle_chat:
        Thực hiện việc chấm điểm và lấy thông tin cơ bản cho các đoạn chat

"""

import traceback
import time
import json
import os
import asyncio
import logging
from typing import List
import httpx  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from sqlalchemy.sql import text  # type: ignore
from sqlalchemy.exc import StatementError, OperationalError # type: ignore
from sqlalchemy import select # type: ignore
from fastapi import HTTPException  # type: ignore

from ..model.chat import Chat
from ..model.model import Model
from ..core.config import settings
from ..services.i18 import translate
from ..exceptions.custom_exceptions import ChatProcessingError

logging.basicConfig(level=logging.INFO)


class HandleChat:
    """
    Lớp HandleChat được sử dụng để chấm điểm và lấy thông tin cơ bản đoạn chat.
    """

    def __init__(self):
        self.token = self.get_token_hoctiep()

    @staticmethod
    def check_is_question(content):
        """Check if a question

        Args:
            content (str): String

        Returns:
            Boolean:  true if the content is a question
        """
        return bool(content)

    @staticmethod
    def get_token_hoctiep():
        """Get the token of hoctiep

        Returns:
            str: _description_
        """
        return settings.HOC_TIEP_KEY

    # Get question and answer
    def get_list_qa(self, chat_messages, check_time: float):
        """Get list of questions and answers

        Args:
            chat_messages (dict): detail of chat
            check_time (float): timestamp of time excute handle chat

        Returns:
            _type_: _description_
        """
        qas = []
        questions = []
        if check_time == 0:
            check_time = int(time.time())
        for index, message in enumerate(chat_messages):
            if check_time - message.get("timestamp", 0) > 30 * 60:
                continue
            if message["role"] != "assistant":
                parent_id = message.get("parentId")
                if parent_id is not None:
                    for question in questions:
                        if parent_id == question["id"]:
                            qas.append(
                                {
                                    "question": question["content"],
                                    "answer": message["content"],
                                    "model_consideration": (chat_messages[index + 1][
                                        "content"
                                    ]) if index + 1 != len(chat_messages) else None
                                }
                            )
                            break
                continue
            if self.check_is_question(message["content"]):
                questions.append(message)
        return qas

    @staticmethod
    def format_prompt(prompt: str):
        """Format a prompt

        Args:
            prompt (str): content sent to hoctiep

        Returns:
            str: formatted prompt
        """
        return prompt

    def get_examples_qa_rq(self):
        """Examples of request

        Returns:
            str: string of array of examples
        """
        current_dir = os.path.dirname(__file__)
        examples_file = os.path.join(
            current_dir, "../constants/handle_chat_examples.json"
        )

        try:
            if os.path.isfile(examples_file):
                with open(examples_file, "r", encoding="utf-8") as f:
                    examples = json.load(f)
            else:
                print(f"File {examples_file} not found.")
                examples = []
        except FileNotFoundError:
            logging.warning(f"File {examples_file} not found.")
            examples = []
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON format in {examples_file}.")
            examples = []
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            examples = []

        examples_str = "Examples:\n"
        for i, example in enumerate(examples, start=1):
            examples_str += (
                f"{i}. Question: \"{example['question']}\"\n"
                f"   Answer: \"{example['answer']}\"\n"
                f"   is_request: {str(example['is_request']).lower()}\n\n"
            )

        return examples_str

    @staticmethod
    def split_chunks(qas):
        """Split a list of questions and answers

        Args:
            qas (array): list of questions and answers

        Returns:
            array: list of list questions and answers
        """
        if not qas:
            return []
        chunk_size = 10
        return [qas[i : i + chunk_size] for i in range(0, len(qas), chunk_size)]

    def get_prompts_from_chunks(self, chunks, meta_tag):
        """Get prompt strings

        Args:
            chunks (array): list of questions and answers
            meta_tag (array): meta

        Returns:
            str: prompt strings
        """
        prompts = []
        for chunk in chunks:
            prompt = self.get_prompt_analysis_qa(chunk, meta_tag)
            prompts.append(prompt)
        return prompts

    async def process_prompt(self, prompt, chat_model):
        """Call hoctiep for 1 prompt

        Args:
            prompt (str): prompt
            chat_model (str): name of model

        Returns:
            json: array of list responses
        """
        response = await self.get_handled_output(prompt, chat_model)
        logging.info(response)
        return self.convert_json(response)

    async def process_all_prompts(self, prompts, chat_model):
        """Call process for all prompts

        Args:
            prompts (str): prompts
            chat_model (str): model name

        Returns:
            array: array of responses for 1 chat
        """
        if not prompts:
            return []
        tasks = [self.process_prompt(prompt, chat_model) for prompt in prompts]
        results = await asyncio.gather(*tasks)
        flattened_results = [
            obj for result in results if result is not None for obj in result
        ]
        return flattened_results

    def get_prompt_analysis_qa(self, ques_ans_list, meta):
        """Make prompt

        Args:
            ques_ans_list (array): list of qas
            meta (arr): array of meta

        Returns:
            str: prompt string
        """
        examples_str = self.get_examples_qa_rq()

        prompt = (
        "Analyze the provided question, answer and model_consideration"
        " and return ONLY an array of objects in JSON format as described below:\n"
        "{\n"
        '  "is_request": <boolean>,\n'
        '  "meta": ["<text>", "<text>", ...],\n'
        '  "level": <number>,\n'
        '  "accuracy": <number>,\n'
        '  "completeness": <number>\n'
        "}\n"
        "Important Requirements:\n"
        "- Always return a **single, complete JSON array** with all objects.\n"
        "- For multiple-choice questions,"
        " if the answer is correct, set 'completeness' to 100.\n"
        "- Do not truncate the array or omit any objects."
        " Return all question-answer pairs in a single response.\n"
        "- If the output is incomplete,"
        " repeat the entire array instead of returning partial data.\n"
        '- If the "model consideration" section has an answer score,'
        " set the score relative to the maximum score for accuracy and completeness.\n"
        "- If there is no explicit score,"
        " analyze the quality of the answer to set 'accuracy' and 'completeness' values.\n"
        "Field Descriptions:\n"
        "- is_request: Boolean, true if the question is a direct inquiry requesting specific"
        " information, explanation, or action, and the answer directly addresses it."
        " If the question is a greeting, social interaction, or open-ended prompt"
        " without clear intent to request information, set 'is_request' to false."
        " If the answer refuses to answer the question , set 'is_request' to false."
        ' Additionally,'
        ' if the question is rhetorical, vague, or does not expect a direct, factual response'
        ' (e.g., "How are you?" or "Can you tell me your level of expertise?"),'
        ' set \'is_request\' to false.'
        " Otherwise, if the answer is a direct response to a clear inquiry,"
        " set 'is_request' to true.\n"
        " Otherwise, false.\n"
        "- meta: Array of strings from meta_input,"
        " containing contextual metadata for the question-answer pair."
        " If the question and the answer are related to user personal information"
        " (such as education level, age, gender, location, preferences, or similar),"
        " set 'meta' to an empty array []."
        " Otherwise, populate it with relevant metadata from meta_input."
        "- level: Numerical difficulty of the question (1: Easy, 2: Medium, 3: Difficult).\n"
        "- accuracy: Score (from 0 to 100)"
        " assessing how well the answer addresses the question.\n"
        "- completeness: Score (from 0 to 100) indicating the comprehensiveness of the answer."
        "\nEvaluation Criteria:\n"
        "- For 'is_request',"
        " questions that are greetings, conversational prompts, or rhetorical in nature"
        " (e.g., \"How can I help you?\" or \"What do you want to learn today?\")"
        " should have 'is_request' set to false.\n"
        "- Base evaluations on semantic understanding, logical analysis, and coherence.\n"
        "- Use 'model_consideration' to analyze and set the accuracy and completeness.\n"
        "- If the answer contains a score (e.g., 'Your score is 8/10', 'Soccer: 4/5',...),"
        " convert it to a percentage on a scale of 100 (e.g., 80 for 8/10).\n"
        "- Consider if the answer is logical, coherent, and contextually relevant to the question."
        f"\n{examples_str}\n"
        "Input Data:\n"
        )

        input_data = {"meta_input": meta, "questions_answers": ques_ans_list}
        prompt += json.dumps(input_data, ensure_ascii=False, indent=2)

        return self.format_prompt(prompt)

    async def get_handled_output(self, prompt, model):
        """Call llm to get response

        Args:
            prompt (str): prompt string
            model (str): model name

        Returns:
            str: response string or None
        """
        # hoctiep
        hoc_tiep_url = "https://chat.hoctiep.com/api/chat/completions"
        # payload
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "files": [],
        }

        headers = {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json",
        }

        retry_attempts = 3

        for attempt in range(retry_attempts):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        hoc_tiep_url, json=payload, headers=headers, timeout=300
                    )
                    response.raise_for_status()  # Kiểm tra lỗi HTTP
                    data = response.json()
                    result = (
                        data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                    )
                    return result  # Trả về kết quả nếu thành công

            except Exception as e:
                logging.error("An error occurred: ", e)
                logging.error("Attempt " + attempt + 1 + "/" + retry_attempts + "...")
                if attempt + 1 == retry_attempts:
                    return None
                await asyncio.sleep(2)
        return None

    @staticmethod
    def convert_json(string):
        """Convert a JSON string

        Args:
            string (str): string to convert

        Returns:
            array: arr
        """
        if string is not None:
            formatted_output = string.strip("\n").strip("`").strip("json\n")
            return json.loads(formatted_output)
        return None

    @staticmethod
    def get_questions(analyzed_output):
        """Get the questions

        Args:
            analyzed_output (array): array of responses

        Returns:
            array: array of questions
        """
        if analyzed_output is None:
            return []
        return [
            item
            for item in analyzed_output
            if item.get("is_request")
        ]

    @staticmethod
    def get_score_info_from_qa(analyzed_qa):
        """Get score info from list of responses"""
        return {
            "accuracy": analyzed_qa.get("accuracy"),
            "completeness": analyzed_qa.get("completeness"),
            "level": analyzed_qa.get("level"),
        }

    @staticmethod
    def get_overall_score_for_meta(scores):
        """Get the overall score"""
        if not scores:
            return None
        total_score = sum(
            ((score["accuracy"] * 0.7 + score["completeness"] * 0.3) * score["level"])
            for score in scores
        )
        total_level = sum(score["level"] for score in scores)
        return {"score": total_score / total_level, "levels": total_level}

    def handle_analysis_meta(self, analyzed_qas, meta_tag):
        """Split response into meta"""
        meta_general = [
            {"meta": meta, "items": [], "scores": [], "levels": 0} for meta in meta_tag
        ]
        for qa in analyzed_qas:
            score = self.get_score_info_from_qa(qa)
            for meta in meta_general:
                if meta.get("meta") in qa.get("meta"):
                    meta["items"].append(qa)
                    meta["scores"].append(score)

        result = []
        for meta in meta_general:
            score_info = self.get_overall_score_for_meta(meta["scores"])
            if score_info:
                result.append(
                    {
                        "meta": meta["meta"],
                        "total_score": score_info["score"],
                        "levels": score_info["levels"],
                    }
                )
        return result

    def distribute_analyzed_output(self, analyzed_output, meta_tag):
        """Get score for each meta"""
        analyzed_qas = self.get_questions(analyzed_output)
        return self.handle_analysis_meta(analyzed_qas, meta_tag)

    @staticmethod
    def safe_json_loads(data):
        """Giải mã JSON nhiều lần nếu bị bọc quá nhiều lớp"""
        while isinstance(data, str):
            try:
                data = json.loads(data)  # Thử giải mã JSON
            except json.JSONDecodeError:
                continue  # Nếu lỗi, dừng lại vì đây không phải JSON hợp lệ
            # To do can xu ly them
        return data

    @staticmethod
    def get_total_result_by_results(results):
        """Get the total results"""
        total_levels = sum(item.get("levels") for item in results)
        total_result = 0
        if total_levels != 0:
            total_result = (
                sum(item.get("levels") * item.get("total_score") for item in results)
                / total_levels
            )
        return total_result

    @staticmethod
    def merge_results(old_result, new_result):
        """Merge new results and old results"""
        final_results = []
        for old_rs in old_result:
            meta = old_rs["meta"]
            score = old_rs["total_score"]
            levels = old_rs["levels"]
            for nw_rs in new_result:
                if nw_rs["meta"] == meta:
                    levels = old_rs["levels"] + nw_rs["levels"]
                    score = (
                        old_rs["total_score"] * old_rs["levels"]
                        + nw_rs["total_score"] * nw_rs["levels"]
                    ) / levels
                    break
            final_results.append({"meta": meta, "total_score": score, "levels": levels})

        existing_meta = {rs["meta"] for rs in final_results}
        for nw_rs in new_result:
            if nw_rs["meta"] not in existing_meta:
                final_results.append(nw_rs)
        return final_results

    async def update_to_target_db(
        self, target_db: AsyncSession, data: dict, check_time: float
    ):
        """Update the target"""
        try:

            # Sử dụng `text()` và `Session.execute()` cho truy vấn SELECT
            result = await target_db.execute(
                text("SELECT id, result FROM chat WHERE id = :chat_id"),
                {"chat_id": data["chat_id"]},
            )
            row = result.fetchone()
            chat_id = row[0]
            cur_result = row[1] if check_time != 1 else []
            if chat_id:
                old_result = cur_result if cur_result is not None else []
                new_result = data["result"]
                merged_result = self.merge_results(old_result, new_result)
                total_result = self.get_total_result_by_results(merged_result)
                await target_db.execute(
                    text(
                        """
                    UPDATE chat
                    SET 
                        updated_at = :updated_at,
                        total_messages = :total_messages,
                        result = :result,
                        total_result = :total_result,
                        start_time = :start_time,
                        finish_time = :finish_time
                    WHERE id = :chat_id
                    """
                    ),
                    {
                        "chat_id": data["chat_id"],
                        "updated_at": data["updated_at"],
                        "total_messages": data["total_messages"],
                        "result": json.dumps(merged_result, ensure_ascii=False),
                        "total_result": total_result,
                        "start_time": data["start_time"],
                        "finish_time": data["finish_time"],
                    },
                )
                print(
                    "Updating chat_id " + data['chat_id'] + " with result: " + json.dumps(merged_result, ensure_ascii=False)
                )
            else:
                print("Chat record not found, skipping update.")

            # Commit transaction
            await target_db.commit()
            return {"status": "success", "message": "Data updated successfully"}
        except StatementError as e:
            await target_db.rollback()
            logging.error("SQL statement error: ", e)

        except OperationalError as e:
            await target_db.rollback()
            logging.error("Database connection error: ", e)
            return {"status": "error", "message": "Database connection error"}

        except Exception as e:
            # Rollback transaction in case of an error
            await target_db.rollback()
            print("An error occurred: ", str(e))
            return {"status": "error", "message": str(e)}

    async def detect_knowledge(
        self,
        chat_id: str,
        target_db: AsyncSession,
        lang,
        check_time: float = 0,
        active_models: List[str] = None,
    ):
        """Handle chat to get score"""
        # Lấy thông tin chat từ database
        chat_exists = await target_db.execute(select(Chat).filter(Chat.id == chat_id))
        chat = chat_exists.scalars().first()
        if not chat:
            raise ChatProcessingError(
                chat_id, translate("chat_id_not_found", lang=lang)
            )
        if not chat:
            logging.warning("No chat content in chat_id: " + chat_id)
            return

        try:
            # Lấy nội dung chat và
            chat_content = chat.chat
            chat_meta = chat.meta

            # Kiểm tra nếu chat_meta không tồn tại
            if not chat_meta:
                logging.warning("No chat_meta in chat_id: " + chat_id)
                return

            # Xử lý chat_meta nếu nó là chuỗi JSON
            if isinstance(chat_meta, str):
                try:
                    chat_meta = json.loads(
                        chat_meta
                    )  # Chuyển chuỗi JSON thành dictionary
                except json.JSONDecodeError:
                    logging.error("Invalid meta format: Not a valid JSON string")
                    return

            # Kiểm tra lại nếu chat_meta không phải là dictionary
            if not isinstance(chat_meta, dict):
                logging.warning("Chat_meta is wrong type in chat_id:" + chat_id)
                return

            # Xử lý chat_content
            chat_content = self.safe_json_loads(chat_content)

            # Kiểm tra nếu chat_content không phải là dictionary
            if not isinstance(chat_content, dict):
                logging.error(
                    "Chat_content is not a dictionary with chat_id:" + chat_id
                )
                return

            # Lấy các giá trị từ chat_meta và chat_content
            meta_tag = chat_meta.get("tags", [])
            chat_messages = chat_content.get("messages", None)
            # Kiểm tra nếu không có tin nhắn trong chat
            if chat_messages is None:
                logging.error("No chat messages with chat_id:" + chat_id)
                return

            # Xử lý tin nhắn để tạo danh sách câu hỏi và câu trả lời
            ques_ans_list = self.get_list_qa(chat_messages, check_time=check_time)
            chunks = self.split_chunks(ques_ans_list)
            prompts = self.get_prompts_from_chunks(chunks, meta_tag)
            # Xử lý chat_model (đảm bảo chat_content là dictionary trước khi gọi .get())
            chat_model = chat_content.get("models", [None])[0]
            # Lấy danh sách các model đang hoạt động nếu không được cung cấp
            if not active_models:
                active_models = await self.get_active_models(target_db)
            # Kiểm tra nếu chat_model không nằm trong danh sách active_models
            if chat_model not in active_models:
                logging.error(
                    "Chat model " + chat_model + " not enabled in chat_id: " + chat_id
                )
                return

            # Xử lý các prompts và phân tích kết quả
            analysis_output = await self.process_all_prompts(prompts, chat_model)
            result = self.distribute_analyzed_output(analysis_output, meta_tag)

            if not result:
                return
            start_time = chat_messages[0].get("timestamp", 0) if chat_messages else None
            finish_time = (
                chat_messages[-1].get("timestamp", 0) if chat_messages else None
            )
            # Chuẩn bị dữ liệu để cập nhật vào database
            update_data = {
                "chat_id": chat_id,
                "updated_at": chat_messages[-1].get("timestamp", 0),
                "total_messages": len(chat_messages),
                "result": result,
                "start_time": start_time,
                "finish_time": finish_time,
            }
            # Cập nhật dữ liệu vào database
            await self.update_to_target_db(
                target_db, update_data, check_time=check_time
            )
        except Exception as e:
            logging.error("Chat " + chat_id + ": Unexpected error - " + str(e))

    async def get_active_models(self, target_db: AsyncSession):
        """Get active models"""
        result = await target_db.execute(
            select(Model.id).where(Model.is_active == True)
        )
        model_ids = [row[0] for row in result.fetchall()]
        return model_ids

    async def update_chat_metadata(
        self,
        target_db: AsyncSession,
        chat_id: str,
        total_messages: int,
        start_time: str,
        finish_time: str,
        chat_model: str,
    ):
        """
        Cập nhật chỉ ba cột: total_messages, start_time, finish_time vào DB.
        """
        try:
            result = await target_db.execute(
                text("SELECT id FROM chat WHERE id = :chat_id"), {"chat_id": chat_id}
            )
            existing_record = result.fetchone()

            if existing_record:
                await target_db.execute(
                    text(
                        """
                    UPDATE chat
                    SET 
                        total_messages = :total_messages,
                        start_time = :start_time,
                        finish_time = :finish_time,
                        model = :model
                    WHERE id = :chat_id
                    """
                    ),
                    {
                        "chat_id": chat_id,
                        "total_messages": total_messages,
                        "start_time": start_time,
                        "finish_time": finish_time,
                        "model": chat_model,
                    },
                )
                await target_db.commit()
                print(
                    f"✅ Cập nhật thành công chat_id {chat_id}: "
                    + "total_messages={total_messages}, "
                    + "start_time={start_time}, "
                    + "finish_time={finish_time}, "
                    + "model={chat_model}"
                )
                return {"status": "success", "message": f"Updated chat_id {chat_id}"}
            else:
                print(f"⚠️ Chat {chat_id} không tồn tại.")
                return {"status": "error", "message": f"Chat {chat_id} not found"}
        except Exception as e:
            await target_db.rollback()
            print(f"❌ Lỗi khi cập nhật chat_id {chat_id}: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def chat_metadata(
        self, chat_id: str, target_db: AsyncSession, check_time: float = 0
    ):
        """
        Phân tích dữ liệu chat và cập nhật chỉ các cột total_messages, start_time, finish_time.
        """
        result = await target_db.execute(
            select(Chat).where(Chat.id == chat_id)
        )
        chat = result.scalar_one_or_none()

        if not chat:
            raise HTTPException(status_code=404, detail=f"Chat {chat_id} not found")

        if check_time - chat.updated_at > 60 * 60 * 24:
            logging.info("No metadata updates in chat_id: " + chat_id)
            return

        try:
            chat_content = self.safe_json_loads(chat.chat)

            if not isinstance(chat_content, dict):
                logging.error("Invalid chat content format")
                return

            chat_messages = chat_content.get("messages", [])
            if not chat_messages:
                raise HTTPException(status_code=400, detail="No chat messages found")

            # Xử lý chat_model (đảm bảo chat_content là dictionary trước khi gọi .get())
            chat_model = chat_content.get("models", [None])[0]
            print("chat_model:", chat_model, type(chat_model))

            # Lấy thông tin cần cập nhật
            total_messages = len(chat_messages)
            # Kiểm tra dữ liệu của tin nhắn đầu tiên và cuối cùng
            first_message = chat_messages[0] if chat_messages else None
            last_message = chat_messages[-1] if chat_messages else None

            # # In log dữ liệu tin nhắn đầu và cuối

            start_time = first_message.get("timestamp", 0) if first_message else None
            finish_time = last_message.get("timestamp", 0) if last_message else None

            # Kiểm tra giá trị start_time và finish_time
            logging.info(
                f"Chat {chat_id}: Start Time -> {start_time}, Finish Time -> {finish_time}"
            )
            # Gọi hàm cập nhật ba cột
            await self.update_chat_metadata(
                target_db, chat_id, total_messages, start_time, finish_time, chat_model
            )

        except Exception as e:
            raise ValueError(f"Chat {chat_id}: Unexpected error - {str(e)}") from e

    async def handle_score_all(self, target_db: AsyncSession, source_db: Session, check_time: float, lang):
        """Score all chat"""
        if source_db is None:
            chat_ids = await target_db.execute(select(Chat.id)).scalars().all()
        else:
            delta_time_epoch = int(check_time - 86400)  # Lấy dữ liệu trong 24 giờ qua
            chat_ids = fetch_recent_chat_ids(source_db, last_id="0", delta_time_epoch=delta_time_epoch)

        if not chat_ids:
            return []  # Không có dữ liệu cập nhật
        active_models = await self.get_active_models(target_db)
        batch_size_handle_chat = settings.BATCH_HANDLE_CHAT
        # chat_ids = [chat_id[0] for chat_id in target_db.query(Chat.id).all()]
        chunks = [
            chat_ids[i : i + batch_size_handle_chat]
            for i in range(0, len(chat_ids), batch_size_handle_chat)
        ]

        errors = []
        for chunk in chunks:
            results = await asyncio.gather(
                *[
                    self.detect_knowledge(
                        chat_id=chat_id,
                        target_db=target_db,
                        lang=lang,
                        check_time=check_time,
                        active_models=active_models,
                    )
                    for chat_id in chunk
                ],
                return_exceptions=True,
            )

            for chat_id, result in zip(chunk, results):
                if isinstance(result, Exception):
                    error_details = traceback.format_exc()
                    errors.append(
                        {
                            "chat_id": chat_id,
                            "error": str(result),
                            "traceback": error_details,
                        }
                    )

        return errors

    async def handle_update_all_meta(self, target_db: AsyncSession,source_db: Session, check_time: float):
        """Handle updating meta information"""
        # chat_ids = [chat_id[0] for chat_id in target_db.query(Chat.id).all()]
        delta_time_epoch = int(check_time - 86400)
        chat_ids = fetch_recent_chat_ids(source_db, last_id="0", delta_time_epoch=delta_time_epoch)

        if not chat_ids:
            return []
        batch_size_handle_chat = settings.BATCH_HANDLE_CHAT
        chunks = [
            chat_ids[i : i + batch_size_handle_chat]
            for i in range(0, len(chat_ids), batch_size_handle_chat)
        ]

        errors = []
        for chunk in chunks:
            results = await asyncio.gather(
                *[
                    self.chat_metadata(
                        chat_id=chat_id, target_db=target_db, check_time=check_time
                    )
                    for chat_id in chunk
                ],
                return_exceptions=True,
            )

            for chat_id, result in zip(chunk, results):
                if isinstance(result, Exception):
                    error_details = traceback.format_exc()
                    errors.append(
                        {
                            "chat_id": chat_id,
                            "error": str(result),
                            "traceback": error_details,
                        }
                    )

        return errors

    async def handle_update_all_chat_data(self, target_db: AsyncSession, source_db: Session):
        """Update score and metadata"""
        check_time = time.time()
        tasks = [
            asyncio.create_task(
                self.handle_update_all_meta(target_db=target_db,source_db=source_db, check_time=check_time)
            ),
            asyncio.create_task(
                self.handle_score_all(target_db=target_db, source_db=source_db, check_time=check_time)
            ),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        errors = []
        for result in results:
            if isinstance(result, list):
                errors.extend(result)

        return errors

def fetch_recent_chat_ids(session: Session, last_id: str, delta_time_epoch: int) -> List[int]:
    """Lấy danh sách chat_id được cập nhật mới nhất trong ngày"""
    query = (
        select(Chat.id)
        .where(Chat.id > last_id)
        .where(Chat.updated_at >= delta_time_epoch)
        .order_by(Chat.id)
    )
    result = session.execute(query).fetchall()
    return [row[0] for row in result]  # Trả về danh sách chat_id