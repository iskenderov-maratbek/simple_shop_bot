import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    BotCommand,
    BotCommandScopeDefault,
    CallbackQuery,
)
from aiogram.filters import CommandStart
from text import start_text, contact_text, address
from admin import TOKEN, ID

bot = Bot(TOKEN)
dp = Dispatcher()

connect = ""
client_data = {}


def adder(id, msg):
    global client_data
    if id in client_data:
        client_data[id].append(f"|{msg}")
    else:
        client_data[id] = [f"|{msg}"]


def add_photo(id, photo):
    global client_data
    if id in client_data:
        client_data[id].append(photo)
    else:
        client_data[id] = [photo]


async def set_commands():
    await bot.set_my_commands(
        BotCommand("/start", "Рестарт бота/Обновление меню"),
        scope=BotCommandScopeDefault(),
    )


@dp.message(CommandStart())
async def cmd_start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправил")],
            [KeyboardButton(text="У меня проблема")],
            [KeyboardButton(text="Контакты")],
            [KeyboardButton(text="Наш адрес")],
        ]
    )
    await message.answer(start_text, reply_markup=keyboard)


@dp.message(F.text == "Отправил")
async def cmd_start(message: Message):
    if f"{message.from_user.id}" != ID:
        await message.answer("Дождитесь ответа, вам ответят в порядке очереди.")
        if connect == "":
            await bot.send_message(ID, "Новый клиент!")


async def menu_builder():
    global client_data
    if len(client_data) > 0:
        inline_keyboard = [
            [
                InlineKeyboardButton(
                    text=f"ID: {key} | сообщений: {len(client_data[key])}",
                    callback_data=key,
                )
            ]
            for key in client_data.keys()
        ]
        print(inline_keyboard)
        print(client_data)
        keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        await bot.send_message(
            ID, "Выберите чат для подключения", reply_markup=keyboard
        )
    else:
        await bot.send_message(ID, "Нет чатов для подключения")


@dp.callback_query()
async def process_callback(callback_query: CallbackQuery):
    print(f"callback query: {callback_query.data}")
    global client_data, connect
    await bot.send_message(ID, f"✅ Подключение к чату: {callback_query.data}")
    connect = f"{callback_query.data}"
    for value in client_data[callback_query.data]:
        if value[:1:] == "|":
            await bot.send_message(ID, value)
        else:
            await bot.send_photo(ID, value)


@dp.message(F.text == "У меня проблема")
async def cmd_problem(message: Message):
    if f"{message.from_user.id}" != ID:
        await message.answer(
            "Опишите подробно и емко в одном сообщении какая у вас проблема!"
        )


@dp.message(F.text == "Контакты")
async def cmd_contact(message: Message):
    await message.answer(contact_text)


@dp.message(F.text == "Наш адрес")
async def cmd_address(message: Message):
    await message.answer(address)


@dp.message(F.photo)
async def photo_handler(message: Message):
    photo_data = message.photo[-1].file_id
    if f"{message.from_user.id}" != ID and connect != f"{message.from_user.id}":
        add_photo(f"{message.from_user.id}", photo_data)
    elif connect != "" and ID == f"{message.from_user.id}":
        print(ID)
        print(f"{message.from_user.id}")
        print("GOOD")
        await bot.send_photo(connect, photo_data)
    elif connect != "" and ID != f"{message.from_user.id}":
        await bot.send_photo(ID, photo_data)


@dp.message(F.text)
async def saver(message: Message):
    print("texteeeed")
    global connect
    if f"{message.from_user.id}" != ID and connect != f"{message.from_user.id}":
        if (
            message.text != "Отправил"
            and message.text != "У меня проблема"
            and message.text != "Контакты"
            and message.text != "Наш адрес"
        ):
            adder(f"{message.from_user.id}", message.text)
    elif connect == f"{message.from_user.id}":
        await bot.send_message(ID, message.text)
    elif f"{message.from_user.id}" == ID and connect != "":
        if message.text == ".":
            await bot.send_message(ID, f"⛔️ Отключение чата с: {connect}")
            client_data.pop(connect)
            await bot.send_message(ID, f"⛔️ Удален чат с: {connect}")
            connect = ""
        else:
            await bot.send_message(connect, message.text)
    else:
        await menu_builder()


async def main():
    await dp.start_polling(bot)
    set_commands()


if __name__ == "__main__":
    asyncio.run(main())
