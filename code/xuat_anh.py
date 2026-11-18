"""Bước 1: xuất ảnh đầu vào cho SegFormer theo từng biến thể, cho cả train, dev, test.

  vis  : ảnh VIS gốc
  ir   : IR xám, nhân 3 kênh
  tb   : Y = (Y_vis + IR)/2, màu CrCb của VIS  (ghép trung bình – đối chứng đơn giản, bài không có)
  clahe: Y = CLAHE(Y_vis), màu CrCb của VIS     (đối chứng "chỉ tăng tương phản", bài không có)
  sage : Y = SAGE Student pretrained, màu CrCb của VIS (giống output thật của SAGE)
  nosam: Y = Student train lại KHÔNG SAM/Teacher (E17, tai_lap/e17), checkpoint sage_student/nosam.pt
  tn   : M5 – trộn thích nghi từng điểm ảnh (CS406, không train):
         Y = (1-w)*Y_vis + w*IR,  w = clip(0,4 + 0,3*(1 - L) + 0,3*S, 0,3; 0,85)
         L = độ sáng cục bộ của VIS (Gauss sigma 21), S = độ nổi IR cục bộ = clip(4*(IR - Gauss(IR)), 0, 1)
         Ý: chỗ tối và chỗ IR nổi (người, xe nóng) lấy nhiều IR hơn; chỗ sáng gần TB/VIS.
  tbct : M8 – nền TB + chi tiết max (không train): nền = (blur31(Y_vis) + blur31(IR))/2,
         chi tiết = phần (ảnh − nền) có |.| lớn hơn giữa VIS và IR, màu CrCb của VIS.
  tbcd : M8b – như tbct nhưng chi tiết = chi tiết VIS + chi tiết IR (cộng, không chọn).
  vci  : M8c – Y = Y_vis + (IR − mean(IR)), cắt [0, 255] (nền cũng cộng).
  vcim : M8d – như M8c nhưng nén mềm (tanh) ngoài [40, 200] thay vì cắt cứng (chống cháy trắng).

Ví dụ: python xuat_anh.py --bien_the sage
"""
import argparse
import sys

import cv2
import numpy as np
import pandas as pd
from pathlib import Path

from chung import ANH, MAN, STUDENT, duong, thu_muc


CKPT = {"sage": "checkpoints.pt", "nosam": "nosam.pt", "nosam_s1": "nosam_s1.pt", "nosam_s2": "nosam_s2.pt"}  # biến thể chạy bằng mạng Student


def trong_so_tn(y, ir):
    """Trọng số IR từng điểm ảnh cho M5 (y, ir: uint8 HxW)."""
    yv, iv = y.astype(np.float32) / 255, ir.astype(np.float32) / 255
    L = cv2.GaussianBlur(yv, (0, 0), 21)
    S = np.clip(4 * (iv - cv2.GaussianBlur(iv, (0, 0), 21)), 0, 1)
    return np.clip(0.4 + 0.3 * (1 - L) + 0.3 * S, 0.3, 0.85)


def tb_chi_tiet(y, ir, k=31):
    """M8: ghép 2 tầng. Nền = trung bình nền VIS và nền IR (như TB, giữ IR cho phân đoạn);
    chi tiết = ở từng điểm lấy chi tiết có |.| lớn hơn (giữ cạnh nét, như loss gradient max của TDFusion/ReFusion).
    Nền = lọc trung bình k x k (k = 31 như GFF, Li 2013)."""
    yv, iv = y.astype(np.float32), ir.astype(np.float32)
    bv, bi = cv2.blur(yv, (k, k)), cv2.blur(iv, (k, k))
    dv, di = yv - bv, iv - bi
    d = np.where(np.abs(dv) >= np.abs(di), dv, di)
    return ((bv + bi) / 2 + d).round().clip(0, 255).astype(np.uint8)


def tb_cong_chi_tiet(y, ir, k=31):
    """M8b: như M8 nhưng CỘNG chi tiết hai nguồn thay vì chọn max (M8 rớt SCD 87,5% vì bỏ chi tiết của nguồn yếu hơn)."""
    yv, iv = y.astype(np.float32), ir.astype(np.float32)
    bv, bi = cv2.blur(yv, (k, k)), cv2.blur(iv, (k, k))
    return ((bv + bi) / 2 + (yv - bv) + (iv - bi)).round().clip(0, 255).astype(np.uint8)


def vis_cong_ir(y, ir):
    """M8c: nền cũng CỘNG (không lấy trung bình): F = (nền VIS + nền IR) + (chi tiết VIS + chi tiết IR) − mean(IR)
    = Y_vis + (IR − mean(IR)). Giữ độ sáng chung của VIS, cộng toàn bộ độ lệch của IR (M8, M8b rớt SCD vì F giống
    trung bình; SCD lớn nhất khi F ≈ VIS + IR). Cắt về [0, 255]."""
    yv, iv = y.astype(np.float32), ir.astype(np.float32)
    return (yv + iv - iv.mean()).round().clip(0, 255).astype(np.uint8)


