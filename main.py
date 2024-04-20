import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InputMediaPhoto, Message)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

from database import (create_messages_table, create_slides_table,
                      create_users_table, delete_messages, get_max_slide_id,
                      get_messages, get_slide, get_users, insert_message,
                      insert_slide, insert_user)
from middleware import AdminMiddleware


load_dotenv(".env")
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()
dp.message.middleware(AdminMiddleware())


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await insert_user(message.from_user.id, message.from_user.username)
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}!")


class AddSlideStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()


@dp.message(Command('add_slide'))
async def add_slide_start(message: Message, is_admin: bool, state: FSMContext):
    if is_admin:
        await message.reply("Отправьте фотографию:")
        await state.set_state(AddSlideStates.waiting_for_name)


@dp.message(AddSlideStates.waiting_for_name, F.photo)
async def add_slide_name(message: Message, state: FSMContext):
    await state.update_data(name=message.photo[-1].file_id)
    await message.reply("Введите описание слайда:")
    await state.set_state(AddSlideStates.waiting_for_description)


@dp.message(AddSlideStates.waiting_for_description)
async def add_slide_description(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data.get('name')
    description = message.text

    await insert_slide(name, description)
    await state.clear()
    await message.reply(f"Слайд успешно добавлен!{name} - {description}")


admin_id = getenv("ADMIN_USER_ID")

class GetSlideStates(StatesGroup):
    waiting_for_id = State()


@dp.message(Command('get_slide'))
async def get_slide_start(message: Message, is_admin: bool, state: FSMContext):
    if is_admin:
        await message.reply("Отправьте id:")
        await state.set_state(GetSlideStates.waiting_for_id)


@dp.message(GetSlideStates.waiting_for_id)
async def get_slide_id(message: Message, state: FSMContext, bot: Bot):
    slide = await get_slide(message.text)
    await state.clear()

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Следующий слайд",
        callback_data=f"next_slide_{slide[0]}")
    )

    users = await get_users()

    for user_id in users:
        if user_id == int(admin_id):
            message = await bot.send_photo(chat_id=user_id, photo=slide[1], reply_markup=builder.as_markup(), caption=slide[2])
        else:
            message = await bot.send_photo(chat_id=user_id, photo=slide[1], caption=slide[2])
        await insert_message(message.message_id, user_id)


@dp.callback_query((lambda callback: callback.data.startswith("next_slide_"))) 
async def send_next_slide(callback: CallbackQuery, bot: Bot):
    slide_id = callback.data.split("_")[2]
    slide = await get_slide(int(slide_id)+1)

    builder = InlineKeyboardBuilder()
    if (int(slide_id)+1) < await get_max_slide_id():
        builder.add(InlineKeyboardButton(
            text="Следующий слайд2",
            callback_data=f"next_slide_{slide[0]}")
        )
    else:
        builder.add(InlineKeyboardButton(
            text="Слайдов больше нет",
            callback_data=f"next_slide")
        )

    messages = await get_messages()
    for message_id, user_id in messages:
        if int(user_id) == int(admin_id):
            await bot.edit_message_media(media=InputMediaPhoto(media=slide[1], caption=slide[2]), chat_id=user_id, message_id=message_id, reply_markup=builder.as_markup())
        else:
            await bot.edit_message_media(media=InputMediaPhoto(media=slide[1], caption=slide[2]), chat_id=user_id, message_id=message_id)


@dp.shutdown()
async def on_shutdown(*args, **kwargs):
    print('Начинаю очищать таблицу messages')
    await delete_messages()
    

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await create_users_table()
    await create_slides_table()
    await create_messages_table()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())