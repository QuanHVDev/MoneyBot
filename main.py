import os
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv

# Load token từ file .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ Không tìm thấy BOT_TOKEN! Kiểm tra file .env.")

# Khởi tạo bot và dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()  # Router để đăng ký handler
dp.include_router(router)  # Gắn router vào dispatcher

# Kết nối database SQLite
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL,
    category TEXT,
    type TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# Tạo menu phím bấm
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Thêm Thu/Chi"), KeyboardButton(text="📊 Xem Báo Cáo")]
    ],
    resize_keyboard=True
)

@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Chào mừng bạn đến với bot quản lý thu chi!", reply_markup=menu_keyboard)


@router.message(lambda message: message.text == "➕ Thêm Thu/Chi")
async def add_expense(message: types.Message):
    await message.answer("Nhập theo mẫu: `số tiền, danh mục, loại (thu/chi)`, ví dụ: `20000, ăn uống, chi`")


@router.message(lambda message: "," in message.text)
async def save_expense(message: types.Message):
    try:
        amount, category, ex_type = [x.strip() for x in message.text.split(",")]
        amount = float(amount)
        ex_type = ex_type.lower()

        if ex_type not in ["thu", "chi"]:
            raise ValueError("Loại phải là 'thu' hoặc 'chi'.")

        cursor.execute("INSERT INTO expenses (amount, category, type) VALUES (?, ?, ?)", (amount, category, ex_type))
        conn.commit()
        await message.answer("✅ Đã lưu giao dịch thành công!")
    except Exception as e:
        await message.answer(f"❌ Lỗi: {str(e)}")


@router.message(lambda message: message.text == "📊 Xem Báo Cáo")
async def report_expense(message: types.Message):
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE type='thu'")
    total_income = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE type='chi'")
    total_expense = cursor.fetchone()[0] or 0
    balance = total_income - total_expense

    report = f"💰 Thu nhập: {total_income} VND\n💸 Chi tiêu: {total_expense} VND\n📊 Số dư: {balance} VND"
    await message.answer(report)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
