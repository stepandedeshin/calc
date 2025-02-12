from aiogram import Router

import psycopg2
from sqlalchemy import Column, Date, DateTime, ForeignKey, String, Integer, cast, create_engine, extract, select, Boolean, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.functions import func
from sqlalchemy.orm import sessionmaker, Session
from datetime import date, datetime, timedelta


from config import settings
from database.users import Users


databaseAccountsRouter = Router()


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

base_of_accounts = declarative_base()
engine_of_accounts = create_engine(settings.db_url, echo=True)
Session = sessionmaker(bind=engine_of_accounts)
session_of_accounts = Session()

class Accounts(base_of_accounts):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(Users.id))
    amount = Column(Integer)
    date = Column(DateTime)
    
base_of_accounts.metadata.create_all(engine_of_accounts)


async def add_action(user_id: int, amount: int, date: DateTime):
    action = Accounts(user_id=user_id, amount=amount, date=date)
    session_of_accounts.add(action)
    session_of_accounts.commit()
    

async def delete_user_data(user_id: int):
    session_of_accounts.query(Accounts).filter_by(user_id=user_id).delete()
    session_of_accounts.commit()
    

async def get_today_amount() -> list[tuple[int, int]]:
    amounts = session_of_accounts.execute(select(Accounts.user_id, func.sum(Accounts.amount)).where(extract('day', Accounts.date) == datetime.now().day).group_by(Accounts.user_id)).all()
    return sorted(amounts)
    

async def get_week_amount() -> list[tuple[int, int]]:
    amounts = session_of_accounts.execute(select(Accounts.user_id, func.sum(Accounts.amount)).where(cast(Accounts.date, Date) >= datetime.now().date() - timedelta(days=7)).group_by(Accounts.user_id)).all()
    return sorted(amounts)


async def delete_all_accounts():
    res = session_of_accounts.execute(delete(Accounts))
    session_of_accounts.commit()