# Hướng dẫn kiểm TN01 – từng bước

Làm lần lượt A → E. Gặp lỗi ở bước nào thì chụp màn hình, hỏi ngay trong [issue #1](https://github.com/dthanhman/sage-research/issues/1).

## A. Chuẩn bị (làm 1 lần)

1. Có tài khoản **GitHub** và **Kaggle**. Tài khoản Kaggle phải xác minh số điện thoại (để bật GPU và Internet).
2. Gửi Mân **username Kaggle**, để Mân chia sẻ dataset FMB riêng tư `fmb-ivif-sage`.
3. Trên máy có Python 3.10+.

## B. Việc 1 – Chạy lại công cụ (~5 phút, không cần GPU)

**B1. Tải repo về**

```bash
git clone https://github.com/dthanhman/sage-research.git
```
(hoặc trên trang repo bấm **Code → Download ZIP** rồi giải nén)

**B2. Cài thư viện**

```bash
pip install numpy pandas opencv-python
```

**B3. Chạy**

Git Bash / Linux / macOS:
```bash
cd sage-research/code
SAGE_RUNS=../thi_nghiem/TN01_quy_tac_cham/runs PYTHONUTF8=1 \
python so_sanh_cap.py --bien_the vis tb sage nosam ir --model b3 --hau _1220_15lop \
  --cap tb-sage tb-vis sage-vis sage-nosam nosam-tb > chay_lai.txt
```

PowerShell (Windows):
```powershell
cd sage-research\code
$env:SAGE_RUNS = "..\thi_nghiem\TN01_quy_tac_cham\runs"; $env:PYTHONUTF8 = "1"
python so_sanh_cap.py --bien_the vis tb sage nosam ir --model b3 --hau _1220_15lop --cap tb-sage tb-vis sage-vis sage-nosam nosam-tb | Out-File -Encoding utf8 chay_lai.txt
```

**B4. So kết quả**

Mở `chay_lai.txt` và `../thi_nghiem/TN01_quy_tac_cham/ket_qua/so_sanh_cap_test_b3.txt`, so từng bảng.
Các con số phải giống nhau. (Dòng cuối "Ghi …csv" có đường dẫn khác là bình thường.)

> Lưu ý: lệnh này ghi thêm file `so_sanh_cap_test_b3.csv` vào thư mục `runs/` – không sao, không cần gửi.

## C. Việc 2 – Đọc quy tắc, trả lời 5 câu hỏi (~20 phút)

Đọc [QUY_TAC_CHAM.md](../../QUY_TAC_CHAM.md), rồi trả lời 5 câu ở mục 6 của [README TN01](README.md).

## D. Việc 3 – Đọc code (~20 phút)

Trong thư mục `code/`:
- `so_sanh_cap.py`: hàm `muc()` (xếp 3 mức) có đúng như QUY_TAC_CHAM.md không; phần bootstrap (vòng `for _ in range(B)`).
- `chung.py`: hàm `cac_miou()`, phần tính `mIoU_co_mat` (bỏ điểm ảnh không nhãn, trung bình các lớp có trong test).

## E. Việc 4 – Train tb seed 3 trên Kaggle (~3 giờ, chạy nền)

**E1. Tạo notebook**
- Kaggle → **Create → New Notebook**.
- Thanh bên phải → **Session options**: Accelerator = **GPU T4 x2** (hoặc T4), **Internet = On**.
- **Add Input** → tab **Datasets** → tìm `fmb-ivif-sage` (Mân đã chia sẻ) → **Add**.

**E2. Dán vào 1 ô code**

```python
!git clone https://github.com/dthanhman/sage-research.git
%cd sage-research/code
import os
os.environ.update(SAGE_MAN="../manifests/fmb_goc", SAGE_ANH="/kaggle/temp/anh",
                  SAGE_RUNS="/kaggle/working/runs", PYTHONUTF8="1")
!python xuat_anh.py --bien_the tb
!python train_seg.py --bien_the tb --model b3 --seed 3 --gop_dev --lop0
!python eval_seg.py --run /kaggle/working/runs/tb_b3_s3_1220_15lop --ckpt last --khong_luu_anh
!cd /kaggle/working/runs && zip -r /kaggle/working/tb_b3_s3.zip tb_b3_s3_1220_15lop -x "*.pt"
```

(FMB được tự tìm trong `/kaggle/input`, không cần đặt đường dẫn.)

**E3. Chạy nền**
- Bấm **Save Version** → chọn **Save & Run All (Commit)** → **Save**.
- Có thể đóng trình duyệt. Chạy khoảng 2,5–3 giờ.

**E4. Lấy kết quả**
- Vào notebook → **Output** (hoặc mục Versions → bản vừa chạy) → tải `tb_b3_s3.zip`.
- Trong log cuối có dòng `273 ảnh: mIoU có mặt (13 lớp) …` → đó là số cần ghi.
- **Đạt** nếu số này nằm trong **63,2 – 65,6**.

## F. Gửi kết quả

Mở [issue #1](https://github.com/dthanhman/sage-research/issues/1) → ô bình luận ở cuối trang:
1. Dán mẫu phiếu (có trong nội dung issue) và điền.
2. **Kéo thả** `chay_lai.txt` và `tb_b3_s3.zip` vào ô bình luận.
3. Bấm **Comment**.

Xong. Mân sẽ lưu file vào repo.
