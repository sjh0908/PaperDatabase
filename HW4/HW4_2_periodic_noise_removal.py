"""HW4-2: 频域选择滤波器去除周期噪声（大脑 CT 体膜 Shepp-Logan）。
生成 Shepp-Logan 体膜 -> 叠加周期性条纹噪声 -> 在频域用陷波(带阻)滤波器去除。
DFT/IDFT 调用 numpy.fft（允许使用库函数）。
"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")

RES = r"C:\Users\s\Desktop\HW4\results"
DATA = r"C:\Users\s\Desktop\HW4\data"
os.makedirs(RES, exist_ok=True)


# ============ 1. Shepp-Logan 体膜（标准参数）============
def shepp_logan(size=512):
    ellipses = [
        (0.69, 0.92, 0.0, 0.0, 0.0, 2.0),
        (0.6624, 0.874, 0.0, 0.0, -0.0184, 1.0),
        (0.11, 0.31, -18.0, 0.22, 0.0, -0.8),
        (0.16, 0.41, 18.0, -0.22, 0.0, -0.2),
        (0.21, 0.25, 0.0, 0.0, 0.35, -0.2),
        (0.046, 0.046, 0.0, 0.0, 0.1, 1.0),
        (0.046, 0.046, 0.0, 0.0, -0.1, 1.0),
        (0.046, 0.023, 0.0, -0.08, -0.605, 1.0),
        (0.023, 0.023, 0.0, 0.0, -0.606, 1.0),
        (0.023, 0.046, 0.0, 0.06, -0.605, 1.0),
    ]
    img = np.zeros((size, size))
    y, x = np.mgrid[0:size, 0:size]
    y = 2 * (y + 0.5) / size - 1.0
    x = 2 * (x + 0.5) / size - 1.0
    for a, b, phi, x0, y0, gray in ellipses:
        xs = x - x0
        ys = y - y0
        phi = np.deg2rad(phi)
        c, s = np.cos(phi), np.sin(phi)
        xp = (c * xs + s * ys) / a
        yp = (-s * xs + c * ys) / b
        mask = xp ** 2 + yp ** 2 <= 1.0
        img[mask] += gray
    img = np.clip(img, 0, None)
    img = img / img.max() * 255.0
    return img


phantom = shepp_logan(512)
Image.fromarray(phantom.astype(np.uint8)).save(os.path.join(DATA, "shepp_logan.png"))
print("shepp-logan size:", phantom.shape)
M, N = phantom.shape


# ============ 2. 叠加周期性条纹噪声 ============
# 设计：两组对角方向二维正弦条纹（45°/-45° 交叉网格），在 512 图上的频率 u0=v0=60
yy, xx = np.mgrid[0:M, 0:N]


def periodic_noise(u0, v0, amp):
    return amp * (np.sin(2 * np.pi * (u0 * xx / N + v0 * yy / M))
                  + np.sin(2 * np.pi * (u0 * xx / N - v0 * yy / M)))


noise = periodic_noise(60, 60, 60.0)
noisy = np.clip(phantom + noise, 0, 255)
Image.fromarray(noisy.astype(np.uint8)).save(os.path.join(RES, "HW4-2_phantom_noisy.png"))

# 注意：在 P=2M x Q=2N 的零填充频谱中，频率索引翻倍，噪声峰位于 ±(2*u0, ±2*v0)
P, Q = 2 * M, 2 * N
true_freq = round(P * 60 / N)            # = 120
print("noise peak index in padded spectrum (from center):", true_freq)


# ============ 3. 频域 5 步法 ============
def freq_filter_5steps(img, H):
    M, N = img.shape
    P, Q = 2 * M, 2 * N
    fp = np.zeros((P, Q))
    fp[:M, :N] = img
    F = np.fft.fftshift(np.fft.fft2(fp))
    G = F * H
    g = np.real(np.fft.ifft2(np.fft.ifftshift(G)))
    return np.clip(g[:M, :N], 0, 255)


def detect_noise_peaks(F_padded, cx, cy, exclude=20):
    """在已 fftshift 的频谱中，按四象限各自取最强离群峰（即周期噪声冲击），返回相对中心的坐标列表。"""
    lm = np.log(1 + np.abs(F_padded))
    peaks = []
    half_x, half_y = F_padded.shape[1] // 2, F_padded.shape[0] // 2
    for sx in (1, -1):
        for sy in (1, -1):
            sub = lm.copy()
            if sx > 0:
                sub[:, :half_x + exclude] = -1
            else:
                sub[:, half_x - exclude:] = -1
            if sy > 0:
                sub[:half_y + exclude, :] = -1
            else:
                sub[half_y - exclude:, :] = -1
            idx = np.unravel_index(np.argmax(sub), sub.shape)  # (row, col)
            peaks.append((idx[1] - cx, idx[0] - cy))  # (u, v) 相对中心
    return peaks


# 在 padding 后的频谱上检测噪声峰
fp = np.zeros((P, Q)); fp[:M, :N] = noisy
F_pad = np.fft.fftshift(np.fft.fft2(fp))
cx, cy = P // 2, Q // 2
detected = detect_noise_peaks(F_pad, cx, cy)
print("detected peak coords (relative to center):", detected)


# ============ 4. 陷波(带阻) 滤波器 ============
def notch_reject(P, Q, centers, r=20):
    u = np.arange(P) - P // 2
    v = np.arange(Q) - Q // 2
    V, U = np.meshgrid(v, u)
    H = np.ones((P, Q), dtype=np.float64)
    for cu, cv in centers:
        for du, dv in [(cu, cv), (-cu, -cv)]:
            D2 = (U - du) ** 2 + (V - dv) ** 2
            H *= 1.0 - np.exp(-D2 / (2 * (r ** 2)))
    return H


# 使用检测到的峰（与理论 true_freq 一致）构建陷波
H_notch = notch_reject(P, Q, detected, r=22)
Image.fromarray((H_notch * 255).astype(np.uint8)).save(
    os.path.join(RES, "HW4-2_notch_filter.png"))  # 显示滤波器本身(亮=通过,暗=抑制)

clean = freq_filter_5steps(noisy, H_notch)
Image.fromarray(clean.astype(np.uint8)).save(os.path.join(RES, "HW4-2_phantom_denoised.png"))


# ============ 5. 频谱图 ============
def show_spectrum(F, name):
    mag = np.log(1 + np.abs(F))
    mag = (mag - mag.min()) / (mag.max() - mag.min()) * 255
    Image.fromarray(mag.astype(np.uint8)).save(os.path.join(RES, name))


show_spectrum(np.fft.fftshift(np.fft.fft2(noisy)), "HW4-2_spectrum_noisy.png")
show_spectrum(np.fft.fftshift(np.fft.fft2(clean)), "HW4-2_spectrum_denoised.png")

# 对照：同样噪声下，用理想低通(同尺度)无法去除周期噪声 -> 证明"选择滤波"必要
uu = np.arange(P) - P // 2
vv = np.arange(Q) - Q // 2
VV, UU = np.meshgrid(vv, uu)
D = np.sqrt(UU ** 2 + VV ** 2)
H_gauss_lp = np.exp(-(D ** 2) / (2 * (40 ** 2)))
clean_lp = freq_filter_5steps(noisy, H_gauss_lp)
Image.fromarray(clean_lp.astype(np.uint8)).save(os.path.join(RES, "HW4-2_phantom_gaussian_lp.png"))
show_spectrum(np.fft.fftshift(np.fft.fft2(clean_lp)), "HW4-2_spectrum_gaussian_lp.png")

print("HW4-2 done.")
