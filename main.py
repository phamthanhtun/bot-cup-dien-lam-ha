try:
            print("→ Đang quét đúng mã PB0306 (Lâm Hà) theo chỉ đạo của Đại ca...")
            # Truy cập trang để lấy session
            await page.goto("https://cskh.evnspc.vn/TraCuu/LichNgungCungCapDien", wait_until="networkidle")
            await asyncio.sleep(2)

            tu_ngay = (datetime.now() - timedelta(days=2)).strftime('%d/%m/%Y')
            
            # SỬ DỤNG MÃ CHUẨN ĐẠI CA VỪA SOI: PB03 (Lâm Đồng) và PB0306 (Lâm Hà)
            api_url = f"https://cskh.evnspc.vn/TraCuu/LayDuLieuLichNgungCungCapDien?MaDonViCha=PB03&MaDonVi=PB0306&TuNgay={tu_ngay}&DenNgay=31/12/2026"
            
            data = await page.evaluate(f'async () => {{ const r = await fetch("{api_url}"); return await r.json(); }}')

            if data and 'data' in data and len(data['data']) > 0:
                msg = f"⚠️ <b>LỊCH CÚP ĐIỆN LÂM HÀ (MÃ PB0306)</b>\n"
                msg += "--------------------------------\n"
                for item in data['data'][:10]:
                    msg += f"📍 <b>Khu vực:</b> {item.get('TenKhuVuc')}\n"
                    msg += f"⏰ <b>Thời gian:</b> {item.get('ThoiGian')}\n"
                    msg += f"📝 <b>Lý do:</b> {item.get('LyDo')}\n"
                    msg += "--------------------------------\n"
                send_telegram(msg)
                print(f"✅ Đã tìm thấy {len(data['data'])} lịch!")
            else:
                # Nếu vẫn không ra, quét rộng ra cả mã tỉnh PB03 rồi tự lọc
                print("Thử quét toàn tỉnh PB03...")
                api_url_tinh = f"https://cskh.evnspc.vn/TraCuu/LayDuLieuLichNgungCungCapDien?MaDonViCha=PB03&MaDonVi=PB03&TuNgay={tu_ngay}&DenNgay=31/12/2026"
                data_tinh = await page.evaluate(f'async () => {{ const r = await fetch("{api_url_tinh}"); return await r.json(); }}')
                
                lich_loc = [i for i in data_tinh['data'] if "lâm hà" in str(i).lower()] if data_tinh else []
                
                if len(lich_loc) > 0:
                    msg = f"⚠️ <b>LỊCH LÂM HÀ (QUÉT TỔNG TỈNH PB03)</b>\n"
                    for i in lich_loc[:5]:
                        msg += f"📍 {i.get('TenKhuVuc')}\n⏰ {i.get('ThoiGian')}\n---\n"
                    send_telegram(msg)
                else:
                    send_telegram("🚀 Đã đổi sang mã PB03 nhưng API vẫn chưa trả kết quả. Đại ca check xem web có đang bảo trì không?")
