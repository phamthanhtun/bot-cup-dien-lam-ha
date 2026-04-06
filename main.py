import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
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
        browser = await p.chromium.launch(headless=True)
        # Giả lập máy tính thật để tránh bị chặn
        context = await browser.new_context(viewport={'width': 1280, 'height': 1200})
        page = await context.new_page()
        
        try:
            print("→ Đang truy cập trực tiếp diện mạo web EVN...")
            await page.goto("https://cskh.evnspc.vn/TraCuu/LichNgungCungCapDien", wait_until="networkidle", timeout=60000)
            
            # Tự tay điền mã PB03 và PB0306 như sếp chỉ
            await page.select_option("#idCongTyDienLuc", "PB03")
            await asyncio.sleep(2)
            await page.select_option("#idDienLuc", "PB0306")
            await asyncio.sleep(2)
            
            # Nhấn nút tra cứu
            await page.click("#btnTraCuu")
            await asyncio.sleep(5) # Đợi nó nạp bảng

            # CHIÊU MỚI: Quét trực tiếp các hàng (Row) trong bảng hiển thị
            rows = await page.query_selector_all("table tbody tr")
            
            if len(rows) > 0:
                ket_qua = []
                for row in rows:
                    cells = await row.query_selector_all("td")
                    if len(cells) >= 5:
                        khu_vuc = await cells[2].inner_text()
                        thoi_gian = await cells[3].inner_text()
                        ly_do = await cells[4].inner_text()
                        ket_qua.append(f"📍 <b>{khu_vuc.strip()}</b>\n⏰ {thoi_gian.strip()}\n📝 {ly_do.strip()}")

                if ket_qua:
                    msg = f"⚠️ <b>LỊCH CÚP ĐIỆN LÂM HÀ (QUÉT TRỰC TIẾP)</b>\n"
                    msg += f"📅 Cập nhật: {datetime.now().strftime('%H:%M %d/%m')}\n"
                    msg += "--------------------------------\n"
                    msg += "\n--------------------------------\n".join(ket_qua[:8]) # Lấy 8 cái mới nhất
                    send_telegram(msg)
                    print("✅ Đã tóm được lịch từ bảng web!")
                else:
                    send_telegram("🚀 Đã vào được bảng nhưng có vẻ chưa có lịch mới cho Lâm Hà đại ca ạ.")
            else:
                send_telegram("❌ Web hiện bảng trống hoặc bị lỗi hiển thị rồi sếp ơi.")

        except Exception as e:
            print(f"Lỗi: {e}")
            # Nếu lỗi, chụp cái ảnh màn hình gửi Telegram cho sếp xem luôn
            await page.screenshot(path="error.png")
            send_telegram(f"❌ Bot bị 'loạn thị' do: {str(e)[:50]}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
