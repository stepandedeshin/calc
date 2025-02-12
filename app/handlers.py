import asyncio
from datetime import date
import os
import uuid
import aiofiles
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode

from app.states import DataFromMessage, Name, AddEmploye, DeleteEmploye
import app.calculations as ca
import app.keyboards as kb
from database.users import get_user_by_name, delete_all, get_user_by_tg_id, add_user, show_users, link_account_to_name, add_user_without_tg_id, delete_user_from_db, get_user_by_id
from database.accounts import add_action, delete_all_accounts, delete_user_data, get_today_amount, get_week_amount


handlersRouter = Router()


@handlersRouter.message(CommandStart())
async def start_count_data(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(DataFromMessage.text)
    await message.answer('Введите данные для счета, например:\n\n`1.5кк papa\n28% 560\n1-Яна \n2-Денис . Надя\n\nЗакрыв:\nМарина`', reply_markup=kb.start_message_keyboard, parse_mode=ParseMode.MARKDOWN)


@handlersRouter.message(F.text == 'Меню')
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text='Меню', reply_markup=kb.menu_keyboard)


@handlersRouter.callback_query(F.data == 'menu')
async def start(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.clear()
    await callback.bot.edit_message_text(text='Меню', reply_markup=kb.menu_keyboard, chat_id=callback.message.chat.id, message_id=callback.message.message_id)    


@handlersRouter.callback_query(F.data == 'add_to_db')
async def add_user_to_db(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(Name.name)
    await callback.message.answer(f'Введите ваше имя')
    
    
@handlersRouter.callback_query(F.data == 'skip_adding_to_db')
async def skip(callback: CallbackQuery):
    await callback.answer()
    
    
@handlersRouter.message(Name.name)
async def add_name_to_db(message: Message, state: FSMContext):
    await state.update_data(name = message.text)
    name = message.text
    user = await get_user_by_name(name=name)
    if not user:
        await add_user(message=message, name=name)
        msg = await message.answer(f'Пользователь {name} добавлен!')
        return
    await message.answer('Пользователь с таким именем уже есть в базе данных, возможно вас уже добавил туда другой сотрудник!', reply_markup=kb.ask_about_db_info_keyboard)


@handlersRouter.callback_query(F.data == 'link_account_to_name')
async def link_account(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    data = await state.get_data()
    await link_account_to_name(callback=callback, name=data["name"])
    await callback.message.answer(f'Аккаунт {callback.from_user.id} успешно привязан к имени {data["name"]}')
    await state.clear()
    

@handlersRouter.callback_query(F.data == 'add_new_employe')
async def new_employe(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    data = await state.get_data()
    await add_user(message=callback, name=data["name"])
    await callback.message.answer(f'Пользователь {callback.from_user.id} с именем {data["name"]} успешно добавлен в базу данных!')
    await state.clear()


@handlersRouter.message(F.data == 'count')
async def start_count_data(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(DataFromMessage.text)
    await message.answer('Введите данные для счета, например:\n\n`1.5кк papa\n28% 560\n1-Яна \n2-Денис . Надя\n\nЗакрыв:\nМарина`', reply_markup=kb.start_message_keyboard, parse_mode=ParseMode.MARKDOWN)


@handlersRouter.message(DataFromMessage.text)
async def count_data(message: Message, state: FSMContext):
    try:
        data = message.text.split('\n')
        amount = data[0].split(' ')
        amount_num = ''
        for digit in amount[0]:
            if digit in ['k', 'к']:
                break
            amount_num+=str(digit)
        amount_num = float(amount_num) if '.' in amount_num else int(amount_num)
        if 'к' in amount[0]:
            amount_num = amount_num * (1000**amount[0].count('к')) 
        elif 'k' in amount[0]:
            amount_num = amount_num * (1000**amount[0].count('k')) 
        else: pass
        amount_result = f"{int(amount_num)} {amount[1]}"
        percent, divisor = data[1].split(' ')[0][:-1:], data[1].split(' ')[1]
        counted_amount = await ca.count_percent(amount=int(amount_num), percent=int(percent))
        result = await ca.count_divisor(amount=float(counted_amount), divisor=int(divisor))
        percentages = await ca.count_percentages(amount=float(result))
        names = []
        name_1 = data[2][2:].split('.')
        names.append(name_1)
        name_2 = data[3][2:].split('.')
        names.append(name_2)
        for string in range(len(data)):
            if 'закрыв' in data[string].lower():
                ind = string
        name_3 = []
        for name in range(ind+1, len(data)):
            name_3.append(data[name])
        names.append(name_3)
        exists = []
        for name in names:
            names_exists = []
            for single in name:
                exist = await get_user_by_name(name=single.strip())
                names_exists.append(exist)
            exists.append(names_exists)
        percentages_expanded = [int(percentages[0]/len(names[0])), int(percentages[1]/len(names[1])), int(percentages[2]/len(names[2]))]
        main_iter = 0
        for name in exists:
            try:
                await add_action(user_id=name[main_iter][0], amount=percentages_expanded[main_iter], date=message.date)
            except:pass
            if None in name:
                none_indexes = []
                for data in range(len(name)):
                    if name[data] == None:
                        none_indexes.append(data)
                for index in none_indexes:
                    await message.answer(f'Пользователя {names[main_iter][index].strip()} нет в базе данных!', reply_markup=await kb.build_add_user_keyboard(name=names[main_iter][index], amount=int(percentages_expanded[main_iter])))
            main_iter+=1
        name_string_1 = '1-'
        for name in names[0]:
            name_string_1 += f'{name.strip()} {percentages_expanded[0]} . '
        name_string_2 = '2-'
        for name in names[1]:
            name_string_2 += f'{name.strip()} {percentages_expanded[1]} . '
        name_string_3 = 'Закрыв:'
        for name in names[2]:
            name_string_3 += f'\n{name.strip()} {percentages_expanded[2]}'
        message_string = f'{amount_result}\n{percent+'%'}={int(counted_amount)}={int(result)}\n{name_string_1[:-3]}\n{name_string_2[:-3]}\n\n{name_string_3}'
        await message.answer(text=message_string, reply_markup=kb.back_to_menu_keyboard)
    except Exception as e:
        print(e.with_traceback()) 
        await message.answer(text='Ошибка при счете, введите запрос еще раз', reply_markup=kb.back_to_menu_keyboard)
        

@handlersRouter.callback_query(F.data == 'employes')
async def show_emps(callback: CallbackQuery):
    await callback.answer('')
    users = await show_users()
    if not users:
        await callback.message.bot.edit_message_text(text='Сотрудники не добавлены', chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=kb.add_and_delete_keyboard)
        return
    users_string = ''
    counter = 1
    sorted_users = sorted(users, key=lambda x: x[2])
    for data in sorted_users:
        users_string+=f'{counter}. {data[2]} | ID: {data[0]}\n'
        counter+=1
    if len(users)<100:
        await callback.message.bot.edit_message_text(text=f'Сотрудники ({len(users)}):\n{users_string}', chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=kb.add_and_delete_keyboard)
    else:
        file_name = str(uuid.uuid4()) + ".html"
        async with aiofiles.open(file_name, "w") as f:
            await f.write(users_string) 
        async with aiofiles.open(file_name, "rb") as f:
            await callback.message.answer_document(caption='Список сотрудников', document=FSInputFile(path=file_name), reply_markup=kb.add_and_delete_keyboard)
        os.remove(file_name)


@handlersRouter.callback_query(F.data == 'admin_add_emp')
async def add_employe(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(AddEmploye.emp_name)
    await callback.message.answer('Введите имя сотрудника', reply_markup=kb.back_to_menu_keyboard)
    await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)


@handlersRouter.message(AddEmploye.emp_name)
async def name_add_employe(message: Message, state: FSMContext):
    await state.clear()
    if not '\n' in message.text:
        name = message.text
        await add_user_without_tg_id(name=name)
        msg = await message.answer(f'Новый сотрудник с именем {name} добавлен в базу данных!', reply_markup=kb.back_to_menu_keyboard)
    else:
        names = message.text.split('\n')
        iter = 0
        for name in names:
            await add_user_without_tg_id(name=name.strip())
            iter+=1
        emps = ''
        emp_num = 1
        for name in names:
            emps+=f'{emp_num}. {name.strip()}\n'
            emp_num+=1
        msg = await message.answer(f'В базу данных добавлено {iter} новых сотрудников:\n\n{emps}', reply_markup=kb.back_to_menu_keyboard)
        

@handlersRouter.callback_query(F.data == 'delete_employe')
async def delete_employe(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.set_state(DeleteEmploye.emp_delete_id)
    await callback.message.answer('Введите айди сотрудника', reply_markup=kb.back_to_menu_keyboard)
    await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)


@handlersRouter.callback_query(F.data == 'delete_all')
async def delete_all_emps(callback: CallbackQuery):
    await callback.answer('')
    await delete_all_accounts()
    await delete_all()
    await callback.message.answer('Все сотрудники и информация о них удалены', reply_markup=kb.back_to_menu_keyboard)
    await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    

@handlersRouter.message(DeleteEmploye.emp_delete_id)
async def delete_employe_name(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        await state.clear()
        user = await get_user_by_id(id=user_id)
        if not user:
            await message.answer('Такого пользователя нет', reply_markup=kb.back_to_menu_keyboard)
            return
        await delete_user_data(user_id=user_id)
        await delete_user_from_db(user_id=user_id)
        await message.answer(f'Пользователь с айди {user_id} и информация о нем удалены из базы данных!', reply_markup=kb.back_to_menu_keyboard)
    except Exception as e: 
        await message.answer('Айди сотрудника должно быть числом, введите его еще раз', reply_markup=kb.back_to_menu_keyboard)
    
    
@handlersRouter.callback_query(F.data == 'day')
async def show_daily(callback: CallbackQuery):
    await callback.answer('')
    msg = 'За день\n'
    for emp in await get_today_amount():
        name = (await get_user_by_id(id=emp[0]))[1]
        msg+=f'\n{emp[0]}. {name} {emp[1]}'
    await callback.bot.edit_message_text(text=msg, reply_markup=kb.back_to_menu_keyboard, chat_id=callback.message.chat.id, message_id=callback.message.message_id)


@handlersRouter.callback_query(F.data == 'week')
async def show_weekly(callback: CallbackQuery):
    await callback.answer('')
    msg = 'За неделю\n'
    for emp in await get_week_amount():
        name = (await get_user_by_id(id=emp[0]))[1]
        msg+=f'\n{emp[0]}. {name} {emp[1]}'
    await callback.bot.edit_message_text(text=msg, reply_markup=kb.back_to_menu_keyboard, chat_id=callback.message.chat.id, message_id=callback.message.message_id)


@handlersRouter.callback_query(F.data.startswith('a_'))
async def add_user_if_not_exists(callback: CallbackQuery):
    await callback.answer('')
    data = callback.data.split('_')
    name = data[1].strip()
    amount = int(data[2])
    date = callback.message.date
    await add_user_without_tg_id(name=name)
    user_id = (await get_user_by_name(name=name))[0]
    await add_action(user_id=user_id, amount=amount, date=date)
    msg = await callback.message.answer(f'Пользователь {name} добавлен!')
    await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await asyncio.sleep(3)
    await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)


@handlersRouter.message()
async def count_data(message: Message, state: FSMContext):
    try:
        data = message.text.split('\n')
        amount = data[0].split(' ')
        amount_num = ''
        for digit in amount[0]:
            if digit in ['k', 'к']:
                break
            amount_num+=str(digit)
        amount_num = float(amount_num) if '.' in amount_num else int(amount_num)
        if 'к' in amount[0]:
            amount_num = amount_num * (1000**amount[0].count('к')) 
        elif 'k' in amount[0]:
            amount_num = amount_num * (1000**amount[0].count('k')) 
        else: pass
        amount_result = f"{int(amount_num)} {amount[1]}"
        percent, divisor = data[1].split(' ')[0][:-1:], data[1].split(' ')[1]
        counted_amount = await ca.count_percent(amount=int(amount_num), percent=int(percent))
        result = await ca.count_divisor(amount=float(counted_amount), divisor=int(divisor))
        percentages = await ca.count_percentages(amount=float(result))
        names = []
        name_1 = data[2][2:].split('.')
        names.append(name_1)
        name_2 = data[3][2:].split('.')
        names.append(name_2)
        for string in range(len(data)):
            if 'закрыв' in data[string].lower():
                ind = string
        name_3 = []
        for name in range(ind+1, len(data)):
            name_3.append(data[name])
        names.append(name_3)
        exists = []
        for name in names:
            names_exists = []
            for single in name:
                exist = await get_user_by_name(name=single.strip())
                names_exists.append(exist)
            exists.append(names_exists)
        percentages_expanded = [int(percentages[0]/len(names[0])), int(percentages[1]/len(names[1])), int(percentages[2]/len(names[2]))]
        main_iter = 0
        for name in exists:
            try:
                await add_action(user_id=name[main_iter][0], amount=percentages_expanded[main_iter], date=message.date)
            except:pass
            if None in name:
                none_indexes = []
                for data in range(len(name)):
                    if name[data] == None:
                        none_indexes.append(data)
                for index in none_indexes:
                    await message.answer(f'Пользователя {names[main_iter][index].strip()} нет в базе данных!', reply_markup=await kb.build_add_user_keyboard(name=names[main_iter][index], amount=int(percentages_expanded[main_iter])))
            main_iter+=1
        name_string_1 = '1-'
        for name in names[0]:
            name_string_1 += f'{name.strip()} {percentages_expanded[0]} . '
        name_string_2 = '2-'
        for name in names[1]:
            name_string_2 += f'{name.strip()} {percentages_expanded[1]} . '
        name_string_3 = 'Закрыв:'
        for name in names[2]:
            name_string_3 += f'\n{name.strip()} {percentages_expanded[2]}'
        message_string = f'{amount_result}\n{percent+'%'}={int(counted_amount)}={int(result)}\n{name_string_1[:-3]}\n{name_string_2[:-3]}\n\n{name_string_3}'
        await message.answer(text=message_string, reply_markup=kb.start_message_keyboard)
    except:
        msg2 = await message.answer(text='Ошибка при счете или данные введены некорректно, введите запрос еще раз', reply_markup=kb.start_message_keyboard)

        