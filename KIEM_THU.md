# Quy trình kiểm chéo

Vòng: **Mân → Quân → Lộc Bé → Lộc Lớn → Mân** (người kế tiếp kiểm thí nghiệm của người trước).

**Khi nào cần kiểm chéo:** thí nghiệm có số đưa vào báo cáo/slide, hoặc dùng để ra quyết định (chọn phương án, chốt tiêu chí, bỏ một hướng).
Thử nhanh để dò hướng thì không cần – ghi lại trong nhật ký của người làm là đủ.

## 1. Người làm: chuẩn bị gói

Mỗi thí nghiệm là một thư mục `thi_nghiem/TNxx_ten_ngan/` gồm:

- `README.md` theo mẫu ở mục 4 (mục tiêu, tiêu chí **đặt trước**, lệnh chạy, môi trường, seed, split).
- Output đủ để chấm lại **không cần GPU**: `*_nham_last.npz`, `config.json`, `log.csv`, bảng kết quả.
- Code đúng phiên bản đã chạy (đã có trong `code/`; nếu dùng code riêng thì để trong thư mục thí nghiệm).
- Ghi rõ **seed nào** để người kiểm chạy lại.

Rồi mở Pull Request (hoặc báo trong nhóm), gắn tên người kiểm.

## 2. Người kiểm: làm 2 bước

**Bước A – Chấm lại từ output (nhanh, không cần GPU).**
Chạy lại lệnh chấm/so sánh trong README trên output đã lưu. Số phải **khớp đúng** (cùng code, cùng dữ liệu).

**Bước B – Chạy lại 1 seed (cần GPU).**
Train lại đúng 1 seed được chỉ định, chấm lại. Không đòi khớp tuyệt đối (GPU/thư viện khác nhau cho kết quả hơi khác),
nhưng phải nằm trong **dao động seed**: lệch so với số của người làm ≤ 2 × SD seed ghi trong README.

## 3. Checklist của người kiểm

| # | Câu hỏi | Đạt? | Ghi chú |
|---|---|---|---|
| 1 | Chạy lại được theo README, không phải sửa code? | | |
| 2 | Bước A: số khớp đúng? | | |
| 3 | Bước B: seed chạy lại nằm trong dao động seed? (ghi số) | | |
| 4 | Split đúng như README? Không dùng test để chọn phương án/siêu tham số? | | |
| 5 | Mọi phương án được so dùng cùng công thức train + cùng script chấm (QUY_TAC_CHAM.md)? | | |
| 6 | Tiêu chí có trước khi chạy không (xem lịch sử commit)? | | |
| 7 | Kết luận trong README đúng với số (đúng mức của thang 3 mức)? | | |
| 8 | Số "theo bài" có ghi nguồn bảng, không ghi như số của nhóm? | | |

## 4. Mẫu README thí nghiệm

```markdown
# TNxx – <tên>
- Người làm: … | Người kiểm: … | Ngày: …
- Câu hỏi: …
- Tiêu chí đặt trước (ngày …): …
- Split: manifests/… | Seed: … | Seed để người kiểm chạy lại: …
- Môi trường: GPU …, torch …, thời gian …
- Lệnh chạy (đủ để chạy lại): …
- Kết quả: bảng + mức theo thang 3 mức
- Giới hạn: …
```

## 5. Phiếu xác nhận (người kiểm điền vào cuối README thí nghiệm)

```markdown
## Phiếu kiểm
- Người kiểm: … | Ngày: …
- Bước A: khớp / không khớp (…)
- Bước B: seed …, số …, lệch … (dao động seed …) → đạt / không đạt
- Checklist: 1 … 8: …
- Kết luận: ĐỒNG Ý / CẦN SỬA (…)
```
