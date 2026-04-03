import requests
from bs4 import BeautifulSoup
import time

def quet_lich_lam_ha():
    print("--- Đang kết nối trực tiếp tới cổng thông tin EVNSPC ---")
    
    # URL chính thức của trang tra cứu
    url = "https://cskh.evnspc.vn/TraCuu/LichNgungCungCapDien"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://cskh.evnspc.vn/"
    }

    session = requests.Session()

    try:
        # Bước 1: Lấy Token bảo mật từ trang chủ (để web không chặn bot)
        print("Bước 1: Khởi tạo phiên làm việc...")
        response = session.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Bước 2: Chuẩn bị dữ liệu để gửi đi (Mã PC15LL là Lâm Hà)
        # Em lấy dữ liệu trực tiếp bằng cách giả lập lệnh POST của trình duyệt
        post_url = "https://cskh.evnspc.vn/TraCuu/GetLichNgungCungCapDien"
        payload = {
            "maDonVi": "PC15LL", # Mã Điện lực Lâm Hà
            "tuNgay": time.strftime("%d/%m/%Y"), # Lấy từ ngày hôm nay
            "denNgay": "15/04/2026", # Quét đến giữa tháng 4
            "LoaiLich": "1"
        }
        
        headers.update({"X-Requested-With": "XMLHttpRequest"})

        print("Bước 2: Đang truy vấn lịch cúp điện Lâm Hà...")
        res = session.post(post_url, data=payload, headers=headers, timeout=30)

        if res.status_code == 200:
            print("\n" + "="*40)
            print("KẾT QUẢ TỪ HỆ THỐNG:")
            
            # Nếu có dữ liệu, nó sẽ trả về một đoạn mã HTML bảng lịch
            ket_qua = res.text
            if "KHU VỰC" in ket_qua or "Thời gian" in ket_qua:
                # Dùng BeautifulSoup để lọc bỏ các thẻ HTML cho đại ca dễ đọc
                clean_soup = BeautifulSoup(ket_qua, 'html.parser')
                print(clean_soup.get_text(separator='\n').strip())
            else:
                print("Hiện tại không có lịch cúp điện nào được ghi nhận tại Lâm Hà.")
            print("="*40)
        else:
            print(f"Lỗi: Server EVN phản hồi mã {res.status_code}")

    except Exception as e:
        print(f"Lỗi kết nối: {e}")

if __name__ == "__main__":
    quet_lich_lam_ha()
