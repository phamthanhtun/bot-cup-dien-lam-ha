import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import urllib.request
import urllib.parse
import os
import hashlib

# --- CẤU HÌNH CỦA ĐẠI CA ---
TELEGRAM_TOKEN = "8400722845:AAHAMQnpd-Y11A1zKaaHMXbFp-YXcCRl254"
CHAT_ID = "7880436708"
LOG_FILE = "sent_logs.txt"

# ĐỔI SANG ĐÔNG ANH - NAM BAN ĐỂ TEST
WATCH_AREAS = [
    {"thon": "Đông Anh", "xa": "Nam Ban"}
]

def send_telegram(message):
    try:
        msg = urllib.parse.quote(message)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=HTML"
        urllib.request.urlopen(url)
    except Exception as e:
        print(f"❌ Lỗi gửi Tele: {e}")

def is_new_event(content):
    event_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f: pass
    
    with open(LOG_FILE, "r") as f:
        log_data = f.read()
        if event_hash in log_data:
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
            print("→ Đang truy cập EVN để test Đông Anh - Nam Ban...")
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            await page.wait_for_selector("#tab-tab2")
            await page.click("#tab-tab2")
            await asyncio.sleep(3)

            await page.select_option("#idCongTyDienLuc", "PB03")
            await asyncio.sleep(4)
            await page.select_option("#idDienLuc", "PB0306")
            
            target_id = "#idThongTinLichNgungGiamMaDonVi"
            await page.wait_for_selector(target_id)
            await asyncio.sleep(7) 

            rows = await page.query_selector_all(f"{target_id} table tbody tr")
            
            found_any = False
            for row in rows:
                text = await row.inner_text()
                clean_text = text.strip()
                if not clean_text: continue

                for area in WATCH_AREAS:
                    thon = area["thon"].lower()
                    xa = area["xa"].lower()
                    
                    if thon in clean_text.lower() and xa in clean_text.lower():
                        found_any = True
                        if is_new_event(clean_text):
                            # SỬA LỖI SYNTAX Ở ĐÂY
                            msg = "⚡ <b>[TEST] LỊCH CÚP ĐIỆN ĐÔNG ANH</b>\n"
                            msg += "📍 <b>Khu vực:</b> " + area['thon'] + " - " + area['xa'] + "\n"
                            msg += "📝 <b>Chi tiết:</b> " + clean_text + "\n"
                            msg += "⏰ <b>Cập nhật:</b> " + datetime.now().strftime('%H:%M %d/%m/%Y')
                            
                            send_telegram(msg)
                            print("✅ Đã tìm thấy lịch Đông Anh và gửi Telegram!")
                        else:
                            print("⏭️ Lịch Đông Anh này đã gửi rồi.")
                        break

            if not found_any:
                print("🏁 ĐÃ QUÉT XONG: Hiện tại khu vực test không có lịch cúp điện.")

        except Exception as e:
            print("❌ Lỗi: " + str(e))
        finally:
            await browser.close()
            print("🔌 Đã đóng trình duyệt.")

if __name__ == "__main__":
    asyncio.run(run())
