# VNHerb-70 · Trạm thu mẫu ảnh cây thuốc

App Streamlit thu thập dữ liệu ảnh **70 cây thuốc nam (QĐ4664/QĐ-BYT 2014)**.
Chụp một bức ảnh → app chạy các bước rút gọn của pipeline:

- **P5 — IQA**: độ nét (Laplacian), tỉ lệ đối tượng, phân giải, độ sáng, độ bão hòa (lọc ảnh filter).
- **P3 — Định loại**: gọi PlantNet API, đối chiếu kết quả với 70 loài; loài ngoài danh mục → `uncertain`.
- **P4 — Bộ phận**: gán `organ_type` (leaf/stem/flower/.../processed_herb) + `organ_subtype`.
- **P6 — Cảnh báo nhầm lẫn**: tự nhắc các cặp dễ nhầm (Gừng/Nghệ/Địa liền, các Phyllanthus, Clerodendrum…).
- **Lưu trữ**: ảnh vào `raw/<species_id>/<organ>/<md5>.jpg` (hoặc `uncertain/`),
  ghi `source_log.csv` (chỉ khi có license — đúng P2) và `verification_log.csv`.

## Cài & chạy
```bash
pip install -r requirements.txt
streamlit run app.py
```
Mở trên điện thoại: chạy `streamlit run app.py --server.address 0.0.0.0`
rồi truy cập `http://<IP-máy>:8501` cùng mạng LAN. Tab "Chụp bằng camera" cần HTTPS
hoặc localhost (giới hạn của trình duyệt với `getUserMedia`).

## Tệp
| File | Vai trò |
|------|---------|
| `app.py` | Giao diện Streamlit, điều phối pipeline |
| `taxonomy.py` | 70 loài QĐ4664 + tra cứu + cặp nhầm lẫn (P1) |
| `iqa.py` | Kiểm tra chất lượng ảnh (P5) |
| `plantnet.py` | Client PlantNet API + MD5 (P3) |
| `storage.py` | Ghi raw/, logs đúng cấu trúc pipeline |

## Ghi chú
- PlantNet là công cụ **sơ bộ**. Ảnh chỉ được route `verified_pending_expert`;
  cần chuyên gia thực vật/dược liệu xác nhận trước khi vào tập `verified` (P3).
- API key gọi trực tiếp từ máy chạy app — nếu triển khai nhiều người, đặt proxy giữ key.
- Ngưỡng IQA chỉnh trong `iqa.CFG`.
- App **không** augment ảnh (đúng P7: không augment trước khi xác minh định loại).
