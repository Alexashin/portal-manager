from aiogram.fsm.state import State, StatesGroup


class TestCreationFSM(StatesGroup):
    waiting_for_question = State()
    waiting_for_options = State()
    waiting_for_correct_option = State()
    waiting_for_next_action = State()
