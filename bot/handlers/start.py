import random

from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters.state import StateFilter

from bot.handlers.quest import RANDOM_IMAGES
from bot.states import QuestStates
from bot.services.database import save_user_data, get_user
from bot.utils.reminders import schedule_reminders

router = Router()

# Маппинг состояния пользователя из БД в FSM
STATE_MAP = {
    None: QuestStates.waiting_for_start,  # новый пользователь
    "Старт квеста": QuestStates.waiting_for_start,
    "Задание 1 выполнено": QuestStates.find_city,
    "Задание 2 выполнено": QuestStates.find_password,
    "Задание 3 выполнено": QuestStates.find_hidden_button,
    "Квест завершён": None,  # завершённый квест
}

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name

    user = await get_user(user_id)
    if user:
        await save_user_data(user_id, username, user.current_state)
        resume_state = STATE_MAP.get(user.current_state, QuestStates.waiting_for_start)

        if resume_state:
            await state.set_state(resume_state)
            if resume_state != QuestStates.waiting_for_start:
                await message.answer(
                    "<b>С возвращением!</b> Продолжаем квест."
                )

            # Переход к нужному заданию
            if resume_state == QuestStates.waiting_for_start:
                keyboard = ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text="Я готов!")]],
                    resize_keyboard=True,
                    one_time_keyboard=True
                )
                await message.answer(
                    "<b>В одной крупной IT-компании произошла утечка данных...</b>\n\n"
                    "Готов ли ты начать квест и помочь нам?",
                    reply_markup=keyboard
                )

            elif resume_state == QuestStates.find_city:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Перейти к заданию 2",
                                          url="https://www.google.com/")]
                ])
                await message.answer(
                    "<b>Задание 2:</b> Введите IP-адрес 95.52.96.86 в Google и найдите город, к которому он привязан. "
                    "Название города в XIX веке — ключ к следующему этапу!",
                    reply_markup=keyboard
                )

            elif resume_state == QuestStates.find_password:
                await message.answer_photo(
                    photo=random.choice(RANDOM_IMAGES),
                    caption="<b>Задание 3:</b> Расшифруйте текст на картинке (captcha).",
                )

            elif resume_state == QuestStates.find_hidden_button:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Перейти к заданию 4",
                                          url="https://bluvvis.github.io/it-quest/hidden_button.html")]
                ])
                await message.answer(
                    "<b>Задание 4:</b> Найдите «невидимую» кнопку на сайте.",
                    reply_markup=keyboard
                )


        else:
            await state.clear()
            await message.answer("Вы уже завершили квест. Чтобы пройти заново, используйте /reset.")

    else:
        # Новый пользователь
        await state.clear()
        await state.update_data(tasks={
            "task1_completed": False,
            "task2_completed": False,
            "task3_completed": False,
        })
        await save_user_data(user_id, username, "Старт квеста")

        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Я готов!")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer(
            "<b>В одной крупной IT-компании произошла утечка данных...</b>\n\n"
            "Готов ли ты начать квест и помочь нам?",
            reply_markup=keyboard
        )
        schedule_reminders(user_id, [3600, 86400, 259200], message.bot)
        await state.set_state(QuestStates.waiting_for_start)


@router.message(F.text == "Я готов!", StateFilter(QuestStates.waiting_for_start))
async def handle_ready(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "<b>История:</b>\n\n"
        "Ты получил(а) анонимное сообщение: «В нашей компании произошла утечка данных... "
        "Найди IP-адрес.»"
    )
    # Создаём inline-кнопку для перехода к заданию 1 через WebApp
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Перейти к заданию 1", web_app=WebAppInfo(url="https://bluvvis.github.io/it-quest/find_ip.html"))]
    ])
    await message.answer(
        "<b>Задание 1:</b> Найдите IP-адрес на сайте.",
        reply_markup=keyboard
    )
    await state.set_state(QuestStates.find_ip)


@router.message(Command("reset"))
async def cmd_clean(message: types.Message, state: FSMContext) -> None:
    # Сбрасываем текущее состояние FSM
    await state.clear()
    # Обновляем данные пользователя в базе, сбрасывая состояние на "Старт квеста"
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    await save_user_data(user_id, username, "Старт квеста")
    # Отправляем сообщение пользователю
    await message.answer("Ваш прогресс очищен. Теперь вы можете начать заново с команды /start.")
