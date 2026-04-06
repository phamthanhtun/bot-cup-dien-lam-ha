import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import urllib.request
import urllib.parse

# --- THÔNG TIN CHUẨN CỦA ĐẠI CA ---
TELEGRAM_TOKEN = "8400722845:AAHAMQnpd-Y11A1zKaaHMXbFp-YXcCRl254"
CHAT_ID = "7880436708"
MA_DON_VI = "PC15LL"

def send_telegram(message):
    try:
        msg = urllib.parse.quote(message)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=HTML"
        urllib.request.urlopen(url)
        print("✅ Đã gửi báo cáo về Telegram!")
    except Exception as e:
        print(f"❌ Lỗi Telegram: {e}")

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        try:
            print("→ Đang quét tổng lực tỉnh Lâm Đồng...")
            await page.goto("https://cskh.evnspc.vn/TraCuu/LichNgungCungCapDien", wait_until="networkidle", timeout=90000)
            await asyncio.sleep(5) 

            tu_ngay = datetime.now().strftime('%d/%m/%Y')
            # Quét mã PC15 (Toàn tỉnh Lâm Đồng)
            api_url = f"https://cskh.evnspc.vn/TraCuu/LayDuLieuLichNgungCungCapDien?MaDonViCha=PC15&MaDonVi=PC15&TuNgay={tu_ngay}&DenNgay=31/12/2026"
            
            data = await page.evaluate(f"""
                async () => {{
                    try {{
                        const response = await fetch("{api_url}");
                        return await response.json();
                    }} catch (e) {{
                        return null;
                    }}
                }}
            """)
            
            if data and 'data' in data and len(data['data']) > 0:
                # Lọc SIÊU NHẠY: Chấp cả viết hoa, viết thường, có dấu hay không dấu
                def check_lam_ha(item):
                    text_to_check = f"{item.get('TenDonVi', '')} {item.get('TenKhuVuc', '')}".lower()
                    # Quét cả từ khóa "lâm hà" và "lam ha" cho chắc cú
                    return "lâm hà" in text_to_check or "lam ha" in text_to_check

                lich_lam_ha = [item for item in data['data'] if check_lam_ha(item)]
                
                if len(lich_lam_ha) > 0:
                    # (Đoạn gửi tin nhắn giữ nguyên...)
                    msg = f"⚠️ <b>CÓ LỊCH CÚP ĐIỆN MỚI TẠI LÂM HÀ!</b>\n"
                    # ... copy lại đoạn for item in lich_lam_ha của sếp ...
                    send_telegram(msg)
                else:
                    # Sếp thêm dòng này để "soi" xem thực tế nó lấy được bao nhiêu lịch toàn tỉnh
                    tong_so = len(data['data'])
                    send_telegram(f"🔍 <b>SOI DỮ LIỆU:</b>\nĐã lấy được {tong_so} lịch toàn tỉnh nhưng không có cái nào khớp 'Lâm Hà'.")

        except Exception as e:
            print(f"Lỗi: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