def nen_mem(x, lo=40.0, hi=200.0):
    """Nén mềm hai đầu thay cho cắt cứng: giữ nguyên trong [lo, hi], ngoài khoảng đó ép dần (tanh) vào [0, lo] / [hi, 255].
    Đơn điệu, liên tục, giữ được chênh lệch (cửa sổ, biển báo) ở vùng sáng thay vì cắt phẳng về 255."""
    y = x.copy()
    t = x > hi
    y[t] = hi + (255 - hi) * np.tanh((x[t] - hi) / (255 - hi))
    t = x < lo
    y[t] = lo - lo * np.tanh((lo - x[t]) / lo)
    return y


def vis_cong_ir_mem(y, ir):
    """M8d: như M8c (Y_vis + IR − mean(IR)) nhưng NÉN MỀM vùng sáng/tối thay vì cắt [0, 255]
    (M8c cháy trắng mặt tiền nhà ban ngày, tới 14% điểm ảnh; biển báo bạc màu)."""
    yv, iv = y.astype(np.float32), ir.astype(np.float32)
    return nen_mem(yv + iv - iv.mean()).round().clip(0, 255).astype(np.uint8)


def tron_thich_nghi(y, ir):
    w = trong_so_tn(y, ir)
    return ((1 - w) * y.astype(np.float32) + w * ir).round().clip(0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bien_the", required=True,
                    help="vis|ir|tb|sage|clahe|nosam*|tn, hoặc tên checkpoint sage_student/<tên>.pt (M4/M6, có đầu 'dau.')")
    ap.add_argument("--gioi_han", type=int, default=0, help="chỉ để thử: xuất N ảnh đầu")
    a = ap.parse_args()

    df = pd.concat([pd.read_csv(MAN / f"{s}.csv", dtype={"image_id": str}) for s in ("train", "dev", "test")])
    if a.gioi_han:
        df = df.head(a.gioi_han)
    if a.bien_the not in CKPT and a.bien_the not in ("vis", "ir", "tb", "clahe", "tn", "tbct", "tbcd", "vci", "vcim"):
        assert (STUDENT / f"{a.bien_the}.pt").exists(), f"không có biến thể/checkpoint {a.bien_the}"
        CKPT[a.bien_the] = f"{a.bien_the}.pt"
    if a.bien_the in CKPT:
        import torch
        sys.path.insert(0, str(STUDENT))
        from model import Network
        dev = "cuda" if torch.cuda.is_available() else "cpu"
        net = Network()
        sd = torch.load(STUDENT / CKPT[a.bien_the], map_location="cpu", weights_only=True)
        if any(k.startswith("dau.") for k in sd):          # M4/M6: Student + đầu trộn (DauTron)
            day = Path(__file__).resolve().parent      # Kaggle: train_student_seg.py nằm cùng thư mục
            sys.path.insert(0, str(day if (day / "train_student_seg.py").exists() else day.parent / "cai_tien"))
            from train_student_seg import DauTron
            net = DauTron(net)
        net.load_state_dict(sd, strict=True)
        net.to(dev).eval()
        t2 = lambda z: torch.from_numpy(z).float().div(255)[None, None].to(dev)

    n = 0
    for r in df.itertuples():
        out = ANH / a.bien_the / thu_muc(r) / f"{r.image_id}.png"
        if out.exists():
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        vis = cv2.imread(str(duong(r.vis_path)))
        ir = cv2.cvtColor(cv2.imread(str(duong(r.ir_path))), cv2.COLOR_BGR2GRAY)
        if a.bien_the == "vis":
            img = vis
        elif a.bien_the == "ir":
            img = cv2.cvtColor(ir, cv2.COLOR_GRAY2BGR)
        else:
            ycc = cv2.cvtColor(vis, cv2.COLOR_BGR2YCrCb)
            y = ycc[:, :, 0]
            if a.bien_the == "clahe":
                yf = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(y)
            elif a.bien_the == "tb":
                yf = ((y.astype(np.float64) + ir) / 2).round().astype(np.uint8)
            elif a.bien_the == "vcim":
                yf = vis_cong_ir_mem(y, ir)
            elif a.bien_the == "vci":
                yf = vis_cong_ir(y, ir)
            elif a.bien_the == "tbcd":
                yf = tb_cong_chi_tiet(y, ir)
            elif a.bien_the == "tbct":
                yf = tb_chi_tiet(y, ir)
            elif a.bien_the == "tn":
                yf = tron_thich_nghi(y, ir)
            else:
                with torch.inference_mode():
                    yf = (net(t2(y), t2(ir))[0].clamp(0, 1) * 255).round().byte().cpu().numpy()[0, 0]
            img = cv2.cvtColor(np.dstack([yf, ycc[:, :, 1:]]), cv2.COLOR_YCrCb2BGR)
        cv2.imwrite(str(out), img)
        n += 1
    print(f"{a.bien_the}: ghi {n} ảnh mới vào {ANH / a.bien_the}", flush=True)


if __name__ == "__main__":
    main()
