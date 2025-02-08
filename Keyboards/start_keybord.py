from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types


def create_keybord():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Найти релевантные источники🌐", callback_data="find_some_data"))
    builder.row(types.InlineKeyboardButton(text="Форматирование документов 📁 [В разработке]", callback_data="formate_data"))
    builder.row(types.InlineKeyboardButton(text="Вопросы по выступлению ❓", callback_data="questions"))
    return builder.as_markup()