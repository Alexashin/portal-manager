from aiogram.fsm.state import State, StatesGroup

class FinalExamFSM(StatesGroup):
    waiting_for_question = State()  # Ожидание ответа на вопрос
    waiting_for_next_question = State()  # Переход к следующему вопросу
    waiting_for_open_answer = State()
    exam_completed = State()  # Завершение экзамена
