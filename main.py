import requests
from bs4 import BeautifulSoup

def quet_evn():
    url = "https://www.evnspc.vn/Lich-ngung-giam-cung-cap-dien"
    # Thêm cái 'headers' này để giả làm trình duyệt Chrome, đánh lừa web EVN
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # In thử để kiểm tra xem có lấy được chữ nào không
        print("Đang quét dữ liệu...")
        
        found = False
        for row in soup.find_all('tr'):
            if "Lâm Hà" in row.text:
                print(f"✅ PHÁT HIỆN LỊCH: {row.text.strip()}")
                found = True
        
        if not found:
            print("Hôm nay web chưa có lịch mới cho Lâm Hà hoặc chưa quét được bảng.")
            
    except Exception as e:
        print(f"Lỗi rồi đại ca ơi: {e}")

if __name__ == "__main__":
    quet_evn()
