import asyncio
from playwright.async_api import async_playwright

async def quet_lich_lam_ha():
    async with async_playwright() as p:
        # Bước 0: Khởi tạo trình duyệt với User-Agent để tránh bị chặn
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()

        print("--- Đang bắt đầu quét lịch cúp điện Lâm Hà ---")
        try:
            # 1. Truy cập trang web (đợi tối đa 90 giây cho mạng lag)
            print("Đang kết nối tới EVNSPC...")
            await page.goto("https://cskh.evnspc.vn/TraCuu/LichNgungCungCapDien", wait_until="domcontentloaded", timeout=90000)
            
            # Đợi thêm 5 giây cho các thành phần ẩn hiện ra hết
            await page.wait_for_timeout(5000) 

            # 2. Chọn "Tìm kiếm theo đơn vị quản lý"
            print("Bước 1: Chọn chế độ tìm kiếm theo đơn vị...")
            # Dùng Selector mạnh hơn để ép nó phải nhận diện được nút tròn
            radio_selector = "input#rdoDonVi"
            await page.wait_for_selector(radio_selector, state="attached", timeout=60000)
            await page.click(radio_selector, force=True)
            await page.wait_for_timeout(2000)

            # 3. Chọn Công ty Điện lực Lâm Đồng (Mã PC15)
            print("Bước 2: Chọn Công ty Điện lực Lâm Đồng...")
            await page.wait_for_selector("#MaDonViCha")
            await page.select_option("#MaDonViCha", value="PC15")
            await page.wait_for_timeout(3000) # Đợi danh sách con tải về

            # 4. Chọn Điện lực Lâm Hà (Mã PC15LL)
            print("Bước 3: Chọn Điện lực Lâm Hà...")
            await page.wait_for_selector("#MaDonVi")
            await page.select_option("#MaDonVi", value="PC15LL")

            # 5. Nhấn nút Tìm kiếm (Tra cứu)
            print("Bước 4: Nhấn nút Tra cứu...")
            await page.click("#btnTraCuu")

            # 6. Đợi bảng kết quả (đợi tối đa 30 giây)
            print("Bước 5: Đang chờ kết quả từ hệ thống...")
            await page.wait_for_selector("#KetQuaTraCuu", timeout=30000)
            
            # 7. Lấy nội dung kết quả
            content = await page.inner_text("#KetQuaTraCuu")

            if "KHU VỰC" in content or "Thời gian" in content:
                print("\nNGON RỒI ĐẠI CA! KẾT QUẢ ĐÂY:")
                print("-" * 30)
                print(content)
                print("-" * 30)
            else:
                print("\nHiện tại không có lịch cúp điện nào được tìm thấy cho Lâm Hà.")

        except Exception as e:
            print(f"\nLỗi rồi đại ca ơi: {e}")
            # Chụp ảnh màn hình lúc lỗi để đại ca xem bot đang thấy gì (nếu cần)
            await page.screenshot(path="error_debug.png")
        
        finally:
            await browser.close()
            print("--- Kết thúc quá trình quét ---")

if __name__ == "__main__":
    asyncio.run(quet_lich_lam_ha())
