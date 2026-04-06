import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import urllib.request
import urllib.parse

# --- THÔNG TIN CHUẨN CỦA ĐẠI CA ---
TELEGRAM_TOKEN = "8400722845:AAHAMQnpd-Y11A1zKaaHMXbFp-YXcCRl254"
CHAT_ID = "7880436708"

def send_telegram(message):
    try:
        msg = urllib.parse.quote(message)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=HTML"
        urllib.request.urlopen(url)
    except Exception as e:
        print(f"❌ Lỗi Telegram: {e}")

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        try:
            print("→ Đang truy quét trực tiếp trên giao diện web...")
            await page.goto("https://cskh.evnspc.vn/TraCuu/LichNgungCungCapDien", wait_until="networkidle", timeout=90000)
            
            # Bước 1: Chọn tỉnh Lâm Đồng
            await page.select_option("#MaDonViCha", "PC15")
            await asyncio.sleep(2)
            
            # Bước 2: Chọn Điện lực Lâm Hà (Mã này bao gồm cả các đội quản lý)
            await page.select_option("#MaDonVi", "PC15LL")
            await asyncio.sleep(2)
            
            # Bước 3: Nhấn nút Tra cứu
            await page.click("#btTraCuu")
            await asyncio.sleep(5) # Đợi bảng hiện ra

            # Bước 4: Quét trực tiếp dữ liệu từ bảng (Table)
            rows = await page.query_selector_all("table#DungCungCapDienTable tbody tr")
            
            lich_moi = []
            for row in rows:
                cols = await row.query_selector_all("td")
                if len(cols) >= 5:
                    area = await cols[2].inner_text() # Khu vực
                    time = await cols[3].inner_text() # Thời gian
                    reason = await cols[4].inner_text() # Lý do
                    lich_moi.append({
                        "area": area.strip(),
                        "time": time.strip(),
                        "reason": reason.strip()
                    })

            if len(lich_moi) > 0:
                msg = f"⚠️ <b>PHÁT HIỆN {len(lich_moi)} LỊCH CÚP ĐIỆN LÂM HÀ!</b>\n"
                msg += "--------------------------------\n"
                for item in lich_moi[:8]: # Gửi 8 cái đầu tiên
                    msg += f"📍 <b>Khu vực:</b> {item['area']}\n"
                    msg += f"⏰ <b>Thời gian:</b> {item['time']}\n"
                    msg += f"📝 <b>Lý do:</b> {item['reason']}\n"
                    msg += "--------------------------------\n"
                
                if len(lich_moi) > 8:
                    msg += f"<i>... và còn {len(lich_moi)-8} lịch khác trên hệ thống.</i>"
                
                send_telegram(msg)
                print(f"✅ Đã gửi {len(lich_moi)} lịch về Telegram.")
            else:
                send_telegram("✅ Đã quét giao diện web: Hiện tại chưa thấy lịch mới được hiển thị.")

        except Exception as e:
            print(f"Lỗi: {e}")
            send_telegram(f"❌ Bot gặp lỗi khi quét web: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
