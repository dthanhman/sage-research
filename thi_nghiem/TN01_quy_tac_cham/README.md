# TN01 – Quy tắc chấm mIoU và công cụ so sánh

Người làm: Mân · Người kiểm: **Lộc Lớn** · Ngày: 18/11/2026 · Hạn kiểm: …

## 1. Mục đích (đọc cái này trước)

Các cách ghép ảnh chỉ chênh nhau khoảng **1 điểm mIoU**. Nhưng chỉ cần train lại với seed khác, mIoU cũng tự lên xuống
khoảng 1 điểm. Nếu không có luật rõ ràng, sau này một phương án hơn 0,5 điểm sẽ không biết là **cải thiện thật** hay **may**.

TN01 làm 2 việc:
1. **Đặt luật** khi nào được nói "A hơn B" → [QUY_TAC_CHAM.md](../../QUY_TAC_CHAM.md).
2. **Viết công cụ** tự tính theo luật đó → [`code/so_sanh_cap.py`](../../code/so_sanh_cap.py), và thử nó trên kết quả đã có.

TN01 **không đo phương án mới nào**. Mọi phương án cải tiến sau này đều chấm bằng luật + công cụ này,
nên cần người khác xác nhận **trước** khi có kết quả cải tiến.

## 2. Luật (tóm tắt)

Chạy mỗi cách ghép nhiều lần (nhiều seed). Với từng seed, lấy hiệu mIoU của A trừ B, rồi xếp 3 mức:

| Mức | Nghĩa dễ hiểu |
|---|---|
| **Hơn chắc chắn** | Hơn kể cả khi tính hết may rủi do chọn ảnh lẫn do seed |
| **Hơn nhất quán** | Seed nào A cũng hơn B, và vẫn hơn khi tính may rủi do chọn ảnh |
| **Chưa phân biệt** | Không đủ bằng chứng để nói A hơn B |

Phương án cải tiến phải đạt ít nhất **"hơn nhất quán"** so với **cả** ghép trung bình (TB) **lẫn** SAGE.

## 3. Dữ liệu có sẵn trong repo

Thư mục `runs/` có kết quả **15 lần train SegFormer-B3** = 5 cách ghép × 3 seed (0, 1, 2), chạy trên Kaggle T4 ngày 12–15/11:

| Tên | Ảnh đưa vào SegFormer |
|---|---|
| `vis` | Chỉ ảnh thường |
| `ir` | Chỉ ảnh hồng ngoại |
| `tb` | Trung bình ảnh thường và hồng ngoại |
| `sage` | Ảnh ghép của SAGE (checkpoint công bố) |
| `nosam` | Ảnh ghép của Student SAGE train lại **không SAM** |

Mỗi lần chạy có file `test_nham_last.npz` = ma trận nhầm lẫn **của từng ảnh** trong 280 ảnh test (có cột đánh dấu 7 ảnh rò).
Đủ để tính lại mọi con số **mà không cần ảnh FMB, không cần GPU**.

> Các lần train này dùng split cũ (1.220 ảnh train). Không sao, vì TN01 chỉ kiểm **cách chấm**, và tập test vẫn là 280 ảnh test chuẩn.

## 4. Việc của Lộc Lớn

| # | Việc | Thời gian |
|---|---|---|
| 1 | Chạy lại công cụ (lệnh bên dưới), so với kết quả đúng ở mục 5 | ~5 phút |
| 2 | Đọc luật, trả lời 5 câu hỏi ở mục 6 | ~20 phút |
| 3 | Đọc code: hàm `muc()` và phần bootstrap trong `so_sanh_cap.py`, hàm `cac_miou()` trong `chung.py` | ~20 phút |
| 4 | *(Tùy chọn – Mân quyết)* Train lại `tb` seed 0 trên Kaggle, xem có ra gần 64,27 không (lệch ≤ 1,2) | ~2,6 h GPU |
| 5 | Điền phiếu ở mục 7, gửi bằng Pull Request hoặc Issue | ~5 phút |

**Lệnh cho việc 1** (cần Python có numpy, pandas):

