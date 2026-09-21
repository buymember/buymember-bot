import os
import json
import asyncio
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN = os.getenv("BOT_TOKEN")
PANEL_API_KEY = os.getenv("PANEL_API_KEY")
PANEL_API_URL = os.getenv("PANEL_API_URL", "https://panel.buymember.top/api/v2")
MINIAPP_URL = os.getenv("MINIAPP_URL")

if GAPGPTMASKTOKENqvudfkyraksX0X BOT_TOKEN:
    raise ValueError("Error: BOT_TOKEN is GAPGPTMASKTOKENqvudfkyraksX1X set!")
if GAPGPTMASKTOKENqvudfkyraksX2X PANEL_API_KEY:
    raise ValueError("Error: PANEL_API_KEY is GAPGPTMASKTOKENqvudfkyraksX3X set!")

bot = Bot(token=GAPGPTMASKTOKENqvudfkyraksX4X
dp = Dispatcher()

# --- Telegram Handlers ---
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 Open Store / ورود به فروشگاه",
                    web_app=WebAppInfo(url=MINIAPP_URL)
                )
            ]
        ]
    )
    await message.answer(
        f"Hello {message.from_user.first_name}! 👋\nWelcome to BuyMember Store.",
        reply_markup=kb
    )

@dp.message(lambda msg: msg.web_app_data is GAPGPTMASKTOKENqvudfkyraksX5X None)
async def web_app_data_handler(message: types.Message):
    try:
        raw_data = message.web_app_data.data
        data = json.loads(raw_data)
        
        payload = {
            "key": PANEL_API_KEY,
            "action": "add",
            "service": str(data.get("service")),
            "link": str(data.get("link")),
            "quantity": str(data.get("quantity"))
        }
        
        # ارسال به صورت فرم (استاندارد پنل‌های SMM)
        async with aiohttp.ClientSession() as session:
            async with session.post(PANEL_API_URL, data=payload, timeout=aiohttp.ClientTimeout(total=25)) as resp:
                result = await resp.json(content_type=None)
                if "order" in result:
                    await message.answer(f"✅ Order Placed Successfully!\nOrder ID: `{result['order']}`")
                else:
                    await message.answer(f"❌ Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        await message.answer(f"❌ System error: {str(e)}")

# --- CORS & Proxy Endpoints ---
def cors_response(data, status=200):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }
    if isinstance(data, (dict, list)):
        return web.json_response(data, status=status, headers=headers)
    return web.Response(text=str(data), status=status, headers=headers)

async def handle_options(request):
    return cors_response("OK")

async def handle_ping(request):
    return cors_response({"status": "live", "service": "buymember-bot"})

async def handle_services(request):
    payload = {
        "key": PANEL_API_KEY,
        "action": "services"
    }
    try:
        async with aiohttp.ClientSession() as session:
            # ارسال data به صورت form-data برای پنل‌های SMM
            async with session.post(PANEL_API_URL, data=payload, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                text_res = await resp.text()
                try:
                    data = json.loads(text_res)
                    return cors_response(data)
                except Exception:
                    return cors_response({"error": "Invalid response from SMM panel", "raw": text_res}, status=502)
    except Exception as e:
        return cors_response({"error": str(e)}, status=500)

async def start_web_server():
    app = web.Application()
    app.router.add_route("OPTIONS", "/{tail:.*}", handle_options)
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)
    app.router.add_get("/services", handle_services)
    
    port = int(os.getenv("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server started on port {port}")

async def main():
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
