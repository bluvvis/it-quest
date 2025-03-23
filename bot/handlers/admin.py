import datetime

from aiogram import types, Router
from aiogram.filters import Command, StateFilter
from aiogram.types import FSInputFile

from bot.config import ADMIN_IDS
from bot.services.database import generate_xlsx

router = Router()

@router.message(Command("info"))
async def cmd_info(message: types.Message) -> None:
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        return

    try:
        filename = f"report_{datetime.datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}.xlsx"
        await generate_xlsx(filename)
        document = FSInputFile(filename)
        await message.answer_document(document)
    except Exception as e:
        await message.answer(f"Ошибка при отправке файла: {e}")
