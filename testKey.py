import os
import json
from dotenv import load_dotenv

load_dotenv()

firebase_key_raw = os.getenv("FIREBASE_KEY")
print("🔥 Giá trị FIREBASE_KEY từ .env:", repr(firebase_key_raw))

try:
    firebase_key = json.loads(firebase_key_raw)
    print("✅ JSON ĐÃ PARSE:", firebase_key)
except json.JSONDecodeError as e:
    print("❌ Lỗi JSON:", e)
