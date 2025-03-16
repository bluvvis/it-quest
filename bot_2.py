from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
    ConversationHandler,
    CallbackQueryHandler
)
import re
import random
import sqlite3
from datetime import datetime

# Состояния
FIND_IP, FIND_CITY, FIND_PASSWORD, FIND_HIDDEN_BUTTON, FINISH_QUEST = range(5)

# Конфигурация
IP_ADDRESS = "95.52.96.86"
CITY_NAMES = ("Кёнигсберг", "Кенигсберг")
PASSWORD = "innohacker"
CHANNEL_ID = "@innoprog"
RANDOM_IMAGES = ["https://usefoyer.com/ap/api/captcha?text=innohacker&type=text"]
HIDDEN_BUTTON_URL = "https://bluvvis.github.io/it-quest/hidden_button.html"


# Инициализация БД
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY,
                  username TEXT,
                  completed_at DATETIME,
                  subscribed BOOLEAN DEFAULT 0)''')
    conn.commit()
    conn.close()


init_db()


def save_user(user_id: int, username: str):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO users 
                 (user_id, username, completed_at)
                 VALUES (?, ?, ?)''',
              (user_id, username, datetime.now()))
    conn.commit()
    conn.close()


async def start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    context.user_data.clear()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Перейти к заданию 1", url="https://bluvvis.github.io/it-quest/find_ip.html")]
    ])

    await update.message.reply_text(
        "🎯 *Задание 1*\nНайдите IP-адрес на указанном сайте и пришлите его мне:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    return FIND_IP


async def handle_ip(update: Update, context: CallbackContext):
    user_input = update.message.text.strip()

    if user_input == IP_ADDRESS:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🗺️ Перейти к заданию 2", url="https://www.google.com")]
        ])

        await update.message.reply_text(
            "✅ *Правильно!*\n\n"
            "🎯 *Задание 2*\nНайдите город по этому IP-адресу (историческое название XIX века):",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        return FIND_CITY

    await update.message.reply_text("❌ Неверный IP-адрес. Попробуйте еще раз!")
    return FIND_IP


async def handle_city(update: Update, context: CallbackContext):
    user_input = update.message.text.strip().lower()

    if user_input in [name.lower() for name in CITY_NAMES]:
        await update.message.reply_text(
            "✅ *Правильно!*\n\n"
            "🎯 *Задание 3*\nРасшифруйте текст на картинке:",
            parse_mode="Markdown"
        )
        await update.message.reply_photo(random.choice(RANDOM_IMAGES))
        return FIND_PASSWORD

    await update.message.reply_text("❌ Неверное название города. Попробуйте еще раз!")
    return FIND_CITY


async def handle_password(update: Update, context: CallbackContext):
    user_input = update.message.text.strip().lower()

    if user_input == PASSWORD.lower():
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎁 Финальное задание", url=HIDDEN_BUTTON_URL)]
        ])

        await update.message.reply_text(
            "✅ *Правильно!*\n\n"
            "🎯 *Задание 4*\nНайдите скрытую кнопку на сайте и нажмите ее!",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        return FIND_HIDDEN_BUTTON

    await update.message.reply_text("❌ Неверный пароль. Попробуйте еще раз!")
    return FIND_PASSWORD


async def handle_hidden_button(update: Update, context: CallbackContext):
    user = update.message.from_user
    save_user(user.id, user.username)

    # Предложение подписаться после завершения
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👉 Подписаться на канал", url=f"https://t.me/{CHANNEL_ID[1:]}")],
        [InlineKeyboardButton("🚫 Нет, спасибо", callback_data="skip_subscription")]
    ])

    await update.message.reply_text(
        "🎉 *Поздравляем! Вы прошли все задания!*\n\n"
        "Хотите подписаться на наш канал с полезными материалами?",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    return FINISH_QUEST


async def finish_quest(update: Update, context: CallbackContext):
    if update.callback_query and update.callback_query.data == "skip_subscription":
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Спасибо за участие! 😊")
    else:
        await update.message.reply_text("Спасибо за подписку! ❤️")

    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("🚫 Квест прерван. Чтобы начать заново, введите /start")
    return ConversationHandler.END


def main():
    application = Application.builder().token("8186767146:AAGIwAU1wulZVPQ8gN9w8YtMqUHJ8wq68lg").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIND_IP: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ip)],
            FIND_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_city)],
            FIND_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password)],
            FIND_HIDDEN_BUTTON: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_hidden_button),
                CallbackQueryHandler(handle_hidden_button)
            ],
            FINISH_QUEST: [
                CallbackQueryHandler(finish_quest),
                MessageHandler(filters.TEXT & ~filters.COMMAND, finish_quest)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()