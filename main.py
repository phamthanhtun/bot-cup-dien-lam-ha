import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import urllib.request
import urllib.parse
import os

# Lấy thông tin từ Secret của GitHub để bảo mật (hoặc dán thẳng nếu đại ca muốn nhanh)
TELEGRAM_TOKEN = "8400722845:AAHAMQnpd-Y11A1zKaaHMXbFp-YXcCRl254"
CHAT_ID = "7880436708"

def send_telegram(message):
    try:
        msg = urllib.parse.quote(message)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=HTML"
        urllib.request.urlopen(url)
    except Exception as e:
        print(f"Lỗi gửi Tele: {e}")

async def run():
    async with async_playwright() as p:
        # Chế độ headless=True để chạy trên GitHub Actions
        browser = await p.chromium.launch(headless=True) 
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            viewport={'width': 1366, 'height': 768}
        )
        page = await context.new_page()
        
        try:
            url = "https://www.cskh.evnspc.vn/TraCuu/LichNgungGiamCungCapDien"
            print(f"→ Đang truy cập EVN...")
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Click Tab 2 (Tìm kiếm theo đơn vị quản lý)
            await page.wait_for_selector("#tab-tab2")
            await page.click("#tab-tab2")
            await asyncio.sleep(3)

            # Chọn Lâm Đồng (PB03)
            await page.select_option("#idCongTyDienLuc", "PB03")
            await asyncio.sleep(4)
            
            # Chọn Lâm Hà (PB0306)
            await page.select_option("#idDienLuc", "PB0306")
            
            # Đợi vùng dữ liệu nạp
            target_id = "#idThongTinLichNgungGiamMaDonVi"
            await page.wait_for_selector(target_id)
            await asyncio.sleep(7) 

            # Hốt dữ liệu
            nội_dung = await page.inner_text(target_id)
            
            if "KHU VỰC" in nội_dung.upper():
                msg = f"⚡ <b>LỊCH CÚP ĐIỆN LÂM HÀ</b>\n"
                msg += f"⏰ Cập nhật: {datetime.now().strftime('%H:%M %d/%m/%Y')}\n"
                msg += "--------------------------------\n"
                msg += nội_dung.strip()
                
                send_telegram(msg[:4000])
                print("✅ Đã gửi báo cáo lên Telegram.")
            else:
                print("⚠️ Hiện tại không có lịch cúp điện mới.")

        except Exception as e:
            print(f"❌ Lỗi: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
