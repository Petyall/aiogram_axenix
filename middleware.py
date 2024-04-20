from aiogram.types import Message, TelegramObject
from aiogram import BaseMiddleware
from dotenv import load_dotenv
from os import getenv
from typing import Callable, Dict, Any, Awaitable

load_dotenv(".env")
ADMIN_USER_ID = int(getenv("ADMIN_USER_ID"))

class AdminMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]) -> Any:
        if data['event_from_user'].id == ADMIN_USER_ID:
            data["is_admin"] = True
        else:
            data["is_admin"] = False
        result = await handler(event, data)
        return result