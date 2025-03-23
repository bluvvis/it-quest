import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_IDS = set(int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(","))
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
DB_URL = os.getenv("DB_URL")

# Настройки Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Данные для заданий
IP_ADDRESS = "95.52.96.86"
CITY_NAME = "Кёнигсберг"
PASSWORD = "innohacker"
