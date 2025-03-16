import os
import logging
from dotenv import load_dotenv
from logger import init_logger

# Загружаем переменные окружения перед их использованием
load_dotenv()

# Уровень логирования и лимит логов
LOGGER_LVL = os.getenv("LOGGER_LVL", "INFO").upper()
MAX_LOGS = int(os.getenv("MAX_LOGS", 5))

# Инициализируем логирование
init_logger(LOGGER_LVL, MAX_LOGS)

log = logging.getLogger(__name__)

if os.getenv("ENV") == "dev":
    DB_HOST = "localhost"
    log.debug("Запущено окружение для разработки")
else:
    DB_HOST = os.getenv("DB_HOST", "localhost")

# Общие переменные
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env!")

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# Разные переменные

TZ = os.getenv("TZ", "Europe/Moscow")

# Строка подключения к БД
DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:5432/{POSTGRES_DB}"
)
