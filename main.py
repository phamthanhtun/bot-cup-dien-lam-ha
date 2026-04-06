import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import urllib.request
import urllib.parse

# --- THÔNG TIN CHUẨN ---
TELEGRAM_TOKEN = "8400722845:AAHAMQnpd-Y11A1zKaaHMXbFp-YXcCRl254"
CHAT_ID = "7880436708"

def send_telegram(message):
    try:
        msg = urllib.parse.quote(message)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=HTML"
        urllib.request.urlopen(url)
    except: pass

async def run():
    async with async_playwright() as p:
        # Dùng trình duyệt giả lập thiết bị di động để lách chặn
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 375, 'height': 812})
        page = await context.new_page()
        
        try:
            # Lùi 1 ngày để lấy cả lịch đang chạy
            tu_ngay = (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')
            
            # ĐƯỜNG DÂY NÓNG: Lấy trực tiếp từ cổng dữ liệu của Đội quản lý Lâm Hà
            api_url = f"https://cskh.evnspc.vn/TraCuu/LayDuLieuLichNgungCungCapDien?MaDonViCha=PC15&MaDonVi=PC15LL01&TuNgay={tu_ngay}&DenNgay=31/12/2026"
            
            # Truy cập trang chủ trước để lấy Cookie (tránh bị Unauthorized)
            await page.goto("https://cskh.evnspc.vn/TraCuu/LichNgungCungCapDien", wait_until="networkidle")
            
            # Gọi API lấy dữ liệu
            data = await page.evaluate(f'async () => {{ const r = await fetch("{api_url}"); return await r.json(); }}')

            if data and 'data' in data and len(data['data']) > 0:
                msg = f"⚠️ <b>LỊCH CÚP ĐIỆN ĐỘI LÂM HÀ</b>\n--------------------------------\n"
                for item in data['data'][:10]: # Lấy 10 lịch mới nhất
                    msg += f"📍 <b>Khu vực:</b> {item.get('TenKhuVuc')}\n"
                    msg += f"⏰ <b>Thời gian:</b> {item.get('ThoiGian')}\n"
                    msg += f"📝 <b>Lý do:</b> {item.get('LyDo')}\n--------------------------------\n"
                send_telegram(msg)
            else:
                # Nếu mã Đội không ra, quét nốt mã Huyện
                api_url_huyen = api_url.replace("PC15LL01", "PC15LL")
                data_huyen = await page.evaluate(f'async () => {{ const r = await fetch("{api_url_huyen}"); return await r.json(); }}')
                if data_huyen and 'data' in data_huyen and len(data_huyen['data']) > 0:
                    msg = f"⚠️ <b>LỊCH CÚP ĐIỆN HUYỆN LÂM HÀ</b>\n--------------------------------\n"
                    for item in data_huyen['data'][:10]:
                        msg += f"📍 <b>Khu vực:</b> {item.get('TenKhuVuc')}\n"
                        msg += f"⏰ <b>Thời gian:</b> {item.get('ThoiGian')}\n"
                        msg += "--------------------------------\n"
                    send_telegram(msg)
                else:
                    send_telegram("🚀 Bot vẫn chạy ổn nhưng EVN chưa cập nhật lịch mới lên hệ thống API.")

        except Exception as e:
            print(f"Lỗi: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
