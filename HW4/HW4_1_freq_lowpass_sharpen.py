"""HW4-1: 频率域滤波（5 步法）——低通平滑 + 频域锐化。
离散傅里叶变换/逆变换调用 numpy.fft（库函数），滤波本身手写实现。
"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RES = r"C:\Users\s\Desktop\HW4\results"
DATA = r"C:\Users\s\Desktop\HW4\data"
os.makedirs(RES, exist_ok=True)


def load_gray(path):
    return np.array(Image.open(path).convert("L")).astype(np.float64)


def save_norm(img, name):
    a = np.clip(img, 0, 255).astype(np.uint8)
    Image.fromarray(a).save(os.path.join(RES, name))


# ---- 步骤 0：读图（matplotlib 自带真实照片，与 HW3 一致）----
import matplotlib.image as mpimg
img_raw = mpimg.imread(matplotlib.get_data_path() + "/sample_data/grace_hopper.jpg")
grace = (img_raw[..., :3] @ np.array([0.299, 0.587, 0.114]))
grace = np.clip(grace, 0, 255).astype(np.uint8)
Image.fromarray(grace).save(os.path.join(DATA, "grace_hopper.jpg"))
f = grace.astype(np.float64)
M, N = f.shape
print("image size:", M, N)


# ---- 频域滤波 5 步法（核心函数）----
def freq_filter_5steps(img, H, norm=True):
    """步骤: (1) 补零到 2M x 2N -> (2) fft2 并 fftshift 居中 -> (3) 乘 H -> (4) ifft2 取实部 -> (5) 裁剪/裁剪回原尺寸并 uint8
    注意: 频谱必须 fftshift(fft2(...)) 才居中, 与居中坐标的 H 对齐。"""
    M, N = img.shape
    P, Q = 2 * M, 2 * N
    # 步骤 1：补零（中心化，让零频居中，减少缠绕误差）
    fp = np.zeros((P, Q))
    fp[:M, :N] = img
    # 步骤 2：DFT（用 fftshift(fft2) 将零频移至中心，与滤波器 H 坐标系一致）
    F = np.fft.fftshift(np.fft.fft2(fp))
    # 步骤 3：频域乘法
    G = F * H
    # 步骤 4：IDFT + 取实部（先 ifftshift 还原，再 ifft2）
    g = np.real(np.fft.ifft2(np.fft.ifftshift(G)))
    # 步骤 5：裁剪回原尺寸
    out = g[:M, :N]
    if norm:
        out = np.clip(out, 0, 255)
    return out


def make_filter(P, Q, builder):
    """构造尺寸 P x Q 的滤波器（中心在 (P//2, Q//2)），返回与 fftshift 后频谱对齐的 H。"""
    u = np.arange(P) - P // 2
    v = np.arange(Q) - Q // 2
    V, U = np.meshgrid(v, u)  # 行索引 v -> 第0轴(行)，列索引 u -> 第1轴(列)
    D = np.sqrt(U.astype(np.float64) ** 2 + V.astype(np.float64) ** 2)
    return builder(D, P, Q)


def ideal_lowpass(D, P, Q, D0=30):
    return (D <= D0).astype(np.float64)


def gaussian_lowpass(D, P, Q, D0=30):
    return np.exp(-(D ** 2) / (2 * (D0 ** 2)))


def ideal_highpass(D, P, Q, D0=30):
    return 1.0 - ideal_lowpass(D, P, Q, D0)


def gaussian_highpass(D, P, Q, D0=30):
    return 1.0 - gaussian_lowpass(D, P, Q, D0)


def unsharp_mask(D, P, Q, alpha=1.0, D0=30):
    # 非锐化掩模频域形式: H = 1 + alpha*(1 - 高斯低通)
    return 1.0 + alpha * gaussian_highpass(D, P, Q, D0)


def show_spectrum(F, name, title):
    # F 必须是已 fftshift 居中后的频谱；取对数幅度并归一化
    mag = np.log(1 + np.abs(F))
    mag = (mag - mag.min()) / (mag.max() - mag.min()) * 255
    Image.fromarray(mag.astype(np.uint8)).save(os.path.join(RES, name))
    print("saved spectrum", name, title)


# 参考频谱（用于展示"原图的频谱图"，用标准 fftshift 展示）
F_orig = np.fft.fftshift(np.fft.fft2(f))
show_spectrum(F_orig, "HW4-1_spectrum_original.png", "原图频谱(对数幅度)")
P, Q = 2 * M, 2 * N

# ===================== (1) 低通平滑 =====================
D0_lp = 80  # 600x512 图：较大截止，保留主要结构的同时明显平滑
H_ideal_lp = make_filter(P, Q, lambda D, p, q: ideal_lowpass(D, p, q, D0_lp))
H_gauss_lp = make_filter(P, Q, lambda D, p, q: gaussian_lowpass(D, p, q, D0_lp))

out_ideal_lp = freq_filter_5steps(f, H_ideal_lp)
out_gauss_lp = freq_filter_5steps(f, H_gauss_lp)

save_norm(out_ideal_lp, "HW4-1_ideal_lowpass_D30.png")
save_norm(out_gauss_lp, "HW4-1_gaussian_lowpass_D30.png")

# 频域操作结果的频谱图（展示滤波后的频谱 G = F*H，对数幅度）
G_ideal = np.fft.fftshift(np.fft.fft2(out_ideal_lp))
G_gauss = np.fft.fftshift(np.fft.fft2(out_gauss_lp))
show_spectrum(G_ideal, "HW4-1_spectrum_ideal_lowpass.png", "理想低通后频谱")
show_spectrum(G_gauss, "HW4-1_spectrum_gaussian_lowpass.png", "高斯低通后频谱")

# 同时保存低通滤波器本身图（展示 H）
Image.fromarray((H_gauss_lp * 255).astype(np.uint8)).save(
    os.path.join(RES, "HW4-1_filter_gaussian_lowpass.png"))
Image.fromarray((H_ideal_lp * 255).astype(np.uint8)).save(
    os.path.join(RES, "HW4-1_filter_ideal_lowpass.png"))

# ===================== (2) 频域锐化 =====================
D0_hp = 30  # 保留中高频边缘
H_ideal_hp = make_filter(P, Q, lambda D, p, q: ideal_highpass(D, p, q, D0_hp))
H_gauss_hp = make_filter(P, Q, lambda D, p, q: gaussian_highpass(D, p, q, D0_hp))
H_unsharp = make_filter(P, Q, lambda D, p, q: unsharp_mask(D, p, q, alpha=1.0, D0=D0_hp))

out_ideal_hp = freq_filter_5steps(f, H_ideal_hp)
out_gauss_hp = freq_filter_5steps(f, H_gauss_hp)
out_unsharp = freq_filter_5steps(f, H_unsharp)

save_norm(out_ideal_hp, "HW4-1_ideal_highpass_D30.png")
save_norm(out_gauss_hp, "HW4-1_gaussian_highpass_D30.png")
save_norm(out_unsharp, "HW4-1_unsharp_D30.png")

Image.fromarray((H_gauss_hp * 255).astype(np.uint8)).save(
    os.path.join(RES, "HW4-1_filter_gaussian_highpass.png"))
Image.fromarray((H_unsharp * 255).astype(np.uint8)).save(
    os.path.join(RES, "HW4-1_filter_unsharp.png"))

print("HW4-1 done.")
