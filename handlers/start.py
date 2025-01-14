from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

rout = Router()

@rout.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Старт')
