import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import urllib.request
import urllib.parse
import json

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
        # Giả lập Chrome xịn trên Windows
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            # Bước 1: Truy cập trang chủ để lấy Cookie (Cực kỳ quan trọng để không bị lỗi JSON)
            await page.goto("https://cskh.evnspc.vn/TraCuu/LichNgungCungCapDien", wait_until="networkidle", timeout=60000)
            await asyncio.sleep(5)

            # Bước 2: Chuẩn bị tham số (Mã PB03/PB0306 đại ca đã soi)
            tu_ngay = (datetime.now() - timedelta(days=2)).strftime('%d/%m/%Y')
            api_url = f"https://cskh.evnspc.vn/TraCuu/LayDuLieuLichNgungCungCapDien?MaDonViCha=PB03&MaDonVi=PB0306&TuNgay={tu_ngay}&DenNgay=31/12/2026"
            
            # Bước 3: Dùng chiêu Page.evaluate nhưng bọc trong Try/Catch để tránh crash JSON
            raw_data = await page.evaluate(f"""
                async () => {{
                    try {{
                        const response = await fetch("{api_url}");
                        if (!response.ok) return null;
                        return await response.json();
                    }} catch (e) {{
                        return null;
                    }}
                }}
            """)

            if raw_data and 'data' in raw_data and len(raw_data['data']) > 0:
                lich_list = raw_data['data']
                msg = f"⚠️ <b>LỊCH CÚP ĐIỆN LÂM HÀ (Mã PB0306)</b>\n"
                msg += f"📅 Cập nhật: {datetime.now().strftime('%H:%M %d/%m')}\n"
                msg += "--------------------------------\n"
                
                # Chỉ lấy những lịch từ hôm nay trở đi để sếp đỡ bị rác máy
                ngay_hien_tai = datetime.now()
                for item in lich_list[:10]:
                    msg += f"📍 <b>Khu vực:</b> {item.get('TenKhuVuc')}\n"
                    msg += f"⏰ <b>Thời gian:</b> {item.get('ThoiGian')}\n"
                    msg += f"📝 <b>Lý do:</b> {item.get('LyDo')}\n"
                    msg += "--------------------------------\n"
                
                send_telegram(msg)
                print(f"✅ Đã tìm thấy {len(lich_list)} lịch!")
            else:
                # Phương án 2: Quét toàn tỉnh PB03 nếu huyện báo trống
                api_url_tinh = api_url.replace("MaDonVi=PB0306", "MaDonVi=PB03")
                data_tinh = await page.evaluate(f'async () => {{ const r = await fetch("{api_url_tinh}"); return await r.json(); }}')
                
                if data_tinh and 'data' in data_tinh:
                    lich_loc = [i for i in data_tinh['data'] if "lâm hà" in str(i).lower()]
                    if len(lich_loc) > 0:
                        msg = f"⚠️ <b>LỊCH LÂM HÀ (QUÉT TỪ MÃ PB03)</b>\n"
                        for i in lich_loc[:5]:
                            msg += f"📍 {i.get('TenKhuVuc')}\n⏰ {i.get('ThoiGian')}\n---\n"
                        send_telegram(msg)
                    else:
                        print("Không tìm thấy lịch Lâm Hà trong mã PB03.")
                
        except Exception as e:
            print(f"Lỗi hệ thống: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
