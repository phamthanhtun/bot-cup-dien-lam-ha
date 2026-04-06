from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import pandas as pd
from datetime import datetime
import time
import random
import os

def scrape_evnspc_lam_ha():
    url = "https://cskh.evnspc.vn/TraCuu/LichNgungCungCapDien"
    
    with sync_playwright() as p:
        # 1. Khởi tạo trình duyệt
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 900}
        )
        page = context.new_page()
        
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] --- Bắt đầu nhiệm vụ quét lịch Lâm Hà ---")
            
            # Mở trang và đợi load
            page.goto(url, wait_until="domcontentloaded", timeout=90000)
            print("✅ Đã kết nối tới EVNSPC")
            time.sleep(5)

            # 2. Chọn "Tìm kiếm theo đơn vị quản lý" (Sửa selector chuẩn của EVN)
            print("→ Đang chọn chế độ Tìm kiếm theo đơn vị...")
            page.wait_for_selector("input#rdoDonVi", timeout=30000)
            page.click("input#rdoDonVi", force=True)
            time.sleep(3)

            # 3. Chọn Công ty Điện lực Lâm Đồng (Mã chuẩn là PC15)
            print("→ Chọn Công ty: PC15 (Lâm Đồng)")
            page.select_option('#MaDonViCha', value='PC15')
            time.sleep(5) # Đợi danh sách huyện hiện ra

            # 4. Chọn Điện lực Lâm Hà (Mã chuẩn là PC15LL)
            print("→ Chọn Điện lực: PC15LL (Lâm Hà)")
            page.select_option('#MaDonVi', value='PC15LL')
            time.sleep(3)

            # 5. Nhấn nút Tra cứu
            print("→ Nhấn nút Tra cứu...")
            page.click("#btnTraCuu")
            
            # Đợi bảng dữ liệu xuất hiện
            print("→ Đang đợi hệ thống trả kết quả...")
            page.wait_for_selector("#KetQuaTraCuu", timeout=30000)
            time.sleep(2)

            # 6. Trích xuất dữ liệu và lưu file (Học tập Grok)
            data = []
            table = page.query_selector("#KetQuaTraCuu table")
            if table:
                rows = table.query_selector_all('tr')
                for row in rows[1:]: # Bỏ header
                    cols = row.query_selector_all('td')
                    if len(cols) >= 3:
                        texts = [c.inner_text().strip() for c in cols]
                        data.append({
                            "Thời gian": texts[1],
                            "Khu vực": texts[2],
                            "Lý do": texts[3] if len(texts) > 3 else "",
                            "Ngày cập nhật": datetime.now().strftime('%d/%m/%Y %H:%M')
                        })

            if data:
                # Lưu file CSV cho đại ca dễ quản lý (Giống Grok)
                df = pd.DataFrame(data)
                os.makedirs("data", exist_ok=True)
                filename = f"data/Lich_Cup_Dien_Lam_Ha_{datetime.now().strftime('%Y%m%d')}.csv"
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                
                print(f"\n🎉 THÀNH CÔNG RỒI ĐẠI CA!")
                print(f"Đã tìm thấy {len(data)} lịch cúp điện.")
                print(f"Dữ liệu đã lưu vào: {filename}")
                # In ra màn hình cho đại ca xem luôn
                print("-" * 50)
                for item in data:
                    print(f"🕒 {item['Thời gian']} | 📍 {item['Khu vực']}")
                print("-" * 50)
            else:
                print("⚠️ Hiện tại hệ thống báo không có lịch cúp điện nào cho Lâm Hà.")

        except Exception as e:
            print(f"❌ Lỗi rồi đại ca: {e}")
            page.screenshot(path="debug_error.png") # Chụp ảnh lại nếu lỗi
        finally:
            browser.close()
            print("--- Kết thúc ---")

if __name__ == "__main__":
    scrape_evnspc_lam_ha()
