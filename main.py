import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import API_TOKEN
from bot.models import engine, Base
from bot.handlers import start, quest, subscription, admin

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main():
    await create_tables()

    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрируем роутеры (handlers)
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(quest.router)
    dp.include_router(subscription.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
