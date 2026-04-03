import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def quet_lich_lam_ha():
    print("--- Đang khởi động trình quét lịch Lâm Hà ---")
    
    # Cấu hình Chrome chạy ẩn danh và nhẹ nhất có thể
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print("Đang truy cập web EVNSPC...")
        driver.get("https://cskh.evnspc.vn/TraCuu/LichNgungCungCapDien")
        
        # 1. Đợi và chọn "Tìm kiếm theo đơn vị quản lý"
        print("Bước 1: Chọn tìm theo đơn vị...")
        radio = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "rdoDonVi")))
        driver.execute_script("arguments[0].click();", radio) # Dùng Script để click cho chắc
        time.sleep(2)

        # 2. Chọn Công ty Điện lực Lâm Đồng (PC15)
        print("Bước 2: Chọn PC Lâm Đồng...")
        select_cty = Select(driver.find_element(By.ID, "MaDonViCha"))
        select_cty.select_by_value("PC15")
        time.sleep(3) # Đợi danh sách huyện load

        # 3. Chọn Điện lực Lâm Hà (PC15LL)
        print("Bước 3: Chọn ĐL Lâm Hà...")
        select_huyen = Select(driver.find_element(By.ID, "MaDonVi"))
        select_huyen.select_by_value("PC15LL")

        # 4. Bấm nút Tra cứu
        print("Bước 4: Nhấn nút Tra cứu...")
        btn = driver.find_element(By.ID, "btnTraCuu")
        driver.execute_script("arguments[0].click();", btn)

        # 5. Đợi bảng kết quả hiện ra
        print("Bước 5: Đang lấy kết quả...")
        time.sleep(5)
        ket_qua = driver.find_element(By.ID, "KetQuaTraCuu").text

        if "KHU VỰC" in ket_qua or "Thời gian" in ket_qua:
            print("\n" + "="*30)
            print("NGON RỒI ĐẠI CA! KẾT QUẢ ĐÂY:")
            print(ket_qua)
            print("="*30)
        else:
            print("\nHiện tại Lâm Hà không có lịch cúp điện.")

    except Exception as e:
        print(f"\nLỗi rồi đại ca: {e}")
    finally:
        driver.quit()
        print("--- Hoàn tất ---")

if __name__ == "__main__":
    quet_lich_lam_ha()
