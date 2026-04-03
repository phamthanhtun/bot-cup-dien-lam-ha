import requests
import json

def quet_lich_tructiep():
    print("--- Đang kết nối thẳng vào API của EVNSPC ---")
    
    # URL API lấy lịch cúp điện của EVNSPC
    url = "https://cskh.evnspc.vn/TraCuu/GetLichNgungCungCapDien"
    
    # Mã đơn vị: PC15 (Lâm Đồng), PC15LL (Lâm Hà)
    payload = {
        "maDonVi": "PC15LL",
        "tuNgay": "03/04/2026",
        "denNgay": "10/04/2026",
        "LoaiLich": "1"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        response = requests.post(url, data=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.text
            print("\nNGON RỒI ĐẠI CA! ĐÃ KẾT NỐI THÀNH CÔNG.")
            
            if "KHU VỰC" in data or "Thời gian" in data:
                print("-" * 30)
                # In ra dữ liệu thô để đại ca xem trước
                print(data) 
                print("-" * 30)
            else:
                print("Hiện tại Lâm Hà không có lịch cúp điện nào từ 03/04 đến 10/04.")
        else:
            print(f"Server EVN phản hồi lỗi: {response.status_code}")
            
    except Exception as e:
        print(f"Lỗi kết nối: {e}")

if __name__ == "__main__":
    quet_lich_tructiep()
