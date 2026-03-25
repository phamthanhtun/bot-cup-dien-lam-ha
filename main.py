import requests
from bs4 import BeautifulSoup

def quet_evn_chuan_lam_dong():
    # Link này là link gửi yêu cầu lấy lịch riêng của Lâm Đồng
    url = "https://www.evnspc.vn/Lich-ngung-giam-cung-cap-dien-ket-qua-tra-cuu"
    
    # Thông số để "ép" web nó hiện đúng Lâm Đồng và huyện Lâm Hà
    # MA_DONVI: PB11LH là mã định danh của Điện lực Lâm Hà
    params = {
        'MaDonVi': 'PB11LH', 
        'TuNgay': '25/03/2026',
        'DenNgay': '01/04/2026'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
    }

    print("--- Đang kết nối thẳng tới Điện lực Lâm Hà ---")
    
    try:
        res = requests.post(url, data=params, headers=headers, timeout=20)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Tìm bảng dữ liệu
        rows = soup.find_all('tr')
        
        if len(rows) <= 1:
            print("Hiện tại chưa có lịch cúp điện mới nào cho Lâm Hà trong tuần tới.")
            return

        print(f"Tìm thấy {len(rows)-1} dòng dữ liệu:")
        for row in rows[1:]: # Bỏ qua dòng tiêu đề
            print(f"✅ {row.text.strip().replace('', ' ')}")
            
    except Exception as e:
        print(f"Lỗi kết nối: {e}")

if __name__ == "__main__":
    quet_evn_chuan_lam_dong()
