import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import urllib.request
import urllib.parse

# --- THÔNG TIN CẤU HÌNH ---
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
        # Chạy ẩn (True) nếu đưa lên GitHub, hiện hình (False) nếu chạy máy sếp
        browser = await p.chromium.launch(headless=False) 
        context = await browser.new_context(viewport={'width': 1366, 'height': 768})
        page = await context.new_page()
        
        try:
            url = "https://www.cskh.evnspc.vn/TraCuu/LichNgungGiamCungCapDien"
            await page.goto(url, wait_until="networkidle")
            
            # 1. Click Tab 2 theo ID sếp soi
            await page.click("#tab-tab2")
            await asyncio.sleep(2)

            # 2. Chọn Tỉnh (PB03) và Huyện (PB0306)
            await page.select_option("#idCongTyDienLuc", "PB03")
            await asyncio.sleep(3)
            await page.select_option("#idDienLuc", "PB0306")
            
            # 3. Đợi vùng dữ liệu sếp vừa gửi hiện ra
            print("→ Đang đợi dữ liệu từ vùng idThongTinLichNgungGiamMaDonVi...")
            target_id = "#idThongTinLichNgungGiamMaDonVi"
            await page.wait_for_selector(target_id)
            await asyncio.sleep(5) # Chờ nạp nội dung bên trong

            # 4. Hốt trọn ổ dữ liệu
            nội_dung = await page.inner_text(target_id)
            
            if "KHU VỰC" in nội_dung.upper():
                # Xử lý chuỗi để gửi Telegram cho đẹp
                msg = f"⚡ <b>LỊCH CÚP ĐIỆN LÂM HÀ</b>\n"
                msg += f"⏰ Cập nhật: {datetime.now().strftime('%H:%M %d/%m/%Y')}\n"
                msg += "--------------------------------\n"
                msg += nội_dung.strip()
                
                send_telegram(msg[:4000]) # Giới hạn ký tự Telegram
                print("✅ Đã bắn lịch chuẩn về Telegram!")
            else:
                print("⚠️ Vùng dữ liệu trống hoặc không có lịch mới.")

        except Exception as e:
            print(f"❌ Lỗi: {e}")
        finally:
            await asyncio.sleep(10)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
