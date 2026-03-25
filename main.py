import requests
from bs4 import BeautifulSoup

def quet_evn():
    url = "https://www.evnspc.vn/Lich-ngung-giam-cung-cap-dien"
    # Đại ca có thể thay bằng link tra cứu cụ thể của Lâm Đồng nếu có
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # Logic: Tìm bảng và lọc chữ "Lâm Hà"
    for row in soup.find_all('tr'):
        if "Lâm Hà" in row.text:
            print(f"PHÁT HIỆN LỊCH: {row.text.strip()}")

if __name__ == "__main__":
    quet_evn()
