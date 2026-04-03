import asyncio
from playwright.async_api import async_playwright

async def quet_lich_lam_ha():
    async with async_playwright() as p:
        # Khởi tạo trình duyệt
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("Đang truy cập EVNSPC...")
        try:
            # Truy cập trang tra cứu và đợi mạng ổn định
            await page.goto("https://cskh.evnspc.vn/TraCuu/LichNgungCungCapDien", wait_until="networkidle", timeout=60000)

            # Bước 1: Chọn "Tìm kiếm theo đơn vị quản lý" bằng ID cho chính xác
            print("Bước 1: Chọn tìm kiếm theo đơn vị...")
            await page.wait_for_selector("#rdoDonVi", timeout=30000)
            await page.click("#rdoDonVi")

            # Bước 2: Chọn Công ty Điện lực Lâm Đồng (Mã PC15)
            print("Bước 2: Chọn Công ty Điện lực Lâm Đồng...")
            await page.wait_for_selector("#MaDonViCha")
            await page.select_option("#MaDonViCha", value="PC15")

            # Bước 3: Đợi dropdown con cập nhật rồi chọn Điện lực Lâm Hà (Mã PC15LL)
            print("Bước 3: Chọn Điện lực Lâm Hà...")
            await page.wait_for_timeout(2000) # Đợi 2s để danh sách con load xong
            await page.wait_for_selector("#MaDonVi")
            await page.select_option("#MaDonVi", value="PC15LL")

            # Bước 4: Nhấn nút Tìm kiếm
            print("Bước 4: Nhấn nút Tra cứu...")
            await page.click("#btnTraCuu")

            # Bước 5: Đợi bảng kết quả hiện ra
            print("Bước 5: Đang lấy dữ liệu...")
            await page.wait_for_selector("#KetQuaTraCuu", timeout=30000)
            
            # Bước 6: Hốt dữ liệu
            content = await page.inner_html("#KetQuaTraCuu")

            if "KHU VỰC" in content:
                print("Ngon rồi đại ca! Đã lấy được dữ liệu.")
                # Đại ca có thể thêm code gửi Telegram ở đây
                print(content)
            else:
                print("Không có lịch cúp điện hoặc trang web trống.")

        except Exception as e:
            print(f"Lỗi rồi đại ca ơi: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(quet_lich_lam_ha())
