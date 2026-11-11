# 数字图像处理 HW4 —— 频率域滤波

**课程**：数字图像处理　**姓名**：申家辉　**学号**：24300680275　**日期**：2026-11-11

## 实验内容

| 题号 | 内容 | 关键实现 |
|------|------|----------|
| HW4-1 (1) | 频域低通平滑 | 五步法 + 高斯低通 / 理想低通（D₀=80），展示原图频谱、滤波后频谱、结果图 |
| HW4-1 (2) | 频域锐化 | 高斯/理想高通（边缘图）+ 非锐化掩模 Unsharp Mask（H=1+α(1−L)，α=1.0） |
| HW4-2 | 周期噪声去除 | Shepp-Logan 体膜 + 45°/−45° 正弦条纹；频谱四象限自动定位 4 个噪声峰 → 高斯带阻陷波滤波 |

## 目录结构

```
HW4/
├── HW4_report.pdf            # 实验报告（5 页，含原理/结果/分析）
├── README.md
├── data/                     # 原始图像（grace_hopper.jpg、shepp_logan.png）
├── results/                  # 全部单张结果图（滤波结果 + 滤波器 + 频谱）
├── report/                   # 报告用对比拼图
└── src/                      # 源码（全部手写，仅 DFT/IDFT 调用 NumPy 库）
    ├── HW4_1_freq_lowpass_sharpen.py
    ├── HW4_2_periodic_noise_removal.py
    ├── make_figures.py
    ├── make_report.py
    └── make_zip.py
```

## 运行方式

```powershell
py -3 src\HW4_1_freq_lowpass_sharpen.py     # 生成 HW4-1 结果
py -3 src\HW4_2_periodic_noise_removal.py   # 生成 HW4-2 结果
py -3 src\make_figures.py                    # 生成报告拼图
py -3 src\make_report.py                     # 生成 HW4_report.pdf
py -3 src\make_zip.py                        # 打包为桌面提交 zip
```

## 关键结论

1. 频率域“五步法”（补零→DFT→频域相乘→IDFT→裁剪）可统一实现平滑/锐化/选择滤波。
2. 低通以模糊与振铃为代价抑制高频；高斯低通过渡平滑、伪影轻于理想低通。
3. 非锐化掩模保留直流分量，锐化自然、几乎无过冲。
4. 规则周期噪声用陷波（带阻）滤波器在频域精确定位挖除，效果远优于全局低通。
