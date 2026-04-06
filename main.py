import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import urllib.request
import urllib.parse

# --- THÔNG TIN CỦA ĐẠI CA ---
TELEGRAM_TOKEN = "8400722845:AAHAMQnpd-Y11A1zKaaHMXbFp-YXcCR1254"
CHAT_ID = "7880436708"
MA_DON_VI = "PC15LL"

def send_telegram(message):
    try:
        msg = urllib.parse.quote(message)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=HTML"
        urllib.request.urlopen(url)
    except Exception as e:
        print(f"Lỗi gửi Telegram: {e}")

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        try:
            print("→ Đang kết nối EVNSPC...")
            await page.goto("https://cskh.evnspc.vn/TraCuu/LichNgungCungCapDien", wait_until="networkidle", timeout=90000)
            await asyncio.sleep(5) 

            tu_ngay = datetime.now().strftime('%d/%m/%Y')
            api_url = f"https://cskh.evnspc.vn/TraCuu/LayDuLieuLichNgungCungCapDien?MaDonViCha=PC15&MaDonVi={MA_DON_VI}&TuNgay={tu_ngay}&DenNgay=31/12/2026"
            
            data = await page.evaluate(f"""
                async () => {{
                    try {{
                        const response = await fetch("{api_url}");
                        return await response.json();
                    }} catch (e) {{
                        return null;
                    }}
                }}
            """)
            
            if data and 'data' in data and len(data['data']) > 0:
                msg = f"⚠️ <b>LỊCH CÚP ĐIỆN LÂM HÀ ({tu_ngay})</b>\n"
                msg += "--------------------------------\n"
                for item in data['data']:
                    msg += f"📍 <b>Khu vực:</b> {item.get('TenKhuVuc')}\n"
                    msg += f"⏰ <b>Thời gian:</b> {item.get('ThoiGian')}\n"
                    msg += f"📝 <b>Lý do:</b> {item.get('LyDo')}\n"
                    msg += "--------------------------------\n"
                send_telegram(msg)
            else:
                send_telegram(f"✅ <b>BOT BÁO CÁO:</b>\nHôm nay Lâm Hà bình yên, chưa có lịch mới đại ca nhé!")

        except Exception as e:
            send_telegram(f"❌ Lỗi Bot: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
