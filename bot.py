from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
import re
import random

# Состояния
WAITING_FOR_START, FIND_IP, FIND_CITY, FIND_PASSWORD, FIND_HIDDEN_BUTTON, FINISH_QUEST = range(6)

# Данные для заданий
IP_ADDRESS = "95.52.96.86"  # Пример IP-адреса
CITY_NAME = "Кёнигсберг"  # Пример города
PASSWORD = "innohacker"  # Пример пароля

# Список случайных картинок для задания 3
RANDOM_IMAGES = [
    "https://usefoyer.com/ap/api/captcha?text=innohacker&type=text",
]

# Функция для старта бота
async def start(update: Update, context: CallbackContext) -> int:
    # Очищаем данные пользователя
    context.user_data.clear()

    # Инициализируем флаги заданий
    context.user_data["tasks"] = {
        "task1_completed": False,
        "task2_completed": False,
        "task3_completed": False,
    }

    # Отправляем приветственное сообщение с кнопкой
    reply_keyboard = [['НУ, В ПУТЬ!']]
    await update.message.reply_text(
        "Привет, это бот-помощник команды INNOPROG. Удачи в IT-квесте!\n\n"
        "Готов ли ты начать?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return WAITING_FOR_START

# Функция для обработки нажатия кнопки "НУ, В ПУТЬ!"
async def handle_start(update: Update, context: CallbackContext) -> int:
    # Удаляем предыдущие сообщения
    await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id - 1)
    await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

    # Переходим к заданию с IP
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Перейти к заданию 1", url="https://bluvvis.github.io/it-quest/find_ip.html")]
    ])
    task_message = await update.message.reply_text(
        "Задание 1: Где-то на этом сайте спрятано число. Это IP-адрес. Найди его, и ты сделаешь первый шаг.",
        reply_markup=keyboard
    )

    # Сохраняем ID сообщения с заданием
    context.user_data["task_message_id"] = task_message.message_id
    return FIND_IP

# Функция для обработки задания 1 (поиск IP-адреса)
async def find_ip(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text

    # Проверка, что введённый текст — это IP-адрес
    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", user_input):
        if user_input == IP_ADDRESS:
            # Удаляем все сообщения, связанные с заданием
            await _delete_task_messages(update, context)

            # Устанавливаем флаг выполнения задания 1
            context.user_data["tasks"]["task1_completed"] = True

            # Отправляем сообщение с правильным ответом и текстом задания 2
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Перейти к заданию 2", url="https://www.google.com")]
            ])
            task_message = await update.message.reply_text(
                "Правильно! 🎉\n\n"
                "Задание 2: Введи этот IP-адрес в Google и найди город, к которому он привязан. Название города в XIX веке — ключ ко следующему этапу!",
                reply_markup=keyboard
            )

            # Сохраняем ID нового сообщения с заданием
            context.user_data["task_message_id"] = task_message.message_id
            return FIND_CITY
        else:
            # Сохраняем ID сообщения с ошибкой
            error_message = await update.message.reply_text("Неправильный IP-адрес. Попробуй ещё раз!")
            context.user_data.setdefault("error_message_ids", []).append(error_message.message_id)
            return FIND_IP
    else:
        # Сохраняем ID сообщения с ошибкой
        error_message = await update.message.reply_text("Это не похоже на IP-адрес. Попробуй ещё раз!")
        context.user_data.setdefault("error_message_ids", []).append(error_message.message_id)
        return FIND_IP

