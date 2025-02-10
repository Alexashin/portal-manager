from dotenv import load_dotenv
import os

load_dotenv()

if os.getenv("ENV") == 'dev':
    DB_HOST = 'localhost'
    print('Запущено окружение для разработки')
else:
    DB_HOST = os.getenv("DB_HOST", 'localhost')

# print('Запущено окружение для разработки')
# DB_HOST = 'localhost'

# Общие переменные
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env!")
# os_admin_ids = os.getenv("ADMIN_IDS")
# if not os_admin_ids:
#     raise ValueError("ADMIN_IDS не найден в .env!")
# else:
#     ADMIN_IDS = list(map(int, os_admin_ids.split(",")))

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# Разные переменные

TZ = os.getenv("TZ", "Europe/Moscow")
LOGGER_LVL = os.getenv("LOGGER_LVL", "INFO")

# Строка подключения к БД
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:5432/{POSTGRES_DB}"
