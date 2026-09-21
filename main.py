import os
import json
import asyncio
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# تمام مقادیر حساس صرفاً از Environment Variables خوانده می‌شوند
BOT_TOKEN = os.getenv("BOT_TOKEN")
PANEL_API_KEY = os.getenv("PANEL_API_KEY")
PANEL_API_URL = os.getenv("PANEL_API_URL", "https://panel.buymember.top/api/v2")
MINIAPP_URL = os.getenv("MINIAPP_URL")

# بررسی وجود متغیرهای حیاتی قبل از اجرا
if not BOT_TOKEN:
    raise ValueError("Error: BOT_TOKEN is not set in Environment Variables!")
if not PANEL_API_KEY:
    raise ValueError("Error: PANEL_API_KEY is not set in Environment Variables!")
if not MINIAPP_URL:
    raise ValueError("Error: MINIAPP_URL is not set in Environment Variables!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Telegram Handlers ---
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 ورود به فروشگاه و ثبت سفارش",
                    web_app=WebAppInfo(url=MINIAPP_URL)
                )
            ]
        ]
    )
    await message.answer(
        f"سلام {message.from_user.first_name} عزیز! 👋\n\n"
        "به ربات خوش آمدید.\n"
        "برای مشاهده سرویس‌ها و ثبت سفارش، دکمه زیر را لمس کنید:",
        reply_markup=kb
    )

@dp.message(lambda msg: msg.web_app_data is not None)
async def web_app_data_handler(message: types.Message):
    try:
        raw_data = message.web_app_data.data
        data = json.loads(raw_data)
        
        service_id = data.get("service")
        link = data.get("link")
        quantity = data.get("quantity")
        
        payload = {
            "key": PANEL_API_KEY,
            "action": "add",
            "service": service_id,
            "link": link,
            "quantity": quantity
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(PANEL_API_URL, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                result = await resp.json()
                
                if "order" in result:
                    await message.answer(
                        f"✅ **سفارش شما با موفقیت ثبت شد!**\n\n"
                        f"🔢 شماره سفارش: `{result['order']}`\n"
                        f"🔗 لینک: `{link}`\n"
                        f"📦 تعداد: `{quantity}`"
                    )
                else:
                    err_msg = result.get("error", "خطای ناشناخته از سمت سرور")
                    await message.answer(f"❌ خطا در ثبت سفارش: {err_msg}")
    except Exception as e:
        await message.answer(f"❌ خطایی رخ داد: {str(e)}")

# --- Web Server (CORS Proxy & Health Check) ---
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

async def handle_options(request):
    return add_cors_headers(web.Response(status=200))

async def handle_ping(request):
    return add_cors_headers(web.Response(text="Bot is running!"))

async def handle_services(request):
    payload = {
        "key": PANEL_API_KEY,
        "action": "services"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(PANEL_API_URL, json=payload, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                data = await resp.json()
                res = web.json_response(data)
                return add_cors_headers(res)
    except Exception as e:
        res = web.json_response({"error": str(e)}, status=500)
        return add_cors_headers(res)

async def start_web_server():
    app = web.Application()
    app.router.add_options("/{tail:.*}", handle_options)
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)
    app.router.add_get("/services", handle_services)
    
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
