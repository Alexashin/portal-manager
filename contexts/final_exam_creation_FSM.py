from aiogram.fsm.state import State, StatesGroup


class FinalExamCreationFSM(StatesGroup):
    waiting_for_question = State()  # Ожидание ввода вопроса
    waiting_for_question_type = (
        State()
    )  # Ожидание типа вопроса (с вариантами ответов или открытый)
    waiting_for_options = State()  # Ожидание ввода вариантов ответа
    waiting_for_correct_option = State()  # Ожидание выбора правильного ответа
    waiting_for_next_action = (
        State()
    )  # Ожидание команды (добавить ещё вопрос или завершить)
