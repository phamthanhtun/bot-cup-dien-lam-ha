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
                # Lọc tất cả những gì có chữ "Lâm Hà" (không phân biệt Đội quản lý hay Điện lực huyện)
                lich_lam_ha = [item for item in data['data'] if "Lâm Hà" in str(item.get('TenDonVi', '')) or "Lâm Hà" in str(item.get('TenKhuVuc', ''))]
                
                if len(lich_lam_ha) > 0:
                    msg = f"⚠️ <b>CÓ LỊCH CÚP ĐIỆN MỚI TẠI LÂM HÀ!</b>\n"
                    msg += "--------------------------------\n"
                    for item in lich_lam_ha:
                        msg += f"🏢 <b>Đơn vị:</b> {item.get('TenDonVi')}\n"
                        msg += f"📍 <b>Khu vực:</b> {item.get('TenKhuVuc')}\n"
                        msg += f"⏰ <b>Thời gian:</b> {item.get('ThoiGian')}\n"
                        msg += f"📝 <b>Lý do:</b> {item.get('LyDo')}\n"
                        msg += "--------------------------------\n"
                    send_telegram(msg)
                else:
                    send_telegram(f"✅ <b>BOT BÁO CÁO:</b>\nĐã quét toàn tỉnh nhưng chưa thấy lịch nào ghi tên 'Lâm Hà' sếp ạ!")
            else:
                send_telegram(f"✅ <b>BOT BÁO CÁO:</b>\nHiện tại toàn tỉnh Lâm Đồng chưa có lịch mới.")

        except Exception as e:
            print(f"Lỗi: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
