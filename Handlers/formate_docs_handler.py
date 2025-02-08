from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery
from Keyboards.start_keybord import create_keybord
from config_status import *
from DataBase.users_db import db_conect, set_status

router = Router()


@router.callback_query(F.data == "formate_data")
async def info(callback: CallbackQuery):
    await db_conect()
    await callback.message.answer("Данная функция *в разработке!* Выберите другую:", parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=create_keybord())
    await set_status(user_id=callback.message.from_user.id, status=SET_STATUS_DEFAULT)
    await callback.answer("Запрос выполнен!")
