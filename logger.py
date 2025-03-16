import os
import logging
from datetime import datetime


def init_logger(LOGGER_LVL: str, MAX_LOGS: int, LOGS_DIR: str = "logs") -> None:
    """
    Устанавливает основные правила логгирования в проекте.
    """
    os.makedirs(LOGS_DIR, exist_ok=True)

    log_files = sorted(
        [
            f
            for f in os.listdir(LOGS_DIR)
            if f.startswith("bot_") and f.endswith(".log")
        ],
        key=lambda f: os.path.getctime(os.path.join(LOGS_DIR, f)),
    )

    # Удаляем старые логи, оставляя только MAX_LOGS файлов
    if len(log_files) > MAX_LOGS:
        for old_log in log_files[:-MAX_LOGS]:
            os.remove(os.path.join(LOGS_DIR, old_log))

    # Формируем имя нового лог-файла с датой и временем
    log_filename = datetime.now().strftime("bot_%Y-%m-%d_%H-%M-%S.log")
    LOG_FILE = os.path.join(LOGS_DIR, log_filename)

    # Настройки логирования
    logging.basicConfig(
        level=LOGGER_LVL,
        format="[%(levelname)s] %(asctime)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),  # Запись в файл
            logging.StreamHandler(),  # Вывод в консоль
        ],
    )
