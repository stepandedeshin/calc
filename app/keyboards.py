from datetime import date
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                            ReplyKeyboardMarkup, KeyboardButton)


start_message_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Меню')],
], resize_keyboard=True)




ask_about_db_add_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data='add_to_db')],
    [InlineKeyboardButton(text='Нет', callback_data='skip_adding_to_db')],
])


ask_about_db_info_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Привязать мой аккаунт к этому имени', callback_data='link_account_to_name')],
    [InlineKeyboardButton(text='Записать нового сотрудника', callback_data='add_new_employe')],
])


back_to_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Меню', callback_data='menu')],
])


add_and_delete_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить', callback_data='admin_add_emp')],
    [InlineKeyboardButton(text='Удалить', callback_data='delete_employe')],
    [InlineKeyboardButton(text='Удалить всех', callback_data='delete_all')],
    [InlineKeyboardButton(text='Меню', callback_data='menu')],
])


menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='За день', callback_data='day')],
    [InlineKeyboardButton(text='За неделю', callback_data='week')],
    [InlineKeyboardButton(text='Сотрудники', callback_data='employes')],
])


async def build_add_user_keyboard(name: str, amount: int):
    add_to_db_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Добавить', callback_data=f'a_{name}_{amount}')],
    ])
    return add_to_db_keyboard


