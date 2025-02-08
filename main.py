from aiogram import Bot, Dispatcher
import asyncio
import logging
import os
from DataBase.users_db import close
from Handlers import start_handler, ist_handler, questions_handler, formate_docs_handler
from dotenv import load_dotenv
from aiogram.fsm.storage.memory import MemoryStorage


async def main():
    load_dotenv()
    logging.basicConfig(level=logging.INFO, filename="tg_GOST_bot_log.log", filemode="w",
                        format="%(asctime)s %(levelname)s %(message)s")

    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    dp = Dispatcher(storage=MemoryStorage(), bot=bot)
    dp.include_routers(start_handler.router, ist_handler.router, questions_handler.router, formate_docs_handler.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    await dp.shutdown(await close())


if __name__ == "__main__":
    asyncio.run(main())
