import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

# =====================
# CONFIG
# =====================

load_dotenv()

BOT_TOKEN = os.getenv("8701511595:AAFhcipS4PB4pa8ygEqwFcCJiTwHFJ9-mMU")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_state = {}

# =====================
# KEYBOARD
# =====================

def main_menu():
    kb = InlineKeyboardBuilder()

    kb.button(text="📊 Статус", callback_data="status")
    kb.button(text="💰 Баланс", callback_data="balance")
    kb.button(text="🤖 AI совет", callback_data="ai")
    kb.button(text="📈 Анализ кейсов", callback_data="cases")
    kb.button(text="⚙️ Настройки", callback_data="settings")

    kb.adjust(2)
    return kb.as_markup()


# =====================
# START
# =====================

@dp.message(Command("start"))
async def start(message: Message):
    user_state[message.from_user.id] = {
        "balance": 0
    }

    await message.answer(
        "🎮 Case Battle AI Bot\nВыбери действие:",
        reply_markup=main_menu()
    )


# =====================
# CALLBACKS
# =====================

@dp.callback_query(F.data == "status")
async def status(call: CallbackQuery):
    await call.message.answer(
        "🟢 Бот работает\n"
        "🟡 Parser: demo mode\n"
        "🔵 AI: ready"
    )


@dp.callback_query(F.data == "balance")
async def balance(call: CallbackQuery):
    await call.message.answer("💰 Введи баланс числом:")


@dp.message(lambda m: m.text.isdigit())
async def set_balance(message: Message):
    user_state[message.from_user.id]["balance"] = int(message.text)

    await message.answer(
        f"✅ Баланс установлен: {message.text}\n"
        "Теперь я могу строить стратегию."
    )


@dp.callback_query(F.data == "cases")
async def cases(call: CallbackQuery):
    balance = user_state.get(call.from_user.id, {}).get("balance", 0)

    # MOCK ANALYTICS (сюда потом вставишь парсер Case Battle)
    analysis = {
        "best_case": "Silver Case",
        "roi": "12-18%",
        "risk": "medium" if balance < 500 else "high"
    }

    await call.message.answer(
        f"📈 Анализ кейсов:\n"
        f"🏆 Лучший: {analysis['best_case']}\n"
        f"💰 ROI: {analysis['roi']}\n"
        f"⚠️ Риск: {analysis['risk']}"
    )


@dp.callback_query(F.data == "ai")
async def ai(call: CallbackQuery):
    balance = user_state.get(call.from_user.id, {}).get("balance", 0)

    # УПРОЩЁННЫЙ AI (без OpenAI чтобы не ломалось)
    if balance == 0:
        text = "Сначала укажи баланс"
    elif balance < 100:
        text = "🔴 Малый баланс: играй только low-risk кейсы"
    elif balance < 500:
        text = "🟡 Средний риск: можно пробовать кейсы до 50"
    else:
        text = "🟢 Агрессивная стратегия возможна, но следи за просадками"

    await call.message.answer(f"🤖 AI анализ:\n{text}")


@dp.callback_query(F.data == "settings")
async def settings(call: CallbackQuery):
    await call.message.answer(
        "⚙️ Настройки:\n"
        "- режим анализа: demo\n"
        "- обновление: manual\n"
        "- AI: local rules"
    )


# =====================
# MAIN
# =====================

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
