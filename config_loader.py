from dotenv import load_dotenv
import os

ENV = os.getenv("ENV", 'dev')
if ENV != "prod":
    load_dotenv(f'.env.{ENV}')

# Общие переменные
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env!")
os_admin_ids = os.getenv("ADMIN_IDS")
if not os_admin_ids:
    raise ValueError("ADMIN_IDS не найден в .env!")
else:
    ADMIN_IDS = list(map(int, os_admin_ids.split(",")))

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# Разные переменные
DB_HOST = os.getenv("DB_HOST", 'localhost')
TZ = os.getenv("TZ", "Europe/Moscow")
LOGGER_LVL = os.getenv("LOGGER_LVL", "INFO")

# Строка подключения к БД
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:5432/{POSTGRES_DB}"
