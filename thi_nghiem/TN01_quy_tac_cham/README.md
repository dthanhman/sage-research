# TN01 – Quy tắc chấm mIoU và script so cặp seed

- Người làm: Mân | Người kiểm: **Quân** | Ngày: 18/11/2026
- Câu hỏi: chênh giữa các cách ghép (~1 điểm mIoU) cỡ bằng dao động seed. Cần một cách chấm **chốt trước**,
  có CI cho **hiệu số**, để biết khi nào được nói "phương án A hơn B".
- Quy tắc: [QUY_TAC_CHAM.md](../../QUY_TAC_CHAM.md). Script: [`code/so_sanh_cap.py`](../../code/so_sanh_cap.py).

## Việc của Quân (người kiểm)

| # | Việc | Cần gì | Thời gian | Nộp lại |
|---|---|---|---|---|
| 1 | **Đọc và góp ý quy tắc** – trả lời 5 câu hỏi bên dưới | Đọc QUY_TAC_CHAM.md | ~20 phút | Trả lời từng câu (đồng ý / đề xuất sửa + lý do) |
| 2 | **Bước A** – chạy lại script trên output có sẵn, so với `ket_qua/so_sanh_cap_test_b3.txt` | Python, không cần GPU | ~5 phút | Khớp / không khớp (dán dòng lệch nếu có) |
| 3 | **Soát code** – đọc hàm `muc()` và phần bootstrap trong `so_sanh_cap.py`, `cac_miou()` trong `chung.py` | Đọc code | ~20 phút | Lỗi tìm được (nếu có) |
| 4 | **Bước B (tùy chọn, nếu còn quota Kaggle)** – train lại tb seed 0 | Kaggle T4, FMB | ~2,6 h | Số mIoU_co_mat 273 ảnh, lệch so với 64,27 |
| 5 | **Điền phiếu kiểm** ở cuối file này | – | ~5 phút | Phiếu + kết luận ĐỒNG Ý / CẦN SỬA |

**Nộp ở đâu:** mở Pull Request sửa file này (điền phiếu + câu trả lời), hoặc mở Issue trên repo nếu không quen PR.
**Hạn:** …

### 5 câu hỏi về quy tắc (việc 1)

1. Vòng cuối **5 seed** (B3 test) – đủ chưa, hay quá tốn quota?
2. Mức **"hơn nhất quán"** (mọi seed dương + CI ảnh không chứa 0) – có quá dễ không? Có nên đòi thêm điều kiện?
3. Phương án cải tiến phải **hơn cả TB lẫn SAGE** – đồng ý không?
4. Metric chính **mIoU_co_mat, 273 ảnh** (bỏ 7 ảnh rò, 13 lớp có mặt) – giữ hay đổi?
5. Rào chắn "ảnh không quá xấu": MS-SSIM ≥ 99%, Q_ABF ≥ 98% SAGE + nhìn mắt; **SCD chỉ báo kèm** (vì nosam tự rớt SCD) – hợp lý không?

## Dữ liệu dùng để kiểm script

Kết quả B3 đã có (chạy trên Kaggle T4 ngày 12–15/11):

- Ảnh ghép: vis, tb (Y = trung bình Y_vis và IR), sage (Student pretrained), nosam (Student train lại không SAM), ir.
- SegFormer-B3 (`nvidia/mit-b3`), train trên 1.220 ảnh train chính thức (`manifests/fmb_goc`, train + dev, `--gop_dev`),
  15 lớp (`--lop0`), 100 epoch, batch 8, crop 512, AdamW lr 6e-5, chấm `last.pt`. Cấu hình đủ trong `runs/*/config.json`.
- Seed 0, 1, 2 cho mỗi biến thể → 15 run. Mỗi run có `test_nham_last.npz` (ma trận nhầm lẫn 15×15 **từng ảnh**, 280 ảnh, cột leak).

## Bước A – chấm lại từ output (không cần GPU, ~1 phút)

