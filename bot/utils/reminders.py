import asyncio
from aiogram import Bot
from bot.services.database import get_user  # Функция для получения данных пользователя из БД

async def send_reminder(bot: Bot, user_id: int, delay: int) -> None:
    await asyncio.sleep(delay)
    try:
        user = await get_user(user_id)
        # Если пользователь найден и его состояние равно "Квест завершён", не отправляем уведомление
        if user and user.current_state == "Квест завершён":
            return
        await bot.send_message(
            chat_id=user_id,
            text="⏰ Не забывай про наш квест! Возвращайся, чтобы пройти дальше."
        )
    except Exception as e:
        print(f"Ошибка при отправке напоминания: {e}")

def schedule_reminders(user_id: int, delays: list[int], bot: Bot) -> None:
    for d in delays:
        asyncio.create_task(send_reminder(bot, user_id, d))