# Функция для обработки задания 2 (поиск города)
async def find_city(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text

    if user_input.lower() == CITY_NAME.lower():
        # Удаляем все сообщения, связанные с заданием
        await _delete_task_messages(update, context)

        # Устанавливаем флаг выполнения задания 2
        context.user_data["tasks"]["task2_completed"] = True

        # Отправляем сообщение с правильным ответом и текстом задания 3
        task_message = await update.message.reply_text(
            "Правильно! 🎉\n\n"
            "Задание 3: Мы сгенерировали captcha, попробуй расшифровать текст!"
        )

        # Отправляем случайную картинку
        random_image = random.choice(RANDOM_IMAGES)
        photo_message = await update.message.reply_photo(random_image)

        # Сохраняем ID сообщения с заданием и картинки
        context.user_data["task_message_id"] = task_message.message_id
        context.user_data["photo_message_id"] = photo_message.message_id
        return FIND_PASSWORD
    else:
        # Сохраняем ID сообщения с ошибкой
        error_message = await update.message.reply_text("Неправильный город. Попробуй ещё раз!")
        context.user_data.setdefault("error_message_ids", []).append(error_message.message_id)
        return FIND_CITY

# Функция для обработки задания 3 (поиск пароля)
async def find_password(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text

    # Сравниваем пароль без учёта регистра
    if user_input.lower() == PASSWORD.lower():
        # Удаляем все сообщения, связанные с заданием
        await _delete_task_messages(update, context)

        # Устанавливаем флаг выполнения задания 3
        context.user_data["tasks"]["task3_completed"] = True

        # Отправляем сообщение с правильным ответом и текстом задания 4
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Перейти к заданию 4", url="https://bluvvis.github.io/it-quest/hidden_button.html")]
        ])
        await update.message.reply_text(
            "Правильно! 🎉\n\n"
            "Задание 4: На сайте с паролем нужно найти «невидимую» кнопку и нажать на неё.",
            reply_markup=keyboard
        )
        return FIND_HIDDEN_BUTTON
    else:
        # Сохраняем ID сообщения с ошибкой
        error_message = await update.message.reply_text("Неправильный пароль. Попробуй ещё раз!")
        context.user_data.setdefault("error_message_ids", []).append(error_message.message_id)
        return FIND_PASSWORD

# Функция для обработки задания 4 (поиск скрытой кнопки)
async def find_hidden_button(update: Update, context: CallbackContext) -> int:
    # Проверяем, что все задания 1-3 выполнены
    tasks = context.user_data.get("tasks", {})
    if not all(tasks.values()):
        await update.message.reply_text(
            "Ты ещё не прошёл все задания! Вернись и выполни их, чтобы завершить квест."
        )
        return FIND_HIDDEN_BUTTON

    # Если все задания выполнены, ждём команду /finish
    if update.message.text.strip().lower() == "/finish":
        # Удаляем все сообщения, связанные с заданием
        await _delete_task_messages(update, context)

        # Фиксируем завершение квеста
        user_id = update.message.from_user.id
        username = update.message.from_user.username

        # Здесь можно добавить логику для сохранения данных в базу данных
        # Например:
        # save_to_db(user_id, username)

        await update.message.reply_text(
            "Поздравляем! Ты успешно прошёл квест! 🎉\n"
            "Твои данные сохранены. Скоро мы добавим их в базу данных."
        )
        return ConversationHandler.END
    else:
        # Сохраняем ID сообщения с ошибкой
        error_message = await update.message.reply_text("Нет, здесь что-то не то. Попробуй ещё раз!")
        context.user_data.setdefault("error_message_ids", []).append(error_message.message_id)
        return FIND_HIDDEN_BUTTON

# Функция для отмены
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Квест завершён. Если хочешь начать заново, введи /start.")
    return ConversationHandler.END

# Вспомогательная функция для удаления всех сообщений, связанных с заданием
async def _delete_task_messages(update: Update, context: CallbackContext):
    # Удаляем сообщение с заданием
    if "task_message_id" in context.user_data:
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=context.user_data["task_message_id"])
        del context.user_data["task_message_id"]

    # Удаляем сообщение с картинкой (если есть)
    if "photo_message_id" in context.user_data:
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=context.user_data["photo_message_id"])
        del context.user_data["photo_message_id"]

    # Удаляем все сообщения с ошибками
    if "error_message_ids" in context.user_data:
        for message_id in context.user_data["error_message_ids"]:
            try:
                await context.bot.delete_message(chat_id=update.message.chat_id, message_id=message_id)
            except Exception as e:
                print(f"Не удалось удалить сообщение: {e}")
        del context.user_data["error_message_ids"]

    # Удаляем последний ответ пользователя
    await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

def main() -> None:
    # Вставь сюда свой токен
    application = Application.builder().token("8186767146:AAGIwAU1wulZVPQ8gN9w8YtMqUHJ8wq68lg").build()

    # Обработчик диалога
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_FOR_START: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_start)],
            FIND_IP: [MessageHandler(filters.TEXT & ~filters.COMMAND, find_ip)],
            FIND_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, find_city)],
            FIND_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, find_password)],
            FIND_HIDDEN_BUTTON: [
                CommandHandler("finish", find_hidden_button),  # Обработчик команды /finish
                MessageHandler(filters.TEXT & ~filters.COMMAND, find_hidden_button),  # Обработчик текстовых сообщений
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()