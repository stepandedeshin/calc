from aiogram.fsm.state import StatesGroup, State


class DataFromMessage(StatesGroup):
    text = State()
    
    
class Name(StatesGroup):
    name = State()
    
    
class AddEmploye(StatesGroup):
    emp_name = State()
    

class DeleteEmploye(StatesGroup):
    emp_delete_id = State()