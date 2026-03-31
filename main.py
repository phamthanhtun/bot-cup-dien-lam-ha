import asyncio
from playwright.async_api import async_playwright

async def quet_lich_lam_ha():
    async with async_playwright() as p:
        # Chạy headless=False nếu đại ca muốn hiện trình duyệt lên xem nó bấm
        browser = await p.chromium.launch(headless=True) 
        page = await browser.new_page()
        
        print("Đang truy cập EVNSPC...")
        await page.goto("https://cskh.evnspc.vn/TraCuu/LichNgungCungCapDien", wait_until="networkidle")

        # Bước 1: Click chọn Tìm kiếm theo đơn vị quản lý
        # Thường nó là Radio button hoặc Tab, em dùng text cho chắc
        await page.click("text='Tìm kiếm theo đơn vị quản lý'")
        
        # Bước 2: Chọn Công ty Điện lực Lâm Đồng (Mã thường là PC15)
        # Em dùng wait_for_selector để đợi nó load xong list
        await page.wait_for_selector("#MaDonViCha")
        await page.select_option("#MaDonViCha", label="Công ty Điện lực Lâm Đồng")
        
        # Bước 3: Đợi dropdown con cập nhật rồi chọn Lâm Hà
        await page.wait_for_timeout(2000) # Đợi 2s cho chắc cú
        await page.select_option("#MaDonVi", label="Điện lực Lâm Hà")
        
        # Bước 4: Nhấn nút Tìm kiếm
        await page.click("#btnTraCuu")
        
        # Bước 5: Đợi bảng kết quả hiện ra
        await page.wait_for_selector("#KetQuaTraCuu")
        
        # Bước 6: Hốt dữ liệu
        content = await page.inner_html("#KetQuaTraCuu")
        
        if "KHU VỰC" in content:
            print("Ngon rồi đại ca! Đã lấy được dữ liệu.")
            # Ở đây đại ca có thể dùng BeautifulSoup để bóc tách text đẹp hơn
            print(content)
        else:
            print("Bảng trống, có vẻ hôm nay Lâm Hà không mất điện.")

        await browser.close()

asyncio.run(quet_lich_lam_ha())
