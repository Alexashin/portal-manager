from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config_loader import *
import logging
import os

# Создание папки для логов (если её нет)
os.makedirs("logs", exist_ok=True)

# Кастомный формат логирования
LOG_FORMAT = "[%(levelname)s] %(asctime)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"  # Убираем миллисекунды

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[
        logging.FileHandler("logs/bot.log", encoding='utf-8'),  # Логирование в файл
        logging.StreamHandler()  # Логирование в консоль
    ]
)

logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
