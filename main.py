import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

from bot.config import API_TOKEN, REDIS_HOST, REDIS_PORT, REDIS_DB
from bot.models import engine, Base
from bot.handlers import start, quest, subscription, admin

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main():
    await create_tables()

    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    storage = RedisStorage.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
    dp = Dispatcher(storage=storage)

    # Регистрируем роутеры (handlers)
    dp.include_router(admin.router)
    dp.include_router(start.router)
    dp.include_router(quest.router)
    dp.include_router(subscription.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
