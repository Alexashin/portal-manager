from aiogram.fsm.state import State, StatesGroup


class ModuleEditFSM(StatesGroup):
    # Создание модуля
    waiting_for_edit_module_title = State()  # Название модуля
    waiting_for_edit_module_description = State()  # Описание модуля

    # Добавление уроков
    waiting_for_edit_lesson_title = State()  # Название урока
    waiting_for_edit_lesson_text = State()  # Текст урока
    waiting_for_edit_lesson_files = State()  # Файлы урока
    waiting_for_edit_lesson_video = State()  # Видео к уроку

    # Переход между уроками
    waiting_for_next_action = State()  # Добавить урок или завершить модуль
