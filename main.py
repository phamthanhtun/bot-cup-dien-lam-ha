import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import hashlib
import requests
import os

# --- CẤU HÌNH TELEGRAM ---
TOKEN = "8400722845:AAHAMQnpd-Y11A1zKaaHMXbFp-YXcCRl254"
CHAT_ID = "7880436708"

# --- DANH SÁCH KHU VỰC CẦN THEO DÕI ---
WATCH_LIST = {
    "Vinh Quang": "Hoài Đức",
    "Vinh Quang": "Tân Hà",
}

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"❌ Lỗi gửi Telegram: {e}")

def is_new_event(event_str):
    """Kiểm tra xem lịch này đã gửi chưa bằng cách so sánh mã Hash"""
    # Tạo mã định danh duy nhất cho mỗi lịch (tránh trùng ngày/giờ/địa điểm)
    event_hash = hashlib.md5(event_str.encode('utf-8')).hexdigest()
    log_file = "sent_logs.txt"
    
    if not os.path.exists(log_file):
        with open(log_file, "w") as f: f.write("")

    with open(log_file, "r") as f:
        sent_hashes = f.read().splitlines()

    if event_hash not in sent_hashes:
        with open(log_file, "a") as f:
            f.write(event_hash + "\n")
        return True
    return False

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True) # Chạy ẩn cho chuyên nghiệp
        page = await browser.new_page()

        url = "https://www.cskh.evnspc.vn/TraCuu/LichNgungGiamCungCapDien"
        await page.goto(url, wait_until="networkidle")

        await page.click("#tab-tab2")
        await asyncio.sleep(1)
        await page.select_option("#Id_DonViPhanPhoi", label="Công ty Điện lực Lâm Đồng")
        await page.select_option("#Id_DonViQuanLy", value="PB0306")
        await asyncio.sleep(3)

        rows = await page.query_selector_all("#LichNgungCungCapDienKhuVuc table tbody tr")
        
        for row in rows:
            cols = await row.query_selector_all("td")
            if len(cols) >= 5:
                ngay = await cols[1].inner_text()
                gio = await cols[2].inner_text()
                dia_diem = await cols[3].inner_text()
                ly_do = await cols[4].inner_text()
                
                for thon, xa in WATCH_LIST.items():
                    if thon.lower() in dia_diem.lower() and xa.lower() in dia_diem.lower():
                        # Tạo chuỗi nội dung để kiểm tra trùng
                        content = f"{ngay}-{gio}-{dia_diem}"
                        
                        if is_new_event(content):
                            msg = (f"🔔 <b>CÓ LỊCH CÚP ĐIỆN MỚI!</b>\n"
                                   f"📍 Khu vực: {thon} - {xa}\n"
                                   f"📅 Ngày: {ngay}\n"
                                   f"⏰ Giờ: {gio}\n"
                                   f"🛠 Lý do: {ly_do}\n"
                                   f"---")
                            send_telegram(msg)
                            print(f"✅ Đã gửi tin nhắn mới cho: {thon}")
                        else:
                            print(f"⏭️ Lịch ngày {ngay} tại {thon} đã gửi rồi, bỏ qua.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
