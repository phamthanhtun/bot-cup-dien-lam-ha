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

# TỪ KHÓA CHÍNH: VINH QUANG (Không phân biệt hoa thường)
WATCH_KEYWORD = "Vinh Quang"

def send_telegram(message):
    try:
        msg = urllib.parse.quote(message)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=HTML"
        urllib.request.urlopen(url)
    except Exception as e:
        print("❌ Lỗi Tele: " + str(e))

def is_new_event(content):
    event_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f: pass
    with open(LOG_FILE, "r") as f:
        if event_hash in f.read(): return False
    with open(LOG_FILE, "a") as f:
        f.write(event_hash + "\n")
    return True

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        try:
            url = "https://www.cskh.evnspc.vn/TraCuu/LichNgungGiamCungCapDien"
            print("🚀 Bot bắt đầu tuần tra khu vực Vinh Quang...")
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            await page.wait_for_selector("#tab-tab2")
            await page.click("#tab-tab2")
            await asyncio.sleep(3)

            await page.select_option("#idCongTyDienLuc", "PB03")
            await asyncio.sleep(4)
            await page.select_option("#idDienLuc", "PB0306")
            
            target_id = "#idThongTinLichNgungGiamMaDonVi"
            await page.wait_for_selector(target_id)
            await asyncio.sleep(5) 

            # Hốt sạch dữ liệu bảng để tránh sót lịch
            content = await page.inner_text(target_id)
            events = content.split("KHU VỰC:")
            
            found_count = 0
            for ev in events:
                # Kiểm tra không phân biệt hoa thường
                if WATCH_KEYWORD.lower() in ev.lower():
                    clean_ev = "KHU VỰC: " + ev.strip()
                    if is_new_event(clean_ev):
                        msg = "🔔 <b>THÔNG BÁO CÚP ĐIỆN VINH QUANG</b>\n"
                        msg += "📝 " + clean_ev[:1000] # Gửi đầy đủ thông tin
                        send_telegram(msg)
                        print("✅ Đã gửi Telegram lịch mới: " + WATCH_KEYWORD)
                        found_count += 1
            
            if found_count == 0:
                print("🏁 Quét xong: Vinh Quang hiện tại bình yên, không có lịch cúp.")
            else:
                print("🏁 Đã xử lý xong " + str(found_count) + " thông báo mới.")

        except Exception as e:
            print("❌ Lỗi hệ thống: " + str(e))
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
