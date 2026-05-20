import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("8701511595:AAFhcipS4PB4pa8ygEqwFcCJiTwHFJ9-mMU")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

users = {}

# ================= MENU =================

def menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="📊 Статус", callback_data="status")
    kb.button(text="💰 Баланс", callback_data="balance")
    kb.button(text="🤖 AI", callback_data="ai")
    kb.button(text="📈 Кейсы", callback_data="cases")
    kb.adjust(2)
    return kb.as_markup()

# ================= START =================

@dp.message(Command("start"))
async def start(message: Message):
    users[message.from_user.id] = {"balance": 0}
    await message.answer("🎮 Case Battle AI Bot", reply_markup=menu())

# ================= BALANCE =================

@dp.message(F.text.regexp(r"^\d+$"))
async def set_balance(message: Message):
    users[message.from_user.id] = users.get(message.from_user.id, {})
    users[message.from_user.id]["balance"] = int(message.text)

    await message.answer(f"💰 Баланс: {message.text}")

# ================= CALLBACKS =================

@dp.callback_query(F.data == "status")
async def status(call: CallbackQuery):
    await call.message.answer("🟢 Bot running\n🟡 Parser: ready\n🔵 AI: active")

@dp.callback_query(F.data == "balance")
async def balance(call: CallbackQuery):
    await call.message.answer("Отправь число баланса")

@dp.callback_query(F.data == "cases")
async def cases(call: CallbackQuery):
    await call.message.answer(
        "📈 CASE ANALYSIS\n"
        "Best: Silver Case\n"
        "ROI: 10–20%\n"
        "Risk: medium"
    )

@dp.callback_query(F.data == "ai")
async def ai(call: CallbackQuery):
    bal = users.get(call.from_user.id, {}).get("balance", 0)

    if bal < 100:
        msg = "🔴 SAFE MODE"
    elif bal < 500:
        msg = "🟡 MEDIUM RISK"
    else:
        msg = "🟢 HIGH RISK"

    await call.message.answer(f"🤖 AI:\n{msg}")

# ================= RUN =================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
