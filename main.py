import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import urllib.request
import urllib.parse

# --- ĐIỀN THÔNG TIN CỦA SẾP VÀO ĐÂY ---
TELEGRAM_TOKEN = "8400722845:AAHAMQnpd-Y11A1zKaaHMXbFp-YXcCRl254"
CHAT_ID = "7880436708"
MA_DON_VI = "PC15LL" # Lâm Hà

def send_telegram(message):
    try:
        msg = urllib.parse.quote(message)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=HTML"
        urllib.request.urlopen(url)
        print("✅ Đã bắn tin nhắn về Telegram!")
    except Exception as e:
        print(f"❌ Lỗi gửi Telegram: {e}")

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        try:
            await page.goto("https://cskh.evnspc.vn/TraCuu/LichNgungCungCapDien", timeout=60000)
            tu_ngay = datetime.now().strftime('%d/%m/%Y')
            api_url = f"https://cskh.evnspc.vn/TraCuu/LayDuLieuLichNgungCungCapDien?MaDonViCha=PC15&MaDonVi={MA_DON_VI}&TuNgay={tu_ngay}&DenNgay=31/12/2026"
            
            # Lấy dữ liệu
            data = await page.evaluate(f'async () => {{ const r = await fetch("{api_url}"); return await r.json(); }}')
            
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
                # Dòng này để sếp TEST xem bot có sống không. 
                # Sau này chạy thật sếp có thể xóa dòng send_telegram ở dưới cho đỡ phiền.
                send_telegram(f"✅ <b>BOT BÁO CÁO:</b>\nHôm nay Lâm Hà bình yên, chưa có lịch cúp điện mới đại ca nhé!")

        except Exception as e:
            send_telegram(f"❌ Lỗi Bot: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
