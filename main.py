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

# Danh sách lọc chuẩn theo cặp để không nhầm xã
WATCH_AREAS = [
    {"thôn": "Đông Anh", "xa": "Nam Ban Lâm Hà"},
    {"thôn": "Đông Anh", "xa": "Nam Ban Lâm Hà"}
]

def send_telegram(message):
    try:
        msg = urllib.parse.quote(message)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=HTML"
        urllib.request.urlopen(url)
    except Exception as e:
        print(f"Lỗi gửi Tele: {e}")

def is_new_event(content):
    event_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f: pass
    
    with open(LOG_FILE, "r") as f:
        if event_hash in f.read():
            return False
            
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
            print(f"→ Truy cập hệ thống...")
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Bước 1: Chuyển Tab
            await page.wait_for_selector("#tab-tab2")
            await page.click("#tab-tab2")
            await asyncio.sleep(3)

            # Bước 2: Chọn đơn vị (Sử dụng ID đại ca đã xác nhận OK)
            await page.select_option("#idCongTyDienLuc", "PB03")
            await asyncio.sleep(4)
            await page.select_option("#idDienLuc", "PB0306")
            
            # Bước 3: Đợi bảng dữ liệu hiện ra hoàn toàn
            target_id = "#idThongTinLichNgungGiamMaDonVi"
            await page.wait_for_selector(target_id)
            
            # Cuộn nhẹ trang để kích hoạt nạp đầy đủ dữ liệu
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
            await asyncio.sleep(5) 

            # Bước 4: Lấy dữ liệu cực kỳ cẩn thận
            rows = await page.query_selector_all(f"{target_id} table tbody tr")
            
            for row in rows:
                text = await row.inner_text()
                clean_text = text.strip()
                
                if not clean_text: continue # Bỏ qua hàng trống
                
                # Logic lọc chính xác theo cặp Thôn - Xã
                for area in WATCH_AREAS:
                    thon = area["thon"].lower()
                    xa = area["xa"].lower()
                    
                    if thon in clean_text.lower() and xa in clean_text.lower():
                        if is_new_event(clean_text):
                            msg = (f"🔔 <b>THÔNG BÁO CẮT ĐIỆN</b>\n"
                                   f"📍 <b>Khu vực:</b> {area['thon']} - {area['xa']}\n"
                                   f"📝 <b>Chi tiết:</b> {clean_text}\n"
                                   f"⏰ <b>Cập nhật:</b> {datetime.now().strftime('%H:%M %d/%m/%Y')}")
                            send_telegram(msg)
                            print(f"✅ Đã báo cáo: {area['thon']}")
                        break # Tìm thấy rồi thì không cần check cặp khác cho hàng này

        except Exception as e:
            print(f"❌ Rà soát phát hiện lỗi: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
