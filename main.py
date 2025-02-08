import json
import firebase_admin
from firebase_admin import credentials, db
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.default import DefaultBotProperties
import asyncio
import os
import datetime
from dotenv import load_dotenv
from aiogram.enums import ParseMode

# Load Firebase credentials từ biến môi trường
print("🔄 Đang load biến môi trường...")
load_dotenv()

firebase_key_raw = os.getenv("FIREBASE_KEY")
print("🔥 Giá trị FIREBASE_KEY từ .env:", repr(firebase_key_raw))

try:
    firebase_key = json.loads(firebase_key_raw)
    print("✅ JSON ĐÃ PARSE thành công!")
except json.JSONDecodeError as e:
    print("❌ Lỗi JSON:", e)
    exit(1)  # Dừng chương trình nếu lỗi

# Khởi tạo Firebase
print("🔄 Đang khởi tạo Firebase...")
cred = credentials.Certificate(firebase_key)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://moneybot-fa25a-default-rtdb.asia-southeast1.firebasedatabase.app/'
})
print("✅ Firebase đã khởi tạo thành công!")

# Telegram Bot
print("🔄 Đang khởi tạo Telegram Bot...")
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
print("✅ Bot đã khởi tạo thành công!")

# Hàm lưu lịch tập gym vào Firebase
async def save_gym_schedule(user_id, schedule_text):
    print(f"💾 Đang lưu lịch tập gym cho user {user_id}...")
    ref = db.reference(f"users/{user_id}/gym_schedule")
    schedule_dict = {}

    for line in schedule_text.split("\n"):
        parts = line.split("/")
        if len(parts) == 2:
            day, workout = parts[0].strip().lower(), parts[1].strip()
            schedule_dict[day] = workout

    ref.set(schedule_dict)
    print("✅ Lịch tập gym đã lưu thành công!")

# Hàm lấy lịch tập gym hôm nay
async def get_today_gym(user_id):
    print(f"📅 Đang lấy lịch tập gym cho user {user_id}...")
    days_map = {
        "monday": "thứ 2", "tuesday": "thứ 3", "wednesday": "thứ 4",
        "thursday": "thứ 5", "friday": "thứ 6", "saturday": "thứ 7", "sunday": "chủ nhật"
    }
    today = datetime.datetime.today().strftime("%A").lower()
    today_vietnamese = days_map.get(today, "không xác định")

    ref = db.reference(f"users/{user_id}/gym_schedule")
    schedule = ref.get()

    if schedule and today_vietnamese in schedule:
        return f"📅 Hôm nay là {today_vietnamese}\n🏋️ Bài tập: {schedule[today_vietnamese]}"
    else:
        return f"📅 Hôm nay là {today_vietnamese}, bạn chưa lưu lịch tập!"

# Hàm lấy báo cáo thu chi từ Firebase
async def get_financial_report(user_id):
    ref = db.reference(f"users/{user_id}/transactions")
    transactions = ref.get() or {}

    total_income = sum(int(t["amount"]) for t in transactions.values() if int(t["amount"]) > 0)
    total_expense = sum(int(t["amount"]) for t in transactions.values() if int(t["amount"]) < 0)

    report_text = f"📊 Báo cáo thu chi:\n💰 Tổng thu: {total_income} VNĐ\n💸 Tổng chi: {abs(total_expense)} VNĐ"
    return report_text

# Tạo menu với các nút chức năng
def get_main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏋️ Lịch tập hôm nay")],
            #[KeyboardButton(text="➕ Thêm thu/chi")],
            [KeyboardButton(text="📊 Xem báo cáo")]
        ],
        resize_keyboard=True
    )
    return keyboard

# Xử lý tin nhắn
@dp.message()
async def handle_message(message: Message):
    user_id = str(message.from_user.id)
    text = message.text.strip().lower()
    print(f"📩 Nhận tin nhắn từ {user_id}: {text}")

    if text.startswith("thứ"):
        await save_gym_schedule(user_id, text)
        await message.answer("✅ Đã lưu lịch tập gym thành công!", reply_markup=get_main_menu())

    elif text == "/start":
        await message.answer("🤖 Chào mừng! Chọn một tùy chọn bên dưới:", reply_markup=get_main_menu())

    elif text == "🏋️ lịch tập hôm nay":
        gym_text = await get_today_gym(user_id)
        await message.answer(gym_text)

    elif text.startswith("+") or text.startswith("-"):
        try:
            amount, category = text.split(" ", 1)
            amount = int(amount)
            await save_transaction(user_id, category, amount)
            await message.answer("✅ Đã ghi nhận giao dịch!", reply_markup=get_main_menu())
        except:
            await message.answer("❌ Định dạng không hợp lệ. Hãy nhập theo mẫu: +1000 ăn sáng hoặc -500 trà sữa",
                                 parse_mode=ParseMode.MARKDOWN)

    elif text == "📊 xem báo cáo":
        report = await get_financial_report(user_id)
        await message.answer(report)


async def save_transaction(user_id, category, amount):
    ref = db.reference(f"users/{user_id}/transactions")
    new_entry = ref.push()
    new_entry.set({
        "category": category,
        "amount": amount
    })

async def main():
    print("🚀 Bot đang khởi động...")
    await dp.start_polling(bot)
    print("✅ Bot đã sẵn sàng nhận lệnh!")

if __name__ == "__main__":
    import sys
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
