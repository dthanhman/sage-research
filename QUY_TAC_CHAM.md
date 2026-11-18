# Quy tắc chấm mIoU

Chốt ngày 18/11/2026, **trước khi** có kết quả của các phương án cải tiến.

## 1. Cách đo (cố định)

- Mạng phân đoạn: **SegFormer-B3**, train lại từ đầu trên ảnh ghép của từng phương án, **cùng một công thức train** cho mọi phương án
  (kể cả ảnh thường, ghép trung bình, SAGE). Chấm bằng checkpoint cuối (`last.pt`), không chọn checkpoint theo test.
- Thước đo chính: **mIoU trên 273 ảnh test** của FMB.
  - Bỏ 7 ảnh test bị rò (khung liền kề ảnh train).
  - Bỏ điểm ảnh không có nhãn.
  - Trung bình 13 lớp có trong test (lớp bicycle không có trong test).
  - Báo kèm số trên đủ 280 ảnh.
- Chọn phương án và chỉnh tham số chỉ dựa trên tập **khám phá** (tách từ tập train). Tập test chỉ chạy **một lần** cho bản cuối.
- Mọi ảnh ghép xử lý màu giống nhau: thay kênh độ sáng (Y), giữ màu (CrCb) của ảnh thường.

## 2. Số lần chạy

- Vòng chốt: mỗi phương án (kể cả ghép trung bình và SAGE) train **5 lần với 5 seed khác nhau**.
- So **theo cặp seed**: với cùng một seed, lấy mIoU phương án A trừ phương án B.

## 3. Cách kết luận "A hơn B" (thang 3 mức)

Công cụ: [`code/so_sanh_cap.py`](code/so_sanh_cap.py).

| Mức | Điều kiện | Nghĩa dễ hiểu |
|---|---|---|
| **Hơn chắc chắn** | Khoảng tin cậy 95% tính cả may rủi do chọn ảnh **và** do seed nằm hoàn toàn trên 0 | Hơn kể cả khi tính hết may rủi |
| **Hơn nhất quán** | Trung bình hiệu > 0, **seed nào cũng** hiệu > 0, và khoảng tin cậy 95% do chọn ảnh nằm trên 0 | Seed nào cũng hơn, mức hơn nhỏ |
| **Chưa phân biệt** | Không đạt hai mức trên | Không đủ bằng chứng |

Khoảng tin cậy tính bằng bootstrap 2.000 lần, bốc lại theo **khối 10 ảnh liền số** (ảnh FMB cắt từ video, ảnh liền số là cùng cảnh).

**Một phương án được tính là cải thiện** khi đạt ít nhất **"hơn nhất quán"** so với **cả** ghép trung bình **lẫn** SAGE, và qua các rào chắn ở mục 4.

## 4. Rào chắn

**a. Không dùng SAM**, kể cả lúc train. Được dùng lại khung mạng Student của SAGE nhưng phải tự train từ đầu, không nạp trọng số SAGE đã công bố.

**b. Ảnh ghép không quá xấu:**
- **MS-SSIM ≥ 99%** và **Q_ABF ≥ 98%** so với SAGE, đo trên tập khám phá.
  Cách đặt ngưỡng: train Student không SAM 5 lần (5 seed), ngưỡng = SAGE − 2 × độ lệch chuẩn giữa 5 lần, làm tròn 1%.
- Kèm theo: tỉ lệ điểm ảnh cháy trắng, và hình so sánh các ca đêm, khói, chạng vạng.
- **SCD chỉ báo cáo kèm, không dùng để loại.** Nếu SCD dưới 85% so với SAGE thì ghi cảnh báo "có thể đang chép gần nguyên một ảnh nguồn".
- Vì sao không dùng SCD để loại:
  1. Chính Student không SAM cũng chỉ đạt SCD 86–92% so với SAGE ở cả 5 lần train. Dùng SCD để loại thì mọi phương án không SAM đều bị loại trước khi xét mIoU.
  2. Kiểm trên nhiều cách ghép cho thấy SCD không dự đoán được mIoU (cách có SCD cao nhất không có mIoU cao nhất).
  - Ghi rõ: quyết định này được đưa ra sau khi đã thấy SCD của một phương án thử nghiệm (89% so với SAGE).

## 5. Số phụ (chốt luôn, không dùng để chọn phương án)

mIoU 7 lớp mà bài SAGE in ra, IoU từng lớp, kết quả theo nhóm ảnh tối / vừa / sáng.

## 6. Kết quả hiện có (273 ảnh test, 3 seed)

Ghép trung bình hơn SAGE +1,05 → **hơn nhất quán**. Các cặp khác (trung bình − ảnh thường, SAGE − ảnh thường, SAGE − Student không SAM) → chưa phân biệt.
Chi tiết ở [TN01](thi_nghiem/TN01_quy_tac_cham/).
