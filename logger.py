import os
import logging
import pytz
from datetime import datetime


class TZFormatter(logging.Formatter):
    """
    Форматтер логирования с учетом часового пояса.
    """

    def __init__(self, fmt, tz):
        super().__init__(fmt)
        self.tz = pytz.timezone(tz)

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, self.tz)
        return dt.strftime(datefmt if datefmt else "%d-%m-%Y %H:%M:%S")


def init_logger(
    LOGGER_LVL: str,
    MAX_LOGS: int,
    TZ: str = "Europe/Moscow",
    LOGS_DIR: str = "logs",
    prefix: str = "bot",
) -> None:
    """
    Устанавливает основные правила логгирования в проекте.
    """
    os.makedirs(LOGS_DIR, exist_ok=True)

    log_files = sorted(
        [
            f
            for f in os.listdir(LOGS_DIR)
            if f.startswith(f"{prefix}_") and f.endswith(".log")
        ],
        key=lambda f: os.path.getctime(os.path.join(LOGS_DIR, f)),
    )

    # Удаляем старые логи, оставляя только MAX_LOGS файлов
    if len(log_files) > MAX_LOGS:
        for old_log in log_files[:-MAX_LOGS]:
            os.remove(os.path.join(LOGS_DIR, old_log))

    # Формируем имя нового лог-файла с правильным временем
    log_filename = datetime.now(tz=pytz.timezone(TZ)).strftime(
        f"{prefix}_%d-%m-%Y_%H-%M-%S.log"
    )
    LOG_FILE = os.path.join(LOGS_DIR, log_filename)

    # Создаем логгер
    logger = logging.getLogger()
    logger.setLevel(LOGGER_LVL)

    # Очищаем старые обработчики (чтобы не дублировались записи)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Создаем форматтер с таймзоной
    formatter = TZFormatter("[%(levelname)s] %(asctime)s | %(name)s | %(message)s", TZ)

    # Обработчик для файла
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Добавляем обработчики
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
