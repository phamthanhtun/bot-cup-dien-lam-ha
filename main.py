import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import urllib.request
import urllib.parse
import os
import hashlib

# --- CẤU HÌNH ---
TELEGRAM_TOKEN = "8400722845:AAHAMQnpd-Y11A1zKaaHMXbFp-YXcCRl254"
CHAT_ID = "7880436708"
LOG_FILE = "sent_logs.txt"

# Danh sách đại ca muốn lọc (Thêm bớt tùy ý sếp)
WATCH_LIST = ["Vinh Quang", "Hoài Đức", "Tân Hà"]

def send_telegram(message):
    try:
        msg = urllib.parse.quote(message)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=HTML"
        urllib.request.urlopen(url)
    except Exception as e:
        print(f"Lỗi gửi Tele: {e}")

def is_new_event(content):
    """Kiểm tra xem lịch đã gửi chưa (dựa trên nội dung)"""
    event_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f: pass
    
    with open(LOG_FILE, "r") as f:
        log_content = f.read()
        if event_hash in log_content:
            return False
            
    with open(LOG_FILE, "a") as f:
        f.write(event_hash + "\n")
    return True

async def run():
    async with async_playwright() as p:
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
            
            # 1. Click Tab 2 (Giữ nguyên ID đang chạy OK của sếp)
            await page.wait_for_selector("#tab-tab2")
            await page.click("#tab-tab2")
            await asyncio.sleep(3)

            # 2. Chọn Lâm Đồng (PB03)
            await page.select_option("#idCongTyDienLuc", "PB03")
            await asyncio.sleep(4)
            
            # 3. Chọn Lâm Hà (PB0306)
            await page.select_option("#idDienLuc", "PB0306")
            
            # 4. Đợi nạp dữ liệu (ID vùng bảng sếp vừa gửi)
            target_id = "#idThongTinLichNgungGiamMaDonVi"
            await page.wait_for_selector(target_id)
            await asyncio.sleep(7) 

            # 5. Duyệt từng dòng trong bảng để lọc
            rows = await page.query_selector_all(f"{target_id} table tbody tr")
            
            found_count = 0
            for row in rows:
                text = await row.inner_text()
                # Kiểm tra nếu dòng có chứa khu vực đại ca quan tâm
                if any(area.lower() in text.lower() for area in WATCH_LIST):
                    if is_new_event(text):
                        msg = f"🔔 <b>CÓ LỊCH CÚP ĐIỆN MỚI</b>\n"
                        msg += f"📍 Chi tiết: {text.strip()}\n"
                        msg += f"⏰ Cập nhật: {datetime.now().strftime('%H:%M %d/%m/%Y')}"
                        send_telegram(msg)
                        print(f"✅ Đã gửi lịch: {text[:50]}...")
                        found_count += 1
                    else:
                        print(f"⏭️ Đã biết lịch: {text[:30]}... (Bỏ qua)")

            if found_count == 0:
                print("⚠️ Không có lịch mới cho các khu vực đại ca theo dõi.")

        except Exception as e:
            print(f"❌ Lỗi: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
