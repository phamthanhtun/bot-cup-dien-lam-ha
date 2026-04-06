import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime

async def quet_lich():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            print("--- Đang truy cập EVNSPC ---")
            await page.goto("https://cskh.evnspc.vn/TraCuu/LichNgungCungCapDien", timeout=60000)
            
            # Bước 1: Click chọn "Tìm kiếm theo đơn vị quản lý" bằng chữ
            print("→ Chọn chế độ tìm kiếm...")
            await page.click("text='Tìm kiếm theo đơn vị quản lý'", timeout=30000)
            await asyncio.sleep(2)

            # Bước 2: Chọn Công ty Lâm Đồng (PC15)
            await page.select_option("#MaDonViCha", value="PC15")
            await asyncio.sleep(3)

            # Bước 3: Chọn Điện lực Lâm Hà (PC15LL)
            await page.select_option("#MaDonVi", value="PC15LL")
            
            # Bước 4: Nhấn nút Tra cứu
            await page.click("#btnTraCuu")
            
            # Bước 5: Đợi bảng kết quả
            await page.wait_for_selector("#KetQuaTraCuu", timeout=20000)
            print("✅ Đã thấy bảng kết quả!")
            
            # Hốt dữ liệu (In ra log để sếp sướng)
            content = await page.inner_text("#KetQuaTraCuu")
            print(content[:500]) 

        except Exception as e:
            print(f"❌ Lỗi rồi đại ca: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(quet_lich())
