import json
import firebase_admin
from firebase_admin import credentials, db
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
import asyncio
import os
import datetime

# Load Firebase credentials từ biến môi trường
firebase_key = json.loads(os.getenv("FIREBASE_KEY"))
cred = credentials.Certificate(firebase_key)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://moneybot-fa25a-default-rtdb.asia-southeast1.firebasedatabase.app/'  # Thay bằng URL Firebase của Quan
})

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=types.ParseMode.HTML))
dp = Dispatcher()

# Lưu lịch tập gym vào Firebase
async def save_gym_schedule(user_id, schedule_text):
    ref = db.reference(f"users/{user_id}/gym_schedule")
    schedule_dict = {}

    for line in schedule_text.split("\n"):
        parts = line.split("/")
        if len(parts) == 2:
            day, workout = parts[0].strip().lower(), parts[1].strip()
            schedule_dict[day] = workout

    ref.set(schedule_dict)

# Nhận lịch tập gym hôm nay
async def get_today_gym(user_id):
    days_map = {
        "monday": "thứ 2",
        "tuesday": "thứ 3",
        "wednesday": "thứ 4",
        "thursday": "thứ 5",
        "friday": "thứ 6",
        "saturday": "thứ 7",
        "sunday": "chủ nhật"
    }

    today = datetime.datetime.today().strftime("%A").lower()
    today_vietnamese = days_map.get(today, "không xác định")

    ref = db.reference(f"users/{user_id}/gym_schedule")
    schedule = ref.get()

    if schedule and today_vietnamese in schedule:
        return f"📅 Hôm nay là {today_vietnamese}\n🏋️ Bài tập: {schedule[today_vietnamese]}"
    else:
        return f"📅 Hôm nay là {today_vietnamese}, bạn chưa lưu lịch tập!"

# Nhận tin nhắn và lưu lịch tập
@dp.message()
async def handle_message(message: Message):
    user_id = str(message.from_user.id)
    text = message.text.strip().lower()

    if text.startswith("thứ"):
        await save_gym_schedule(user_id, text)
        await message.answer("✅ Đã lưu lịch tập gym thành công!")

    elif text == "/today_gym":
        gym_text = await get_today_gym(user_id)
        await message.answer(gym_text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
