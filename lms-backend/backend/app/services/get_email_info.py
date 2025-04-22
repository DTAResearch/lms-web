from sqlalchemy.orm import Session
from fastapi import HTTPException, Response
from sqlalchemy import func
import logging
from typing import List, Dict, Optional
from ..model.user import User
from ..model.chat import Chat
from ..constants.email_list import email_list
import json
import pandas as pd
from io import BytesIO

# # Thiết lập logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

class EmailService:
    """Class xử lý thông ti logic liên quan đến email """

    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Lấy thông tin user từ database theo email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_chat_details(self, user_id: int) -> tuple[int, int, List[Dict[str, str]]]:
        """Lấy danh sách chat và đếm số cuộc hội thoại"""
        chats = self.db.query(Chat).filter(Chat.user_id == user_id).all()
        chat_count = len(chats)
        total_message_count = 0
        chat_details = []

        for chat in chats:
            chat_data = chat.chat
            if isinstance(chat_data, str):
                try:
                    chat_data = json.loads(chat_data)
                except json.JSONDecodeError:
                    self.logger.error(f"Invalid JSON in chat ID {chat.id}: {chat_data}")
                    chat_data = {}
            messages = chat_data.get("messages", []) if chat_data else []
            total_message_count += len(messages)
            chat_details.append({
                "title": chat.title,
                "link": f"https://lms.hoctiep.com/chat/{chat.id}"
            })

        return chat_count, total_message_count, chat_details
    
    def get_email_info(self, email: str) -> Dict:
        """Lấy thông tin email chi tiết"""
        self.logger.info(f"Checking email: {email}")
        
        user = self.get_user_by_email(email)
        has_account = 1 if user else 0
        
        if user:
            chat_count, message_count, chat_details = self.get_chat_details(user.id)
        else:
            chat_count, message_count, chat_details = 0, 0, []

        result = {
            "email": email,
            "has_account": has_account,
            "chat_count": chat_count,
            "message_count": message_count,
            "chat_details": chat_details
        }
        
        self.logger.info(f"Result: {result}")
        return result
    def get_email_info_default(self, email: str) -> Dict:
        """Lấy thông tin email từ danh sách mẫu"""
        if email not in email_list:
            self.logger.error(f"Email {email} not in default list")
            raise HTTPException(status_code=400, detail="Email không hợp lệ")
        
        return self.get_email_info(email)
    
    def get_email_info_default(self, email: str) -> Dict:
        """Lấy thông tin email từ danh sách mẫu"""
        if email not in email_list:
            self.logger.error(f"Email {email} not in default list")
            raise HTTPException(status_code=400, detail="Email không hợp lệ")
        
        return self.get_email_info(email)

    def _create_excel_response(self, df: pd.DataFrame, sheet_name: str, stats_df: pd.DataFrame = None) -> Response:
        """Tạo file Excel response"""
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            # Ghi bảng chính
            df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1)
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]

            # Thêm tiêu đề "Email Info" vào dòng đầu tiên
            title_format = workbook.add_format({
                'bold': True,
                'font_size': 16,
                'align': 'center',
                'font_name': 'Times New Roman',
                'valign': 'vcenter'
            })
            worksheet.merge_range('A1:E1', 'Email Info', title_format)

            # Định dạng border và hyperlink
            border_format = workbook.add_format({
                'border': 1,
                'font_name': 'Times New Roman',
                'valign': 'vcenter',
                'text_wrap': True
            })
            hyperlink_format = workbook.add_format({'border': 1, 'font_color': 'blue', 'underline': 1})

            # Áp dụng định dạng cho toàn bộ dữ liệu
            for row_num in range(2, len(df) + 2):
                for col_num in range(len(df.columns)):
                    cell_value = df.iloc[row_num - 2, col_num]
                    if isinstance(cell_value, str) and cell_value.startswith("=HYPERLINK"):
                        worksheet.write(row_num, col_num, cell_value, hyperlink_format)
                    else:
                        worksheet.write(row_num, col_num, cell_value, border_format)

            # Điều chỉnh độ rộng cột
            worksheet.set_column("A:A", 20)  # Độ rộng cột Email
            worksheet.set_column("B:B", 15)  # Độ rộng cột Có tài khoản chưa
            worksheet.set_column("C:C", 15)  # Độ rộng cột Số lượng chat
            worksheet.set_column("D:D", 15)  # Độ rộng cột Số lượng tin nhắn

            # Điều chỉnh độ rộng các cột link động
            for col_num in range(4, len(df.columns)):
                worksheet.set_column(col_num, col_num, 30)

            # Ghi bảng thống kê vào một sheet mới
            if stats_df is not None:
                stats_df.to_excel(writer, sheet_name="Thống kê", index=False)
                stats_worksheet = writer.sheets["Thống kê"]

                # Định dạng border cho bảng thống kê
                for row_num in range(1, len(stats_df) + 1):
                    for col_num in range(len(stats_df.columns)):
                        stats_worksheet.write(row_num, col_num, stats_df.iloc[row_num - 1, col_num], border_format)

                # Điều chỉnh độ rộng cột cho bảng thống kê
                stats_worksheet.set_column("A:A", 30)
                stats_worksheet.set_column("B:B", 20)

        output.seek(0)
        headers = {
            "Content-Disposition": "attachment; filename=email_info.xlsx",
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
        return Response(output.read(), headers=headers, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    def export_emails_excel(self) -> Response:
        """Xuất file Excel thông tin email"""
        data = []
        emails = self.db.query(User.email).limit(10).all()
        email_list_db = [email[0] for email in emails]

        for email in email_list_db:
            email_info = self.get_email_info(email)
            chat_links = "\n".join([f'=HYPERLINK("{chat["link"]}", "{chat["title"]}")' 
                                for chat in email_info["chat_details"]])
            
            data.append({
                "Email": email_info["email"],
                "Có tài khoản chưa": "Có" if email_info["has_account"] else "Không",
                "Số lượng chat": email_info["chat_count"],
                "Số lượng tin nhắn": email_info["message_count"],
                "Chi tiết chat": chat_links
            })

        df = pd.DataFrame(data).fillna("").sort_values(by="Số lượng chat", ascending=False)

        # Tính toán các thống kê
        total_emails = len(email_list_db)
        emails_with_account = df[df["Có tài khoản chưa"] == "Có"].shape[0]
        emails_without_account = total_emails - emails_with_account
        total_chats = df["Số lượng chat"].sum()
        total_messages = df["Số lượng tin nhắn"].sum()
        emails_without_chats = df[df["Số lượng chat"] == 0].shape[0]
        email_most_chats = df.loc[df["Số lượng chat"].idxmax()]["Email"]
        email_least_chats = df.loc[df["Số lượng chat"].idxmin()]["Email"]

        # Tạo bảng thống kê
        stats_data = {
            "Tiêu chí": [
                "Tổng số email",
                "Số email đã có tài khoản",
                "Số email chưa có tài khoản",
                "Tổng số cuộc hội thoại",
                "Tổng số tin nhắn",
                "Số Email chưa có cuộc hội thoại nào",
                "Email có nhiều nhất cuộc hội thoại",
                "Email có ít nhất cuộc hội thoại"
            ],
            "Giá trị": [
                total_emails,
                emails_with_account,
                emails_without_account,
                total_chats,
                total_messages,
                emails_without_chats,
                email_most_chats,
                email_least_chats
            ]
        }
        stats_df = pd.DataFrame(stats_data)

        return self._create_excel_response(df, "Email Info", stats_df)

    def export_default_emails_excel(self) -> Response:
        """Xuất file Excel cho danh sách email mặc định"""
        data = []
        
        for email in email_list:
            email_info = self.get_email_info_default(email)
            row = {
                "Email": email_info["email"],
                "Có tài khoản chưa": "Có" if email_info["has_account"] else "Không",
                "Số lượng chat": email_info["chat_count"],
                "Số lượng tin nhắn": email_info["message_count"],
            }
            for i, chat in enumerate(email_info["chat_details"]):
                row[f"Link {i + 1}"] = f'=HYPERLINK("{chat["link"]}", "{chat["title"]}")'
            data.append(row)

        df = pd.DataFrame(data).fillna("").sort_values(by="Số lượng chat", ascending=False)

        # Tính toán các thống kê
        total_emails = len(email_list)
        emails_with_account = df[df["Có tài khoản chưa"] == "Có"].shape[0]
        emails_without_account = total_emails - emails_with_account
        total_chats = df["Số lượng chat"].sum()
        total_messages = df["Số lượng tin nhắn"].sum()
        emails_without_chats = df[df["Số lượng chat"] == 0].shape[0]
        email_most_chats = df.loc[df["Số lượng chat"].idxmax()]["Email"]
        email_least_chats = df.loc[df["Số lượng chat"].idxmin()]["Email"]

        # Tạo bảng thống kê
        stats_data = {
            "Tiêu chí": [
                "Tổng số email",
                "Số email đã có tài khoản",
                "Số email chưa có tài khoản",
                "Tổng số cuộc hội thoại",
                "Tổng số tin nhắn",
                "Số Email chưa có cuộc hội thoại nào",
                "Email có nhiều nhất cuộc hội thoại",
                "Email có ít nhất cuộc hội thoại"
            ],
            "Giá trị": [
                total_emails,
                emails_with_account,
                emails_without_account,
                total_chats,
                total_messages,
                emails_without_chats,
                email_most_chats,
                email_least_chats
            ]
        }
        stats_df = pd.DataFrame(stats_data)

        return self._create_excel_response(df, "Default Email Info", stats_df)
        
# def get_email_info(email: str, target_db: Session, source_db: Session) -> dict:
#     """Lấy thông tin email từ database với hiệu suất tối ưu"""
#     logger.info(f"Checking email: {email}")
#      # 1. Kiểm tra email trong target_db
#     user = target_db.query(User).filter(User.email == email).first()
    
#     # Initialize `has_source_account` to avoid UnboundLocalError
#     has_source_account = 0  # Default to 0 (Không có tài khoản)

#     if user:
#         has_source_account = 1  # Nếu user tồn tại, cập nhật thành 1 (Có tài khoản)
#     # # 1. Kiểm tra email trong target_db
#     # user = target_db.query(User).filter(User.email == email).first()
#     # if not user:
#     #     all_emails = [u.email for u in target_db.query(User).all()]
#     #     logger.error(f"Email {email} not found in target_db. Available emails: {all_emails}")
#     #     raise HTTPException(status_code=404, detail="Email not found in target_db")
    
#     # logger.info(f"Found user: {user.email}, ID: {user.id}")

#     # has_source_account = source_db.query(User.id).filter(User.email == email).scalar() is not None
#     # logger.info(f"Has source account: {has_source_account}")

#     # 2. Lấy danh sách chat và đếm số cuộc hội thoại
#     chats = target_db.query(Chat).filter(Chat.user_id == user.id).all()
#     chat_count = len(chats)
#     logger.info(f"Chat query result: {chat_count} chats found")

#     # 3. Tính tổng số tin nhắn và tạo chat_details
#     total_message_count = 0
#     chat_details = []

#     for chat in chats:
#         # Xử lý chat.chat: Parse nếu là string, dùng dict nếu đã là JSON
#         chat_data = chat.chat
#         if isinstance(chat_data, str):
#             try:
#                 chat_data = json.loads(chat_data)
#             except json.JSONDecodeError:
#                 logger.error(f"Invalid JSON in chat.chat for chat ID {chat.id}: {chat_data}")
#                 chat_data = {}
#         messages = chat_data.get("messages", []) if chat_data else []
#         total_message_count += len(messages)
#         chat_details.append({
#             "title": chat.title,
#             "link": f"https://lms.hoctiep.com/chat/{chat.id}"
#         })

#     # 4. Trả về kết quả
#     result = {
#         "email": email,
#         "has_source_account": has_source_account,
#         "chat_count": chat_count,
#         "message_count": total_message_count,
#         "chat_details": chat_details
#     }
#     logger.info(f"Result: {result}")
#     return result

# def get_email_info_default(email: str, target_db: Session, source_db: Session) -> dict:
#     """Lấy thông tin email từ database nhưng chỉ kiểm tra các email trong danh sách mẫu."""
#     if email not in email_list:
#         logger.error(f"Email {email} không nằm trong danh sách mẫu.")
#         raise HTTPException(status_code=400, detail="Email không hợp lệ")

#     logger.info(f"Checking email: {email}")

#     # 1. Kiểm tra email trong target_db
#     user = target_db.query(User).filter(User.email == email).first()
    
#     # Initialize `has_source_account` to avoid UnboundLocalError
#     has_source_account = 0  # Default to 0 (Không có tài khoản)

#     if user:
#         has_source_account = 1  # Nếu user tồn tại, cập nhật thành 1 (Có tài khoản)

#     # 2. Lấy danh sách chat và đếm số cuộc hội thoại
#     chats = target_db.query(Chat).filter(Chat.user_id == user.id).all() if user else []
#     chat_count = len(chats)
#     logger.info(f"Chat query result: {chat_count} chats found")

#     # 3. Tính tổng số tin nhắn và tạo chat_details
#     total_message_count = 0
#     chat_details = []

#     for chat in chats:
#         # Xử lý chat.chat: Parse nếu là string, dùng dict nếu đã là JSON
#         chat_data = chat.chat
#         if isinstance(chat_data, str):
#             try:
#                 chat_data = json.loads(chat_data)
#             except json.JSONDecodeError:
#                 logger.error(f"Invalid JSON in chat.chat for chat ID {chat.id}: {chat_data}")
#                 chat_data = {}
#         messages = chat_data.get("messages", []) if chat_data else []
#         total_message_count += len(messages)
#         chat_details.append({
#             "title": chat.title,
#             "link": f"https://lms.hoctiep.com/chat/{chat.id}"
#         })

#     # 4. Trả về kết quả
#     result = {
#         "email": email,
#         "has_source_account": has_source_account,
#         "chat_count": chat_count,
#         "message_count": total_message_count,
#         "chat_details": chat_details
#     }
#     logger.info(f"Result: {result}")
#     return result
