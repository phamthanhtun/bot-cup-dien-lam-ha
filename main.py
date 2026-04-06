import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
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
            print("→ Đang truy cập hệ thống EVNSPC...")
            await page.goto("https://cskh.evnspc.vn/TraCuu/LichNgungCungCapDien", wait_until="networkidle", timeout=90000)
            await asyncio.sleep(5) 

            # LÙI 2 NGÀY ĐỂ TÓM CẢ LỊCH VỪA DIỄN RA
            tu_ngay = (datetime.now() - timedelta(days=2)).strftime('%d/%m/%Y')
            
            # CHIÊU MỚI: Quét đồng thời cả mã huyện và mã đội quản lý
            # PC15LL: Điện lực Lâm Hà | PC15LL01: Đội quản lý điện Lâm Hà
            danh_sach_ma = ["PC15LL", "PC15LL01", "PC15LL02", "PC15LL03"]
            
            ket_qua_tong = []
            
            for ma in danh_sach_ma:
                api_url = f"https://cskh.evnspc.vn/TraCuu/LayDuLieuLichNgungCungCapDien?MaDonViCha=PC15&MaDonVi={ma}&TuNgay={tu_ngay}&DenNgay=31/12/2026"
                
                data = await page.evaluate(f"""
                    async () => {{
                        try {{
                            const response = await fetch("{api_url}");
                            const result = await response.json();
                            return result;
                        }} catch (e) {{
                            return null;
                        }}
                    }}
                """)
                
                if data and 'data' in data:
                    ket_qua_tong.extend(data['data'])

            # Lọc bỏ trùng lặp (nếu có)
            seen = set()
            lich_duy_nhat = []
            for item in ket_qua_tong:
                identifier = f"{item.get('ThoiGian')}-{item.get('TenKhuVuc')}"
                if identifier not in seen:
                    lich_duy_nhat.append(item)
                    seen.add(identifier)

            if len(lich_duy_nhat) > 0:
                # Sắp xếp theo thời gian
                lich_duy_nhat.sort(key=lambda x: x.get('ThoiGian', ''))
                
                msg = f"⚠️ <b>PHÁT HIỆN LỊCH CÚP ĐIỆN LÂM HÀ!</b>\n"
                msg += f"📅 <i>Dữ liệu cập nhật: {datetime.now().strftime('%H:%M %d/%m')}</i>\n"
                msg += "--------------------------------\n"
                
                # Gửi tối đa 8 lịch mới nhất để không bị quá tải tin nhắn
                for item in lich_duy_nhat[:8]:
                    msg += f"📍 <b>Khu vực:</b> {item.get('TenKhuVuc')}\n"
                    msg += f"⏰ <b>Thời gian:</b> {item.get('ThoiGian')}\n"
                    msg += f"📝 <b>Lý do:</b> {item.get('LyDo')}\n"
                    msg += "--------------------------------\n"
                
                if len(lich_duy_nhat) > 8:
                    msg += f"<i>... và còn {len(lich_duy_nhat)-8} lịch khác sếp nhé!</i>"
                
                send_telegram(msg)
                print(f"✅ Đã tìm thấy {len(lich_duy_nhat)} lịch!")
            else:
                print("Vẫn chưa thấy lịch trên hệ thống API.")

        except Exception as e:
            print(f"Lỗi: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
