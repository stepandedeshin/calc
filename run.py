import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import settings

from app.handlers import handlersRouter
from database.accounts import databaseAccountsRouter
from database.users import databaseUsersRouter


async def main():
    bot = Bot(settings.token)
    dp= Dispatcher()
    dp.include_routers(handlersRouter, databaseUsersRouter, databaseAccountsRouter)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot disabled')