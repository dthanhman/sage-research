# Quy tắc chấm mIoU – chốt 18/11/2026 (Mân), TRƯỚC khi có kết quả phương án mới

## Cố định (giữ như nhóm đã chốt ở Tab 4)
- SegFormer-B3, cùng công thức train cho mọi phương án (kể cả VIS, TB, SAGE), chấm `last.pt`.
- Metric chính: `mIoU_co_mat` (bỏ pixel unlabeled, 13 lớp có mặt) trên **273 ảnh test sạch**; báo kèm 280 ảnh.
- Chọn phương án chỉ dựa trên kham_pha (val 151) hoặc Dev. Test chạy **một lần** cho bản cuối.
- Đường màu: mọi biến thể = Y mới + CrCb của VIS (OpenCV), đã kiểm 18/11 (`code/xuat_anh.py`).

## Số seed
- Vòng cuối B3 test: **5 seed** cho phương án nhóm, TB, SAGE (tb, sage đã có seed 0–2 → thêm seed 3, 4).
- So **theo cặp seed**: cùng seed segmentation cho mọi phương án.

## Cách gọi kết quả (thang 3 mức) – `code/so_sanh_cap.py`
d_s = mIoU(A, s) − mIoU(B, s); CI_anh = bootstrap khối 10 ảnh id liền; CI_anh_seed = bootstrap 2 tầng (seed + khối ảnh); B = 2000.

| Mức | Điều kiện | Cách ghi |
|---|---|---|
| Hơn chắc chắn | cận dưới CI_anh_seed > 0 | "hơn có ý nghĩa thống kê" |
| Hơn nhất quán | d_tb > 0, **mọi seed** d_s > 0, cận dưới CI_anh > 0 | "hơn nhất quán qua mọi seed, mức nhỏ" |
| Chưa phân biệt | còn lại | báo đúng như vậy |

**Phương án nhóm được tính là cải thiện** khi đạt ít nhất "hơn nhất quán" so với **cả TB lẫn SAGE**, và qua rào chắn.

## Rào chắn
- Không dùng SAM (kể cả lúc train).
- Chỉ số ghép (SCD, MS-SSIM, Q_ABF) không dưới sàn: sàn = SAGE − 2 × SD 5 seed nosam trên val 151 (thí nghiệm chốt sàn, sẽ thêm vào `thi_nghiem/`).

## Số phụ (chốt luôn, KHÔNG dùng để chọn phương án)
mIoU 7 lớp của bài, IoU từng lớp, nhóm ảnh tối/vừa/sáng, dòng trần 4 kênh (RGB + IR) khi có.

## Mốc hiện có (B3 test 273, seed 0–2, kiểm script 18/11)
tb − sage +1,05 → **hơn nhất quán**; tb − vis +1,87, sage − vis +0,82, sage − nosam −0,44 → chưa phân biệt.
