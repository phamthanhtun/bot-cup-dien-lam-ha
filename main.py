import requests
from bs4 import BeautifulSoup

def quet_chot_ha():
    # Sử dụng trang tổng hợp lịch cúp điện (thường ít bảo mật hơn web chính EVN)
    url = "https://lichcupdien.com.vn/lich-cup-dien-lam-dong.html"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    print("--- Đang quét lịch Lâm Đồng (Trang tổng hợp) ---")
    
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Tìm tất cả các bảng hoặc thẻ chứa thông tin
        items = soup.find_all(['tr', 'div'], class_=['event-item', 'row'])
        
        found = False
        for item in items:
            text = item.get_text()
            if "Lâm Hà" in text:
                print(f"✅ ĐÃ CHÍN: {text.strip()}")
                found = True
        
        if not found:
            print("Kết quả: Hiện tại trên hệ thống chưa có lịch cúp điện mới nào được đăng tải cho Lâm Hà.")
            
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    quet_chot_ha()
