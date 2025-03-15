from aiogram.fsm.state import State, StatesGroup


class EmployeeFSM(StatesGroup):
    waiting_for_identifier = State()
    waiting_for_full_name = State()
    waiting_for_role = State()
