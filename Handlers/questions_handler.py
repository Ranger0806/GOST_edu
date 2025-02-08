import asyncio
import pathlib
import aiofiles
from aiogram.client.bot import Bot
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from Keyboards.start_keybord import create_keybord
from config_status import *
from DataBase.users_db import db_conect, set_status, set_requ_count, get_requ_count
import os
from config_status import SET_STATUS_req2
from dotenv import load_dotenv
from google import genai

load_dotenv()
router = Router()

gemini_client = genai.Client(api_key=os.getenv("GIMINI_API"))


class UploadStates(StatesGroup):
    waiting_for_file = State()


@router.callback_query(F.data == "questions")
async def info(callback: CallbackQuery, state: FSMContext):
    await db_conect()
    await callback.message.answer("Отправьте файл в формате txt или pdf")
    await state.set_state(UploadStates.waiting_for_file)
    await callback.answer("Запрос выполнен!")


@router.message(UploadStates.waiting_for_file, F.document)
async def handle_file_upload(message: Message, state: FSMContext, bot: Bot):
    file_id = message.document.file_id
    file_name = message.document.file_name
    file_mime_type = message.document.mime_type

    if file_mime_type not in ["application/pdf", "text/plain"]:
        await message.answer("Файл должен быть в формате PDF или TXT.")

    file_path = f"./{file_name}"
    try:
        file = await bot.get_file(file_id)
        file_content = await bot.download_file(file.file_path)
        async with aiofiles.open(file_path, mode='wb') as f:
            await f.write(file_content.read())

        sample_file = await asyncio.to_thread(
            gemini_client.files.upload,
            file=pathlib.Path(file_path)  # Передаём как ключевой аргумент
        )

        prompt = "Задай вопросы которые могут возникнуть у комиссии по этому документу, важно чтобы вопросы были на русском языке."
        response = await asyncio.to_thread(
            gemini_client.models.generate_content,
            model="gemini-1.5-flash",
            contents=[sample_file, prompt]
        )
        await set_status(user_id=message.from_user.id, status=SET_STATUS_req2)
        await message.answer(f"Ответ от Gemini:\n{response.text}", parse_mode=ParseMode.MARKDOWN)
        await set_requ_count(requ=int(await get_requ_count(user_id=message.from_user.id)) + 1,
                             user_id=message.from_user.id)
        await set_status(user_id=message.from_user.id, status=SET_STATUS_DEFAULT)
        await message.answer("Можете продолжать!", reply_markup=create_keybord())
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
    finally:
        await set_status(user_id=message.from_user.id, status=SET_STATUS_DEFAULT)
        if os.path.exists(file_path):
            os.remove(file_path)
            await state.clear()
