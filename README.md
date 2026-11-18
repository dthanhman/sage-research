# sage-research – Thí nghiệm cải tiến SAGE trên FMB (CS406 & CS431)

Repo **cá nhân của Mân** – thí nghiệm nghiên cứu cải tiến SAGE, đóng gói để có thể kiểm chéo.
Đây không phải repo chung của nhóm.
Bài gốc: *Every SAM Drop Counts* (SAGE, CVPR 2025), code gốc `RollingPlain/SAGE_IVIF`.

## Kiểm chéo

Theo vòng kiểm chéo của nhóm (Mân → Quân → Lộc Bé → Lộc Lớn → Mân), thí nghiệm trong repo này
do **Quân** kiểm lại.

Quy trình, checklist và phiếu xác nhận nằm trong [KIEM_THU.md](KIEM_THU.md).
Mức kiểm đã thống nhất: **chấm lại từ output đã lưu + chạy lại 1 seed**.

## Quy tắc chấm

Mọi so sánh mIoU dùng [QUY_TAC_CHAM.md](QUY_TAC_CHAM.md), chốt ngày 18/11/2026 trước khi có kết quả phương án mới:
SegFormer-B3, `last.pt`, `mIoU_co_mat` trên 273 ảnh test sạch, 5 seed, so theo cặp seed, thang 3 mức
(hơn chắc chắn / hơn nhất quán / chưa phân biệt).

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `code/` | Code dùng chung: xuất ảnh ghép, train/chấm SegFormer, so cặp có CI |
| `code/sage_student/model.py` | Mạng Student của SAGE (giấy phép MIT, xem `LICENSE_SAGE_IVIF`). `checkpoints.pt` tải từ repo gốc |
| `manifests/fmb_goc/` | Split cũ: 1.045 train / 175 dev / 280 test (cột `leak` đánh dấu 7 ảnh test rò) |
| `manifests/scene_v1/goc/` | Split scene_v1 (bản sao, nhóm chốt): 992 Train / 228 Dev (Quân, 16/11) |
| `manifests/scene_v1/kham_pha/` | Tách từ 992 Train để khám phá: train 841 / val 151 (3 đoạn id liền) |
| `thi_nghiem/TNxx_*/` | Mỗi thí nghiệm một thư mục: README (mục tiêu, tiêu chí, lệnh), output, phiếu kiểm |

**Không có trong repo:** ảnh FMB, ảnh ghép, checkpoint (nặng). Chỉ có manifest + md5 để đối chiếu.

## Cài đặt

Python 3.10+, đã chạy với: torch 2.7.1 (máy nhà) / 2.11 (Kaggle T4), transformers 5.20, opencv 4.9, numpy 1.26, pandas 2.2.

Biến môi trường (xem đầu `code/chung.py`):

| Biến | Ý nghĩa |
|---|---|
| `SAGE_FMB` | Thư mục FMB (có `train/` và `test/`, mỗi cái gồm `Visible/ Infrared/ Label/`) |
| `SAGE_MAN` | Thư mục manifest dùng (vd `manifests/fmb_goc`, `manifests/scene_v1/kham_pha`) |
| `SAGE_ANH` | Nơi ghi ảnh ghép `{bien_the}/{train|test}/{id}.png` |
| `SAGE_RUNS` | Nơi ghi kết quả train/chấm |

Trên Windows cần `PYTHONUTF8=1` (in tiếng Việt).

## Danh sách thí nghiệm

| Mã | Nội dung | Người làm | Người kiểm | Trạng thái |
|---|---|---|---|---|
| [TN01](thi_nghiem/TN01_quy_tac_cham/) | Quy tắc chấm + script so cặp seed, kiểm trên B3 test (vis, tb, sage, nosam, ir × 3 seed) | Mân | Quân | Chờ kiểm |
