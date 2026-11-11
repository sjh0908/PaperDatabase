"""HW4 报告对比拼图：把各结果图拼成易读的对比图，供 PDF 嵌入。"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

RES = r"C:\Users\s\Desktop\HW4\results"
REP = r"C:\Users\s\Desktop\HW4\report"
os.makedirs(REP, exist_ok=True)

# 中文字体
plt.rcParams["font.family"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

DATA = r"C:\Users\s\Desktop\HW4\data"


def load(name):
    return np.array(Image.open(os.path.join(RES, name)).convert("L"))


def montage(images, titles, outname, ncol=None, figsize=(14, 5)):
    n = len(images)
    ncol = ncol or n
    nrow = (n + ncol - 1) // ncol
    fig, axes = plt.subplots(nrow, ncol, figsize=figsize)
    axes = np.atleast_1d(axes).ravel()
    for ax, (im, t) in zip(axes, zip(images, titles)):
        ax.imshow(im, cmap="gray", vmin=0, vmax=255)
        ax.set_title(t, fontsize=11)
        ax.axis("off")
    for ax in axes[n:]:
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(REP, outname), dpi=130, bbox_inches="tight")
    plt.close(fig)
    print("saved", outname)


# ---- HW4-1 低通平滑对比 ----
orig = np.array(Image.open(os.path.join(DATA, "grace_hopper.jpg")).convert("L"))
montage(
    [orig, load("HW4-1_gaussian_lowpass_D30.png"), load("HW4-1_ideal_lowpass_D30.png")],
    ["原图", "高斯低通 (D0=80)", "理想低通 (D0=80)"],
    "fig_HW4-1_lowpass.png", ncol=3, figsize=(13, 4.2),
)

# ---- HW4-1 频谱对比 ----
montage(
    [load("HW4-1_spectrum_original.png"),
     load("HW4-1_spectrum_gaussian_lowpass.png"),
     load("HW4-1_spectrum_ideal_lowpass.png")],
    ["原图频谱 (对数幅度)", "高斯低通后频谱", "理想低通后频谱"],
    "fig_HW4-1_spectrum_lowpass.png", ncol=3, figsize=(13, 4.2),
)

# ---- HW4-1 锐化对比 ----
montage(
    [orig, load("HW4-1_gaussian_highpass_D30.png"), load("HW4-1_unsharp_D30.png")],
    ["原图", "高斯高通 (边缘图)", "非锐化掩模 (锐化结果)"],
    "fig_HW4-1_sharpen.png", ncol=3, figsize=(13, 4.2),
)

# ---- HW4-2 周期噪声去除 ----
phantom = np.array(Image.open(os.path.join(DATA, "shepp_logan.png")).convert("L"))
montage(
    [phantom, load("HW4-2_phantom_noisy.png"), load("HW4-2_notch_filter.png"),
     load("HW4-2_phantom_denoised.png"), load("HW4-2_phantom_gaussian_lp.png")],
    ["体膜原图", "含周期噪声", "陷波滤波器 H", "陷波去噪结果", "对照: 理想低通(无效)"],
    "fig_HW4-2_pipeline.png", ncol=5, figsize=(16, 3.6),
)

# ---- HW4-2 频谱对比 ----
montage(
    [load("HW4-2_spectrum_noisy.png"), load("HW4-2_spectrum_denoised.png")],
    ["含噪图像频谱 (可见4个噪声冲击)", "去噪后频谱 (冲击被抑制)"],
    "fig_HW4-2_spectrum.png", ncol=2, figsize=(10, 4.2),
)

print("make_figures done.")
