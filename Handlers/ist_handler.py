import requests
from aiogram import Router, F, types
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from yandex_gpt.yandex_gpt import YandexGPTMessage

from config_status import *
from DataBase.users_db import db_conect, set_status
import os
from config_status import SET_STATUS_req1
from dotenv import load_dotenv
from yandex_gpt import YandexGPTConfigManagerForAPIKey
from yandex_gpt import YandexGPT

load_dotenv()
router = Router()
config_manager = YandexGPTConfigManagerForAPIKey(
    model_type="yandexgpt-lite",
    catalog_id=os.getenv("YANDEX_FOLDER_ID"),
    api_key=os.getenv("YANDEX_API_KEY")
)
yandex_gpt = YandexGPT(config_manager=config_manager)


class SearchStates(StatesGroup):
    waiting_for_topic = State()
    waiting_for_doc_type = State()
    waiting_for_min_year = State()
    waiting_for_max_year = State()
    waiting_for_confirmation = State()


@router.callback_query(F.data == "find_some_data")
async def info(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SearchStates.waiting_for_topic)
    await db_conect()
    await set_status(user_id=callback.from_user.id, status=SET_STATUS_req1)
    await callback.message.answer("Введите тему для поиска:")
    await callback.answer("Запрос выполнен!")


@router.message(SearchStates.waiting_for_topic)
async def process_topic(message: types.Message, state: FSMContext):
    topic = message.text.strip()
    await state.update_data(topic=topic)
    await message.answer(
        "Хорошо, тема: <b>{}</b>\n\n"
        "Какой тип источников тебе нужен? (например: книги, статьи, научные статьи и т.п.)".format(topic)
    )
    await state.set_state(SearchStates.waiting_for_doc_type)


@router.message(SearchStates.waiting_for_doc_type)
async def process_doc_type(message: types.Message, state: FSMContext):
    doc_type = message.text.strip().lower()
    await state.update_data(doc_type=doc_type)
    await message.answer("Отлично! Теперь введи минимальный год публикации (или напиши 'нет', если неважно).")
    await state.set_state(SearchStates.waiting_for_min_year)


@router.message(SearchStates.waiting_for_min_year)
async def process_min_year(message: types.Message, state: FSMContext):
    min_year_text = message.text.strip().lower()
    if min_year_text.isdigit():
        min_year = int(min_year_text)
    else:
        min_year = None
    await state.update_data(min_year=min_year)
    await message.answer("А теперь введи максимальный год публикации (или 'нет', если неважно).")
    await state.set_state(SearchStates.waiting_for_max_year)


@router.message(SearchStates.waiting_for_max_year)
async def process_max_year(message: types.Message, state: FSMContext):
    max_year_text = message.text.strip().lower()
    if max_year_text.isdigit():
        max_year = int(max_year_text)
    else:
        max_year = None
    await state.update_data(max_year=max_year)
    data = await state.get_data()
    topic = data["topic"]
    doc_type = data["doc_type"]
    min_year = data["min_year"]
    max_year = data["max_year"]
    text_preview = (
        f"<b>Тема:</b> {topic}\n"
        f"<b>Тип источников:</b> {doc_type}\n"
        f"<b>Минимальный год:</b> {min_year if min_year else 'не указан'}\n"
        f"<b>Максимальный год:</b> {max_year if max_year else 'не указан'}\n\n"
        f"Подтвердить поиск? (да/нет)"
    )
    await message.answer(text_preview)
    await state.set_state(SearchStates.waiting_for_confirmation)


@router.message(SearchStates.waiting_for_confirmation)
async def process_confirmation(message: types.Message, state: FSMContext):
    confirm_text = message.text.strip().lower()

    if confirm_text in ["да", "yes", "конечно", "ок", "lf"]:
        data = await state.get_data()
        topic = data["topic"]
        doc_type = data["doc_type"]
        min_year = data["min_year"]
        max_year = data["max_year"]
        await message.answer("Собираю результаты...")
        response = await get_chatgpt_sources(topic, doc_type, min_year, max_year)
        await message.answer(response, disable_web_page_preview=True)
        await set_status(user_id=message.from_user.id, status=SET_STATUS_DEFAULT)
        await state.clear()
    else:
        await message.answer("Поиск отменён. Введите /start, чтобы начать заново.")
        await set_status(user_id=message.from_user.id, status=SET_STATUS_DEFAULT)
        await state.clear()


async def get_chatgpt_sources(topic: str, doc_type: str, min_year: int, max_year: int) -> str:
    user_prompt = f"""Ты – помощник, который помогает студенту найти релевантные {doc_type} по теме: '{topic}'. "
        Требования по годам: 
        {f'не раньше {min_year}' if min_year else ''} 
        {'и' if (min_year and max_year) else ''}
        {f'не позже {max_year}' if max_year else ''}.
        Перечисли несколько основных источников с краткими пояснениями, почему они полезны."""
    prompt = [
        {'role': 'system', 'text': "Ты помогаешь выбирать релевантные источники информации"},
        {'role': 'user', 'text': user_prompt},
    ]
    try:
        return await yandex_gpt.get_async_completion(messages=prompt, temperature=0.6, max_tokens=1000, stream=False,
                                              completion_url='https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync')
    except Exception as e:
        return "Произошла ошибка при обращении к YandexGpt. Попробуйте ещё раз."
