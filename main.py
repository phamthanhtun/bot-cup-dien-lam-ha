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
    except:
        pass

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        try:
            # Truy cập trang chủ lấy cookie
            await page.goto("https://cskh.evnspc.vn/TraCuu/LichNgungCungCapDien", wait_until="networkidle", timeout=60000)
            
            # Lùi 2 ngày cho chắc
            tu_ngay = (datetime.now() - timedelta(days=2)).strftime('%d/%m/%Y')
            
            # DÙNG MÃ CHUẨN PB03 VÀ PB0306 ĐẠI CA SOI ĐƯỢC
            api_url = f"https://cskh.evnspc.vn/TraCuu/LayDuLieuLichNgungCungCapDien?MaDonViCha=PB03&MaDonVi=PB0306&TuNgay={tu_ngay}&DenNgay=31/12/2026"
            
            data = await page.evaluate(f'async () => {{ const r = await fetch("{api_url}"); return await r.json(); }}')

            if data and 'data' in data and len(data['data']) > 0:
                msg = f"⚠️ <b>LỊCH CÚP ĐIỆN LÂM HÀ (MÃ PB0306)</b>\n"
                msg += "--------------------------------\n"
                for item in data['data'][:10]:
                    msg += f"🏢 <b>Đơn vị:</b> {item.get('TenDonVi')}\n"
                    msg += f"📍 <b>Khu vực:</b> {item.get('TenKhuVuc')}\n"
                    msg += f"⏰ <b>Thời gian:</b> {item.get('ThoiGian')}\n"
                    msg += f"📝 <b>Lý do:</b> {item.get('LyDo')}\n"
                    msg += "--------------------------------\n"
                send_telegram(msg)
                print("✅ Đã tìm thấy lịch và gửi Telegram!")
            else:
                # Nếu mã huyện không ra, quét toàn tỉnh PB03 để tìm chữ Lâm Hà
                api_url_tinh = f"https://cskh.evnspc.vn/TraCuu/LayDuLieuLichNgungCungCapDien?MaDonViCha=PB03&MaDonVi=PB03&TuNgay={tu_ngay}&DenNgay=31/12/2026"
                data_tinh = await page.evaluate(f'async () => {{ const r = await fetch("{api_url_tinh}"); return await r.json(); }}')
                
                lich_loc = [i for i in data_tinh['data'] if "lâm hà" in str(i).lower()] if (data_tinh and 'data' in data_tinh) else []
                
                if len(lich_loc) > 0:
                    msg = f"⚠️ <b>LỊCH LÂM HÀ (TÌM THẤY TRONG MÃ PB03)</b>\n"
                    msg += "--------------------------------\n"
                    for item in lich_loc[:8]:
                        msg += f"📍 <b>Khu vực:</b> {item.get('TenKhuVuc')}\n"
                        msg += f"⏰ <b>Thời gian:</b> {item.get('ThoiGian')}\n"
                        msg += "--------------------------------\n"
                    send_telegram(msg)
                else:
                    send_telegram("🚀 Đã chạy mã PB0306 nhưng hệ thống EVN báo chưa có lịch mới đại ca ạ!")

        except Exception as e:
            print(f"Lỗi: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
