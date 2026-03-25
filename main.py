import requests

def nam_vung_evn():
    # Đây là cổng API nội bộ (Endpoint) thường ít bị chặn hơn web giao diện
    url = "https://api.evnspc.vn/api/LichNgungGiamCungCapDien/GetLichNgungGiamCungCapDien"
    
    # Payload nhắm thẳng vào mã Điện lực Lâm Hà (PB11LH)
    # Thời gian từ hôm nay đến 7 ngày tới
    data = {
        "maDonVi": "PB11LH",
        "tuNgay": "2026-03-25",
        "denNgay": "2026-04-01",
        "loaiLich": "0"
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0"
    }

    print("--- Đang đột nhập vào hệ thống dữ liệu Lâm Hà ---")
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        if response.status_code == 200:
            ket_qua = response.json()
            if not ket_qua or len(ket_qua) == 0:
                print("Hệ thống báo: Hiện tại Lâm Hà chưa có lịch cúp điện mới nào đăng ký trên server.")
            else:
                print(f"✅ ĐÃ TÓM ĐƯỢC {len(ket_qua)} THÔNG TIN:")
                for item in ket_qua:
                    print(f"- Khu vực: {item.get('TenKhuVuc')}")
                    print(f"  Thời gian: {item.get('ThoiGian')}")
                    print(f"  Lý do: {item.get('LyDo')}")
                    print("-" * 20)
        else:
            print(f"Bị chặn cửa rồi đại ca: Mã lỗi {response.status_code}")
            
    except Exception as e:
        print(f"Lỗi nằm vùng: {e}")

if __name__ == "__main__":
    nam_vung_evn()