```bash
cd code
SAGE_RUNS=../thi_nghiem/TN01_quy_tac_cham/runs PYTHONUTF8=1 \
python so_sanh_cap.py --bien_the vis tb sage nosam ir --model b3 --hau _1220_15lop \
  --cap tb-sage tb-vis sage-vis sage-nosam nosam-tb
```

## 5. Kết quả đúng phải ra

Khớp từng chữ số với [`ket_qua/so_sanh_cap_test_b3.txt`](ket_qua/so_sanh_cap_test_b3.txt). Tóm tắt:

| So sánh | Hơn trung bình | Số seed hơn | Mức |
|---|---|---|---|
| tb − sage | +1,05 | 3/3 | **hơn nhất quán** |
| tb − vis | +1,87 | 3/3 | chưa phân biệt |
| sage − vis | +0,82 | 3/3 | chưa phân biệt |
| sage − nosam | −0,44 | 0/3 | chưa phân biệt |
| nosam − tb | −0,61 | 1/3 | chưa phân biệt |

mIoU trung bình 3 seed (273 ảnh): tb 64,42 · nosam 63,81 · sage 63,37 · vis 62,55 · ir 56,41.

## 6. Năm câu hỏi về luật

1. Vòng chốt chạy **5 seed** – đủ chưa, hay quá tốn GPU?
2. Mức **"hơn nhất quán"** có quá dễ không?
3. Phương án cải tiến phải hơn **cả TB lẫn SAGE** – đồng ý không?
4. Thước đo chính là **mIoU trên 273 ảnh** (bỏ 7 ảnh rò, bỏ điểm ảnh không nhãn, trung bình 13 lớp có trong test) – giữ hay đổi?
5. Rào chắn ảnh: chỉ đòi MS-SSIM và Q_ABF không thấp hơn SAGE quá mức dao động, còn SCD chỉ báo kèm – hợp lý không?

## 7. Phiếu kiểm (Lộc Lớn điền)

- Ngày kiểm: …
- Việc 1 – chạy lại: khớp / không khớp (…)
- Việc 2 – 5 câu hỏi: 1 … / 2 … / 3 … / 4 … / 5 …
- Việc 3 – đọc code: không thấy lỗi / lỗi: …
- Việc 4 – train lại: không làm / ra …, lệch … → đạt / không đạt
- Kết luận: **ĐỒNG Ý** / **CẦN SỬA** (…)

---

<details>
<summary>Chi tiết kỹ thuật (cho ai muốn soát sâu)</summary>

- **CI ảnh:** bốc lại ảnh theo khối 10 ảnh id liền nhau (ảnh FMB cắt từ video, ảnh liền số là cùng cảnh), 2.000 lần.
- **CI ảnh + seed:** mỗi lần bốc lại cả khối ảnh lẫn seed (có hoàn lại). Với 3 seed thì còn thô → vòng chốt dùng 5 seed.
- **Hơn nhất quán** = trung bình hiệu > 0, mọi seed hiệu > 0, cận dưới CI ảnh > 0. **Hơn chắc chắn** = cận dưới CI ảnh + seed > 0.
- **SegFormer-B3** (`nvidia/mit-b3`): train 1.220 ảnh (`manifests/fmb_goc`, `--gop_dev`), 15 lớp (`--lop0`), 100 epoch,
  batch 8, crop 512, AdamW lr 6e-5, chấm `last.pt`. Cấu hình đủ trong `runs/*/config.json`.
- **Lệnh train lại cho việc 4:**
  ```bash
  cd code
  export SAGE_FMB=<thư mục FMB> SAGE_MAN=../manifests/fmb_goc SAGE_ANH=<nơi ghi ảnh> SAGE_RUNS=<nơi ghi runs> PYTHONUTF8=1
  python xuat_anh.py --bien_the tb
  python train_seg.py --bien_the tb --model b3 --seed 0 --gop_dev --lop0
  python eval_seg.py --run $SAGE_RUNS/tb_b3_s0_1220_15lop --ckpt last
  ```
</details>
