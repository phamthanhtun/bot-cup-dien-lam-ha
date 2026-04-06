import asyncio
from playwright.async_api import async_playwright
import pandas as pd

async def run():
    async with async_playwright() as p:
        # Dùng User-Agent giả lập người dùng thật để tránh bị chặn
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = await context.new_page()
        
        try:
            print("--- Đang đột nhập web EVN ---")
            # Tăng timeout lên 90s vì mạng GitHub sang VN hơi lag
            await page.goto("https://cskh.evnspc.vn/TraCuu/LichNgungCungCapDien", timeout=90000)
            
            # Đợi cái form hiện ra, không click lung tung
            await page.wait_for_selector("#MaDonViCha", timeout=60000)
            
            # Chọn Lâm Đồng (PC15) và Lâm Hà (PC15LL)
            await page.select_option("#MaDonViCha", value="PC15")
            await asyncio.sleep(3) # Đợi huyện load
            await page.select_option("#MaDonVi", value="PC15LL")
            
            await page.click("#btnTraCuu")
            await page.wait_for_selector("#KetQuaTraCuu", timeout=30000)
            
            # In kết quả ra log cho sếp xem
            print("🎉 THÀNH CÔNG RỒI ĐẠI CA!")
            res = await page.inner_text("#KetQuaTraCuu")
            print(res[:500])
            
        except Exception as e:
            print(f"❌ Vẫn lỗi sếp ơi: {e}")
            await page.screenshot(path="loi_roi.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
