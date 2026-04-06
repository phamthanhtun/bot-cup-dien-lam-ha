import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

async def run():
    async with async_playwright() as p:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] --- Đang khởi động Bot ---")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            # 1. Truy cập trang để lấy "giấy thông hành" (Cookie)
            print("→ Đang kết nối EVNSPC...")
            await page.goto("https://cskh.evnspc.vn/TraCuu/LichNgungCungCapDien", wait_until="networkidle", timeout=60000)
            await asyncio.sleep(2)

            # 2. Gọi API lấy dữ liệu thô (Dùng bọc try-except để không bị crash)
            tu_ngay = datetime.now().strftime('%d/%m/%Y')
            api_url = f"https://cskh.evnspc.vn/TraCuu/LayDuLieuLichNgungCungCapDien?MaDonViCha=PC15&MaDonVi=PC15LL&TuNgay={tu_ngay}&DenNgay=31/12/2026"
            
            print(f"→ Đang quét lịch Lâm Hà từ ngày {tu_ngay}...")
            
            # Thực thi fetch dữ liệu
            response_json = await page.evaluate(f"""
                async () => {{
                    try {{
                        const r = await fetch("{api_url}");
                        if (!r.ok) return null;
                        return await r.json();
                    }} catch (e) {{ return null; }}
                }}
            """)

            # 3. Xử lý kết quả
            if response_json and 'data' in response_json and len(response_json['data']) > 0:
                print(f"🎉 PHÁT HIỆN CÓ {len(response_json['data'])} LỊCH CÚP ĐIỆN TẠI LÂM HÀ!")
                print("-" * 50)
                for item in response_json['data']:
                    print(f"📍 Khu vực: {item.get('TenKhuVuc', 'N/A')}")
                    print(f"⏰ Thời gian: {item.get('ThoiGian', 'N/A')}")
                    print(f"📝 Lý do: {item.get('LyDo', 'N/A')}")
                    print("-" * 20)
            else:
                print("✅ Hiện tại chưa ghi nhận lịch cúp điện mới cho Lâm Hà, đại ca yên tâm nhé!")

        except Exception as e:
            print(f"❌ Có chút trục trặc nhỏ: {e}")
        finally:
            await browser.close()
            print("\n--- Hoàn thành. Bấm phím bất kỳ để tắt bảng ---")

if __name__ == "__main__":
    asyncio.run(run())
