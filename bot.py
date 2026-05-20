import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("8701511595:AAFhcipS4PB4pa8ygEqwFcCJiTwHFJ9-mMU")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# память пользователей
users = {}

# =========================
# /start
# =========================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    users[message.from_user.id] = {
        "balance": 0,
        "mode": "safe"
    }

    await message.answer(
        "🎮 Case Battle AI Bot\n\n"
        "Команды:\n"
        "/balance - установить баланс\n"
        "/ai - получить стратегию\n"
        "/cases - анализ кейсов (demo)\n"
        "/upgrade - анализ апгрейдов\n"
    )


# =========================
# баланс
# =========================
@dp.message_handler(commands=["balance"])
async def balance_cmd(message: types.Message):
    await message.answer("💰 Отправь свой баланс числом")


@dp.message_handler(lambda m: m.text.isdigit())
async def set_balance(message: types.Message):
    users[message.from_user.id] = users.get(message.from_user.id, {})
    users[message.from_user.id]["balance"] = int(message.text)

    await message.answer(f"✅ Баланс установлен: {message.text}")


# =========================
# AI стратегия
# =========================
@dp.message_handler(commands=["ai"])
async def ai(message: types.Message):
    balance = users.get(message.from_user.id, {}).get("balance", 0)

    if balance <= 0:
        text = "❗ Сначала задай баланс через /balance"
    elif balance < 100:
        text = (
            "🔴 SAFE режим\n"
            "- только дешёвые кейсы\n"
            "- без апгрейдов\n"
            "- цель: минимизировать риск"
        )
    elif balance < 500:
        text = (
            "🟡 BALANCED режим\n"
            "- кейсы до 10–50\n"
            "- апгрейд до 30%\n"
            "- осторожный риск"
        )
    else:
        text = (
            "🟢 AGGRESSIVE режим\n"
            "- можно риск кейсы\n"
            "- апгрейды 40–60%\n"
            "- высокая волатильность"
        )

    await message.answer("🤖 AI стратегия:\n\n" + text)


# =========================
# анализ кейсов (заглушка под парсер)
# =========================
@dp.message_handler(commands=["cases"])
async def cases(message: types.Message):
    await message.answer(
        "📊 Анализ кейсов:\n\n"
        "🏆 Best case: Silver Case\n"
        "📈 ROI: 10–18%\n"
        "⚠️ Risk: medium\n\n"
        "💡 (подключи parser позже для реальных данных)"
    )


# =========================
# апгрейды
# =========================
@dp.message_handler(commands=["upgrade"])
async def upgrade(message: types.Message):
    await message.answer(
        "🚀 Анализ апгрейдов:\n\n"
        "- безопасный шанс: 20–35%\n"
        "- средний: 35–55%\n"
        "- высокий риск: 55%+\n\n"
        "⚠️ сейчас рынок нестабилен"
    )


# =========================
# запуск
# =========================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
