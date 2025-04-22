
import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv
import logging
#Load environment variables
load_dotenv()
class TelegramBot:
    def __init__(self, token=None, chat_id=None):
        """
        Khoi tao TelegramBot voi token va chat_id neu khong duoc truyen lay tu moi truongtruong
        """

        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")

        if not self.token or not self.chat_id:
            raise ValueError("Both token and chat_id must be provided.")
        
        self.bot = Bot(token=self.token) 
        self.messages = [] # List to store messages
    
    def add_message(self, message):
        """Them tin nhan vao 1 danh sachsach"""
        self.messages.append(message)
    

    async def send_combined_message(self):
        """Gui tin nhan duoc gop lai sau do lam trong danh sach"""
        if self.messages:
            combined_message = "\n".join(self.messages)
            await self.bot.send_message(chat_id=self.chat_id, text=combined_message )
            self.messages = [] # Clear after sending
# Example usage
async def main():
    bot = TelegramBot()
    await bot.send_combined_message()  # Ensure to await the async method

if __name__ == "__main__":
    asyncio.run(main())