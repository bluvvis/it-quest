import re
import random
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from aiogram.types import WebAppInfo, FSInputFile

from bot.states import QuestStates
from bot.config import IP_ADDRESS, CITY_NAME, PASSWORD
from bot.services.database import save_user_data

router = Router()

RANDOM_IMAGES = [
    "https://ibb.co/YFbmtMLt"
]

# Импорт функции проверки подписки
from bot.services.subscription_check import check_subscription


@router.message(StateFilter(QuestStates.find_ip))
async def find_ip_handler(message: types.Message, state: FSMContext) -> None:
    user_input = message.text.strip()
    if re.match(r"^\d{1,3}(?:\.\d{1,3}){3}$", user_input):
        if user_input == IP_ADDRESS:
            data = await state.get_data()
            tasks = data.get("tasks", {})
            tasks["task1_completed"] = True
            await state.update_data(tasks=tasks)

            user_id = message.chat.id
            username = message.chat.username or message.chat.full_name
            # Проверяем подписку и обновляем статус
            is_sub = await check_subscription(user_id, message.bot)
            subscription_status = "Подписан" if is_sub else "Не подписан"
            await save_user_data(user_id, username, "Задание 1 выполнено", subscription_status)

            await message.answer(
                "<b>Отлично!</b>\n\n"
                "Теперь нужно определить, в каком городе находится сервер.",
            )
            # Inline-кнопка для перехода ко второму заданию через WebApp
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(
                    text="Перейти к заданию 2",
                    web_app=WebAppInfo(url="https://2ip.io/ru/geoip/")
                )]
            ])
            await message.answer(
                "<b>Задание 2:</b> Введите IP-адрес и найдите город, к которому он привязан. "
                "Название города в XIX веке — ключ к следующему этапу!",
                reply_markup=keyboard,
            )
            await state.set_state(QuestStates.find_city)
        else:
            await message.answer("<b>Неправильный IP-адрес.</b> Попробуйте ещё раз! ❌")
    else:
        await message.answer("<b>Это не похоже на IP-адрес.</b> Попробуйте ещё раз! ❌")


@router.message(StateFilter(QuestStates.find_city))
async def find_city_handler(message: types.Message, state: FSMContext) -> None:
    user_input = message.text.strip().lower().replace("ё", "е")
    expected_city = CITY_NAME.lower().replace("ё", "е")
    if user_input == expected_city:
        data = await state.get_data()
        tasks = data.get("tasks", {})
        tasks["task2_completed"] = True
        await state.update_data(tasks=tasks)

        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.full_name
        # Проверка подписки
        is_sub = await check_subscription(user_id, message.bot)
        subscription_status = "Подписан" if is_sub else "Не подписан"
        await save_user_data(user_id, username, "Задание 2 выполнено", subscription_status)

        await message.answer("<b>Отлично!</b> Теперь нужно ввести пароль от сервера.")
        # Inline-кнопка для перехода к заданию 3 через WebApp

        await message.answer_photo(
            photo= random.choice(RANDOM_IMAGES),
            caption = "<b>Задание 3:</b> Расшифруйте текст на картинке (captcha)"
        )
        await state.set_state(QuestStates.find_password)
    else:
        await message.answer("<b>Неверная расшифровка.</b> Попробуйте ещё раз! ❌")


@router.message(StateFilter(QuestStates.find_password))
async def find_password_handler(message: types.Message, state: FSMContext) -> None:
    user_input = message.text.strip().lower()
    if user_input == PASSWORD.lower():
        data = await state.get_data()
        tasks = data.get("tasks", {})
        tasks["task3_completed"] = True
        await state.update_data(tasks=tasks)

        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.full_name
        # Проверка подписки
        is_sub = await check_subscription(user_id, message.bot)
        subscription_status = "Подписан" if is_sub else "Не подписан"
        await save_user_data(user_id, username, "Задание 3 выполнено", subscription_status)

        await message.answer(
            "<b>Отлично!</b> Доступ к системе получен, но для доступа к файлу нужен ещё один шаг...",
        )
        # Inline-кнопка для перехода к заданию 4 через WebApp
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(
                text="Перейти к заданию 4",
                web_app=WebAppInfo(url="https://bluvvis.github.io/it-quest/hidden_button.html")
            )]
        ])
        await message.answer(
            "<b>Задание 4:</b> Найдите «невидимую» кнопку на сайте.",
            reply_markup=keyboard,
        )
        await state.set_state(QuestStates.find_hidden_button)
    else:
        await message.answer("<b>Неправильный пароль.</b> Попробуйте ещё раз! ❌")


@router.message(StateFilter(QuestStates.find_hidden_button))
async def find_hidden_button_handler(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    tasks = data.get("tasks", {})
    if not all(tasks.values()):
        await message.answer("<b>Вы не выполнили все задания.</b> Сначала выполните предыдущие шаги.")
        return

    # Завершаем квест
    await finish_quest(message, state)


async def finish_quest(message: types.Message, state: FSMContext) -> None:
    from bot.services.database import save_user_data
    from bot.services.subscription_check import check_subscription

    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    is_sub = await check_subscription(user_id, message.bot)
    subscription_status = "Подписан" if is_sub else "Не подписан"

    await save_user_data(user_id, username, "Квест завершён", subscription_status)

    if subscription_status == "Не подписан":
        await message.answer(
            "<b>Поздравляем!</b> Вы успешно прошли квест! 🎉\n\n"
            "Для участия в розыгрыше подпишитесь на канал:",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="Подписаться на канал", url="https://t.me/innoprog")],
                [types.InlineKeyboardButton(text="Проверить подписку", callback_data="check_subscription")]
            ]),
        )
    else:
        await message.answer(
            "<b>Поздравляем!</b> Вы успешно прошли квест и были добавлены в список участников розыгрыша! 🎉\n\n"
            "Скоро, в прямом эфире, мы объявим итоги нашего квеста в Telegram-канале! Не пропустите — ждем вас в эфире, удачи и до встречи! 😉\n\n",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="Перейти в канал", url="https://t.me/innoprog")]
            ]),
        )
    await state.clear()
