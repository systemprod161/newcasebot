import os
import asyncio
import aiohttp
import statistics
from fastapi import FastAPI
from aiogram import Bot, Dispatcher, types
from openai import OpenAI
import uvicorn

# =========================
# CONFIG
# =========================

BOT_TOKEN = os.getenv("8701511595:AAFhcipS4PB4pa8ygEqwFcCJiTwHFJ9-mMU")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

BASE_URL = "https://case-battle.red"
ASSETS_API = BASE_URL + "/api/assets?priceMin=0&priceMax=999999&page=1"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()
client = OpenAI(api_key=OPENAI_API_KEY)

# =========================
# MEMORY STATE
# =========================

user_balance = {}
loss_streak = {}
trades = []

# =========================
# MARKET DATA
# =========================

class Market:

    async def get_assets(self):
        async with aiohttp.ClientSession() as s:
            async with s.get(ASSETS_API) as r:
                return await r.json()

market = Market()

# =========================
# EV ENGINE
# =========================

class EVEngine:

    def calculate_ev(self, items):
        return sum(i["price"] * i.get("probability", 0) for i in items)

    def roi(self, case_price, ev):
        return (ev - case_price) / case_price * 100 if case_price else 0

    def volatility(self, items):
        vals = [i["price"] for i in items]
        if len(vals) < 2:
            return 0
        return statistics.pstdev(vals)

ev_engine = EVEngine()

# =========================
# RISK ENGINE
# =========================

class RiskEngine:

    def risk_score(self, volatility, loss_streak_value):
        return volatility * 0.7 + loss_streak_value * 2

    def should_stop(self, balance, loss_streak_value, risk):

        if balance < 20:
            return True, "LOW_BALANCE"

        if loss_streak_value >= 4:
            return True, "LOSS_STREAK"

        if risk > 50:
            return True, "HIGH_RISK"

        return False, "OK"

risk_engine = RiskEngine()

# =========================
# SIGNAL ENGINE
# =========================

class SignalEngine:

    def signal(self, ev, risk, balance):

        if balance < 20:
            return "STOP"

        if risk > 50:
            return "AVOID"

        if ev > 1.15:
            return "STRONG_BUY"

        if ev > 1.05:
            return "BUY"

        return "WAIT"

signal_engine = SignalEngine()

# =========================
# PORTFOLIO
# =========================

class Portfolio:

    def add_trade(self, cost, payout):
        trades.append({
            "cost": cost,
            "payout": payout,
            "pnl": payout - cost
        })

    def pnl(self):
        return sum(t["pnl"] for t in trades)

    def roi(self):
        inv = sum(t["cost"] for t in trades)
        if inv == 0:
            return 0
        return self.pnl() / inv * 100

portfolio = Portfolio()

# =========================
# AI ADVISOR
# =========================

class AIAdvisor:

    def analyze(self, context):

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"""
You are a professional risk analyst.

RULES:
- no prediction of RNG
- only statistical analysis
- focus on bankroll safety

DATA:
{context}

OUTPUT:
- signal
- explanation
- recommendation
"""
            }]
        )

        return res.choices[0].message.content

ai = AIAdvisor()

# =========================
# TELEGRAM BOT
# =========================

@dp.message()
async def handler(message: types.Message):

    uid = message.from_user.id
    text = message.text

    if text.startswith("/balance"):
        user_balance[uid] = float(text.split()[1])
        await message.answer("Balance set")

    elif text == "/status":

        bal = user_balance.get(uid, 0)
        ls = loss_streak.get(uid, 0)

        assets = await market.get_assets()

        # fake EV model (from assets prices only)
        ev = sum(a["price"] for a in assets[:10]) / 10 / 100
        vol = ev_engine.volatility(assets[:10])

        risk = risk_engine.risk_score(vol, ls)

        stop, reason = risk_engine.should_stop(bal, ls, risk)

        signal = signal_engine.signal(ev, risk, bal)

        context = {
            "balance": bal,
            "ev": ev,
            "risk": risk,
            "signal": signal,
            "stop": reason,
            "pnl": portfolio.pnl(),
            "roi": portfolio.roi()
        }

        result = ai.analyze(context)

        await message.answer(result)

    elif text == "/portfolio":
        await message.answer(
            f"""
📊 PORTFOLIO

PnL: {portfolio.pnl()}
ROI: {portfolio.roi():.2f}%
Trades: {len(trades)}
"""
        )

# =========================
# FASTAPI DASHBOARD
# =========================

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/portfolio")
def get_portfolio():
    return {
        "pnl": portfolio.pnl(),
        "roi": portfolio.roi(),
        "trades": len(trades)
    }

@app.get("/risk")
async def risk():
    assets = await market.get_assets()
    vol = ev_engine.volatility(assets[:10])

    return {
        "volatility": vol
    }

# =========================
# RUN BOTH (BOT + API)
# =========================

async def start_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    loop.create_task(start_bot())

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 10000))
    )