import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = os.getenv("BOT_TOKEN")
PANEL_API_KEY = os.getenv("PANEL_API_KEY")
MINIAPP_URL = os.getenv("MINIAPP_URL", "https://buymember.github.io/buymember-bot/")

if not BOT_TOKEN:
    raise ValueError("Error: BOT_TOKEN is not set in Environment Variables!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 ورود به پنل خدمات",
                    web_app=WebAppInfo(url=MINIAPP_URL)
                )
            ]
        ]
    )
    await message.answer(
        f"سلام {message.from_user.first_name} عزیز! 👋\n"
        "برای مشاهده خدمات و ثبت سفارش روی دکمه زیر کلیک کنید:",
        reply_markup=kb
    )

# وب‌سرور ساده برای راضی نگه داشتن Web Service در Render
async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    print("Bot is starting...")
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
