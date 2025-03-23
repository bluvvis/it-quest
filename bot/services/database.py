import asyncio
import logging
from datetime import datetime
import openpyxl
from sqlalchemy import select

from bot.models import async_session, User


async def get_user(user_id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()


async def save_user_data(user_id: int, username: str, current_state: str, subscription_status: str = None) -> None:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if user:
            user.username = username
            user.last_activity = datetime.utcnow()
            user.current_state = current_state
            if subscription_status is not None:
                user.subscription_status = subscription_status
        else:
            user = User(
                id=user_id,
                username=username,
                first_connection=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                current_state=current_state,
                subscription_status=subscription_status or "Не проверено"
            )
            session.add(user)
        await session.commit()

async def generate_xlsx(filename: str):
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Users"
    sheet.append(["ID", "Username", "First Connection", "Last Activity", "Current State", "Subscription Status"])
    for user in users:
        sheet.append([
            user.id,
            user.username,
            user.first_connection.strftime("%Y-%m-%d %H:%M:%S") if user.first_connection else "",
            user.last_activity.strftime("%Y-%m-%d %H:%M:%S") if user.last_activity else "",
            user.current_state,
            user.subscription_status
        ])
    workbook.save(filename)
