from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from DataBase.users_db import db_conect, cheker_user, get_new_user, get_status
from Keyboards.start_keybord import create_keybord
from config_status import SET_STATUS_DEFAULT

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await db_conect()
    if not await cheker_user(user_id=message.from_user.id):
        await get_new_user(user_id=message.from_user.id, name=message.from_user.first_name, status=SET_STATUS_DEFAULT,
                           requ=0)
        await message.answer(
            f"*{message.from_user.first_name}, добрый день!\n*", parse_mode=ParseMode.MARKDOWN,
            reply_markup=create_keybord())
    else:
        if await get_status(user_id=message.from_user.id) != SET_STATUS_DEFAULT:
            await message.answer("Подождите ответа на запрос!")
        await message.answer(
            f"*{message.from_user.first_name}, добрый день!\nВы уже зарегистрированы.*", parse_mode=ParseMode.MARKDOWN,
            reply_markup=create_keybord())
