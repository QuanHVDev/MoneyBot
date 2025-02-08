import os
import json
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Kiểm tra xem biến môi trường có tồn tại không
bot_token = os.getenv("BOT_TOKEN")
firebase_key = os.getenv("FIREBASE_KEY")

print("Bot Token:", bot_token if bot_token else "BOT_TOKEN is missing!")
print("Firebase Key:", firebase_key if firebase_key else "FIREBASE_KEY is missing!")

# Nếu FIREBASE_KEY hợp lệ, parse JSON
if firebase_key:
    firebase_data = json.loads(firebase_key)
    print("Firebase Project ID:", firebase_data.get("project_id"))
else:
    print("Lỗi: FIREBASE_KEY không được tìm thấy hoặc bị sai định dạng!")
