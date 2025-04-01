from aiogram import types, Router
from bot.services.database import save_user_data
from bot.services.subscription_check import check_subscription

router = Router()

@router.callback_query(lambda callback: callback.data=="check_subscription")
async def check_subscription_callback(callback: types.CallbackQuery) -> None:
    user_id = callback.from_user.id
    username = callback.from_user.username or callback.from_user.full_name
    is_subscribed = await check_subscription(user_id, callback.bot)
    if is_subscribed:
        await save_user_data(user_id, username, "Подписка подтверждена", "Подписан")
        await callback.message.edit_reply_markup(None)
        await callback.answer("Спасибо! Вы в списке участников 🎉", show_alert=True)
    else:
        await save_user_data(user_id, username, "Подписка не подтверждена", "Не подписан")
        await callback.answer("Вы ещё не подписались на канал ❌", show_alert=True)
