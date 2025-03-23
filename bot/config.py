import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_IDS = set(int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(","))
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
DB_URL = os.getenv("DB_URL")

# Данные для заданий – задаются здесь напрямую
IP_ADDRESS = "95.52.96.86"
CITY_NAME = "Кёнигсберг"
PASSWORD = "innohacker"
