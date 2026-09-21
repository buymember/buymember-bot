import os
import json
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# کدهای حساس از متغیرهای محیطی خوانده می‌شوند (امنیت کامل)
BOT_TOKEN = os.getenv("BOT_TOKEN")
PANEL_API_KEY = os.getenv("PANEL_API_KEY")
PANEL_API_URL = "https://panel.buymember.top/api/v2"
MINIAPP_URL = os.getenv("MINIAPP_URL")

bot = Bot(token=GAPGPTMASKTOKEN906dsl802rdX0X
dp = Dispatcher()

# کش کردن سرویس‌ها برای افزایش سرعت
cached_services = []

async def fetch_services():
    global cached_services
    async with aiohttp.ClientSession() as session:
        payload = {"key": PANEL_API_KEY, "action": "services"}
        async with session.post(PANEL_API_URL, data=payload) as resp:
            cached_services = await resp.json()
            return cached_services

# دستور /start برای باز کردن مینی‌اپ
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⚡ Open Order Store",
                web_app=WebAppInfo(url=MINIAPP_URL)
            )
        ],
        [
            InlineKeyboardButton(text="💳 Balance / Deposit", callback_data="balance"),
            InlineKeyboardButton(text="📦 Orders History", callback_data="history")
        ]
    ])
    
    await message.answer(
        f"Hi {message.from_user.first_name}! 👋\n"
        "Welcome to **BuyMember Store**.\n"
        "Tap the button below to browse services and place your order directly:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# دریافت نتیجه خرید از طریق مینی‌اپ
@dp.message(lambda msg: msg.web_app_data is not None)
async def web_app_receive_handler(message: types.Message):
    data = json.loads(message.web_app_data.data)
    
    service_id = data.get("service_id")
    link = data.get("link")
    quantity = data.get("quantity")
    
    await message.answer("⏳ Processing your order with the server...")
    
    # ارسال به API پنل شما
    async with aiohttp.ClientSession() as session:
        payload = {
            "key": PANEL_API_KEY,
            "action": "add",
            "service": service_id,
            "link": link,
            "quantity": quantity
        }
        async with session.post(PANEL_API_URL, data=payload) as resp:
            result = await resp.json()
            
            if "order" in result:
                order_id = result["order"]
                await message.answer(
                    f"✅ **Order Placed Successfully!**\n\n"
                    f"🆔 Order ID: `{order_id}`\n"
                    f"🔗 Target: `{link}`\n"
                    f"🔢 Quantity: `{quantity}`\n\n"
                    "We are processing your request now.",
                    parse_mode="Markdown"
                )
            else:
                error_msg = result.get("error", "Unknown error occurred.")
                await message.answer(f"❌ **Failed to place order:** {error_msg}")

# API Endpoint برای مینی‌اپ
async def services_endpoint(request):
    global cached_services
    if not cached_services:
        await fetch_services()
    return web.json_response(cached_services)

async def main():
    logging.basicConfig(level=logging.INFO)
    await fetch_services()
    
    # راه‌اندازی سرور مینی‌اپ
    app = web.Application()
    app.router.add_get('/api/services', services_endpoint)
    # سرو فایل استاتیک
    app.router.add_static('/', path='./public', show_index=True)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

    # اجرای ربات
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
