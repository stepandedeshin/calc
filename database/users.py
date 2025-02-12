from aiogram import Router
from aiogram.types import Message, CallbackQuery

import psycopg2
from sqlalchemy import Column, String, Integer, create_engine, select, func, Boolean, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime


from config import settings


databaseUsersRouter = Router()


try:
    conn = psycopg2.connect(
        host=settings.host,
        database=settings.db_name,
        user=settings.user,
        password=settings.passw
    )
    cursor = conn.cursor()
    conn.autocommit = True 
    cursor.execute(f"CREATE DATABASE calc_bot")
    cursor.close()
    conn.close()
except: pass

base_of_users = declarative_base()
engine_of_users = create_engine(settings.db_url, echo=True)
Session = sessionmaker(bind=engine_of_users)
session_of_users = Session()

class Users(base_of_users):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True)
    name = Column(String)
    
base_of_users.metadata.create_all(engine_of_users)


async def get_user_by_id(id: int) -> list[int, str, str] | None:
    user = session_of_users.query(Users).filter_by(id = id).first()
    if not user:
        return None
    return [user.id, user.name, user.telegram_id]


async def get_user_by_tg_id(message: Message) -> list[int, str, str] | None:
    tg_id = str(message.from_user.id)
    user = session_of_users.query(Users).filter_by(telegram_id = tg_id).first()
    if not user:
        return None
    return [user.id, user.name, user.telegram_id]


async def get_user_by_name(name: str) -> list[int, str, str] | None:
    user = session_of_users.query(Users).filter_by(name = name).first()
    if not user:
        return None
    return [user.id, user.name, user.telegram_id]


async def add_user(message: Message, name: str) -> bool:
    try:
        telegram_id = str(message.from_user.id)
        user = Users(telegram_id=telegram_id, name=name)
        session_of_users.add(user)
        session_of_users.commit()
        return True
    except: return False
    

async def delete_user_from_db(user_id: int):
    user = session_of_users.query(Users).filter_by(id=user_id).first()
    session_of_users.delete(user)
    session_of_users.commit()
    

async def add_user_without_tg_id(name: str) -> bool:
    try:
        user = Users(name=name)
        session_of_users.add(user)
        session_of_users.commit()
        return True
    except: return False
    

async def show_users() -> list[int, str, str]:
    rows = session_of_users.query(Users).all()
    users = [[getattr(row, column)for column in Users.__table__.columns.keys()] for row in rows]
    return users
    

async def link_account_to_name(callback: CallbackQuery, name: str) -> bool:
    try:
        user = session_of_users.query(Users).filter_by(name = name).first()
        user.telegram_id = str(callback.from_user.id)
        session_of_users.commit()
        return True
    except: return False
    

async def delete_all():
    res = session_of_users.execute(delete(Users))
    session_of_users.commit()