import json
import firebase_admin
from firebase_admin import credentials, db
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.enums import ParseMode
import asyncio
import os

# Load Firebase credentials
cred = credentials.Certificate("firebase_key.json")  # Đổi tên nếu cần
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-database.firebaseio.com/'  # Thay bằng URL Firebase của Quan
})

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Lưu dữ liệu thu chi vào Firebase
async def save_transaction(user_id, category, amount):
    ref = db.reference(f"users/{user_id}/transactions")
    new_entry = ref.push()
    new_entry.set({
        "category": category,
        "amount": amount
    })

@dp.message(commands=['start'])
async def start(message: Message):
    user_id = str(message.from_user.id)  # Lấy ID Telegram của user
    await message.answer(f"Xin chào {message.from_user.first_name}! Hãy nhập thu chi của bạn.")

@dp.message(commands=['add'])
async def add_transaction(message: Message):
    try:
        user_id = str(message.from_user.id)
        args = message.text.split()
        if len(args) < 3:
            await message.answer("Vui lòng nhập đúng định dạng: /add <loại> <số tiền>")
            return

        category = args[1]
        amount = float(args[2])
        await save_transaction(user_id, category, amount)
        await message.answer(f"Đã lưu: {category} - {amount} VND ✅")

    except Exception as e:
        await message.answer("Lỗi: " + str(e))

@dp.message(commands=['history'])
async def show_history(message: Message):
    user_id = str(message.from_user.id)
    ref = db.reference(f"users/{user_id}/transactions")
    transactions = ref.get()

    if not transactions:
        await message.answer("Bạn chưa có dữ liệu thu chi nào.")
        return

    msg = "📊 <b>Lịch sử thu chi:</b>\n"
    for key, data in transactions.items():
        msg += f"🔹 {data['category']}: {data['amount']} VND\n"

    await message.answer(msg)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