```bash
cd code
SAGE_RUNS=../thi_nghiem/TN01_quy_tac_cham/runs PYTHONUTF8=1 \
python so_sanh_cap.py --bien_the vis tb sage nosam ir --model b3 --hau _1220_15lop \
  --cap tb-sage tb-vis sage-vis sage-nosam nosam-tb
```

Phải ra đúng như [`ket_qua/so_sanh_cap_test_b3.txt`](ket_qua/so_sanh_cap_test_b3.txt) (bootstrap có seed cố định nên khớp tới chữ số cuối).

Kết quả (273 ảnh sạch, 3 seed):

| Cặp | Hiệu TB | Seed dương | CI ảnh | CI ảnh + seed | Mức |
|---|---|---|---|---|---|
| tb − sage | +1,05 | 3/3 | [+0,18; +1,82] | [−0,21; +2,03] | **hơn nhất quán** |
| tb − vis | +1,87 | 3/3 | [−0,05; +3,89] | [−0,22; +3,93] | chưa phân biệt |
| sage − vis | +0,82 | 3/3 | [−0,93; +3,07] | [−1,00; +3,24] | chưa phân biệt |
| sage − nosam | −0,44 | 0/3 | [−0,94; +0,09] | [−1,16; +0,37] | chưa phân biệt |
| nosam − tb | −0,61 | 1/3 | [−1,22; +0,02] | [−1,42; +0,48] | chưa phân biệt |

mIoU_co_mat TB 3 seed: tb 64,42 ± 0,60 / nosam 63,81 ± 0,81 / sage 63,37 ± 0,94 / vis 62,55 ± 0,48 / ir 56,41 ± 1,64.

## Điểm nhờ người kiểm soát kỹ

1. Cách tính CI: khối 10 ảnh id liền (ảnh FMB cắt từ video, ảnh liền số cùng cảnh); bootstrap 2 tầng (seed + khối ảnh).
2. Thang 3 mức trong hàm `muc()` có khớp với QUY_TAC_CHAM.md không.
3. `mIoU_co_mat`: bỏ pixel unlabeled, trung bình 13 lớp có trong test (bicycle không có trong test). Hàm `cac_miou` trong `code/chung.py`.
4. Bỏ đúng 7 ảnh rò (cột `leak` trong npz).

## Bước B – chạy lại 1 seed (GPU, ~2,6 h trên Kaggle T4)

Chạy lại **tb, seed 0**, rồi chấm:

```bash
cd code
SAGE_FMB=<FMB> SAGE_MAN=../manifests/fmb_goc SAGE_ANH=<ảnh> SAGE_RUNS=<runs> PYTHONUTF8=1 \
python xuat_anh.py --bien_the tb
python train_seg.py --bien_the tb --model b3 --seed 0 --gop_dev --lop0
python eval_seg.py --run <runs>/tb_b3_s0_1220_15lop --ckpt last
```

Số gốc: tb seed 0 = **64,27** (273 ảnh, `mIoU_co_mat`). Đạt nếu lệch ≤ 2 × 0,60 = 1,2 điểm.

## Giới hạn

- Với 3 seed, tầng seed của bootstrap còn thô → vòng cuối sẽ dùng 5 seed (QUY_TAC_CHAM.md).
- Các run này train trên 1.220 ảnh của split cũ; split nhóm mới (scene_v1) dùng cho khám phá phương án.

## Phiếu kiểm (Quân điền)

- Người kiểm: Quân | Ngày: …
- Việc 1 – trả lời 5 câu hỏi: 1 … / 2 … / 3 … / 4 … / 5 …
- Việc 2 – Bước A: khớp / không khớp (…)
- Việc 3 – Soát code: không thấy lỗi / lỗi: …
- Việc 4 – Bước B: không làm / seed 0 = …, lệch … → đạt / không đạt
- Checklist KIEM_THU.md mục 3 (1–8): …
- Kết luận: ĐỒNG Ý / CẦN SỬA (…)
