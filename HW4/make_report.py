# -*- coding: utf-8 -*-
"""HW4 课程报告 PDF 生成（reportlab + 系统 SimSun/SimHei 字体，中文正确）。"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                PageBreak, Table, TableStyle)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

BASE = r"C:\Users\s\Desktop\HW4"
RES = os.path.join(BASE, "results")
REP = os.path.join(BASE, "report")
OUT = os.path.join(BASE, "HW4_report.pdf")

# ---- 注册中文字体 ----
FONT_CANDIDATES = [
    (r"C:\Windows\Fonts\simsun.ttc", "SimSun"),
    (r"C:\Windows\Fonts\simhei.ttf", "SimHei"),
    (r"C:\Windows\Fonts\msyh.ttc", "MicrosoftYaHei"),
]
CN = "SimSun"
for path, name in FONT_CANDIDATES:
    if os.path.exists(path):
        try:
            pdfmetrics.registerFont(TTFont(name, path))
            CN = name
            break
        except Exception:
            continue
print("using CN font:", CN)

styles = getSampleStyleSheet()
body = ParagraphStyle("body", parent=styles["Normal"], fontName=CN,
                      fontSize=10.5, leading=17, spaceAfter=6,
                      alignment=4)  # 4=justify
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontName=CN,
                    fontSize=15, leading=20, spaceBefore=10, spaceAfter=8)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontName=CN,
                    fontSize=12.5, leading=17, spaceBefore=8, spaceAfter=5)
title = ParagraphStyle("title", parent=styles["Title"], fontName=CN,
                       fontSize=22, leading=28, spaceAfter=6)
sub = ParagraphStyle("sub", parent=styles["Normal"], fontName=CN,
                     fontSize=12, leading=18, alignment=1, spaceAfter=2)
cap = ParagraphStyle("cap", parent=styles["Normal"], fontName=CN,
                     fontSize=9, leading=13, alignment=1, textColor=colors.HexColor("#444444"))
small = ParagraphStyle("small", parent=styles["Normal"], fontName=CN,
                      fontSize=9.5, leading=15)


def img(path, width=16 * cm):
    from PIL import Image as PILImage
    p = os.path.join(REP, path)
    iw, ih = PILImage.open(p).size
    h = width * ih / iw
    return Image(p, width=width, height=h)


def fig_caption(text):
    return Paragraph(text, cap)


story = []

# ===== 封面 =====
story.append(Spacer(1, 3 * cm))
story.append(Paragraph("数字图像处理 · 课程实验报告", title))
story.append(Spacer(1, 0.3 * cm))
story.append(Paragraph("HW4：频率域滤波（低通平滑 / 频域锐化 / 周期噪声去除）", sub))
story.append(Spacer(1, 1.2 * cm))
cover = Table([
    ["学    院", "复旦大学 大数据学院"],
    ["姓    名", "申家辉"],
    ["学    号", "24300680275"],
    ["日    期", "2026 年 11 月 11 日"],
    ["实验环境", "Python 3.12 + NumPy + Matplotlib + ReportLab"],
], colWidths=[4 * cm, 10 * cm])
cover.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, -1), CN),
    ("FONTSIZE", (0, 0), (-1, -1), 11),
    ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#222222")),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
]))
story.append(cover)
story.append(PageBreak())

# ===== 一、实验原理 =====
story.append(Paragraph("一、实验原理", h1))
story.append(Paragraph(
    "频率域滤波基于二维傅里叶变换（本实验 DFT/IDFT 调用 NumPy 库函数实现）。"
    "对尺寸为 M×N 的图像 f(x,y)，频率域滤波遵循标准的“五步法”：", body))
steps = [
    "（1）补零：将图像补零扩展至 2M×2N，减少后续卷积的缠绕误差；",
    "（2）变换：对补零图像做二维 DFT，得频谱 F(u,v)；本实验统一用 fftshift 将零频移至中心，"
    "使滤波器 H 的坐标原点与频谱一致；",
    "（3）频域相乘：G(u,v) = H(u,v)·F(u,v)；",
    "（4）反变换：对 G 做 IDFT 并取实部得到空间域结果；",
    "（5）裁剪与缩放：取回原 M×N 区域，并裁剪到 [0,255]。",
]
for s in steps:
    story.append(Paragraph(s, body))
story.append(Paragraph(
    "常用滤波器：① 低通（理想 / 高斯）用于平滑，抑制高频细节；"
    "② 高通（理想 / 高斯）提取边缘；③ 非锐化掩模（unsharp mask）"
    "H = 1 + α(1 − L(u,v))，在保留原图基础上增强高频，是常用的频域锐化手段；"
    "④ 陷波（带阻）滤波器在频谱中若干对称位置挖掉窄带，专用于去除周期性噪声。", body))

# ===== 二、HW4-1 低通平滑 =====
story.append(Paragraph("二、HW4-1（1）：频域低通平滑", h1))
story.append(Paragraph(
    "对灰度图（人物照片，600×512）分别施加高斯低通与理想低通。高斯低通"
    " H(u,v)=exp(−D²/2D₀²)，截止半径 D₀=80；理想低通在 D₀ 内全通、之外全阻。"
    "下图为原图、两种低通的结果，以及对应的频谱（对数幅度）。可见低通滤除高频细节，"
    "画面明显变柔和、颗粒感下降；理想低通因频域突变产生更明显的振铃（ringing）伪影，"
    "而高斯低通过渡平滑、伪影更轻。", body))
story.append(img("fig_HW4-1_lowpass.png"))
story.append(fig_caption("图 1　低通平滑结果：原图 / 高斯低通 / 理想低通（D₀=80）"))
story.append(Spacer(1, 0.2 * cm))
story.append(img("fig_HW4-1_spectrum_lowpass.png"))
story.append(fig_caption("图 2　频谱图：原图频谱（含丰富高频）、低通后频谱（高频被抑制）"))

# ===== 三、HW4-1 频域锐化 =====
story.append(PageBreak())
story.append(Paragraph("三、HW4-1（2）：基于频域的锐化", h1))
story.append(Paragraph(
    "频域锐化本质上是“保留或放大高频、抑制低频”。本实验实现两类：① 高通滤波"
    "（理想 / 高斯），H = 1 − L(u,v)，输出为边缘图；② 非锐化掩模"
    " H = 1 + α(1 − L(u,v))（取 α=1.0、D₀=30），在原始图像基础上叠加高频分量，"
    "得到既保留整体亮度与结构、又边缘更清晰的锐化结果。下左为原图，"
    "中为高斯高通得到的边缘图，右为非锐化掩模锐化结果。", body))
story.append(img("fig_HW4-1_sharpen.png"))
story.append(fig_caption("图 3　频域锐化：原图 / 高斯高通（边缘图）/ 非锐化掩模（锐化结果）"))
story.append(Paragraph(
    "与空间中值/卷积锐化相比，频域锐化可一次性对全部频率施加连续增益，"
    "非锐化掩模因保留直流分量而不会出现亮度整体偏移或严重过冲（clipping），"
    "视觉效果自然。", body))

# ===== 四、HW4-2 周期噪声去除 =====
story.append(PageBreak())
story.append(Paragraph("四、HW4-2：频域选择滤波去除周期噪声", h1))
story.append(Paragraph(
    "选用标准 Shepp-Logan 大脑 CT 体膜（512×512）作为底图，叠加两组 45°/−45° "
    "方向的正弦条纹构成可见的周期噪声（噪声在 512 图上频率约为 60 周，"
    "在 2M×2N 零填充频谱中对应约 ±120 处出现对称冲击）。", body))
story.append(Paragraph(
    "处理流程：① 计算含噪图像频谱，可见中心直流与 4 个对称分布的高亮冲击（即噪声峰）；"
    "② 在频谱中自动定位 4 个最强离群峰（四象限各自取最大），"
    "构造陷波（带阻）滤波器 H=∏[1−exp(−D²/2r²)]，在对应位置及共轭位置挖除窄带（r=22）；"
    "③ 频域相乘后经 IDFT 取实部得到去噪结果。", body))
story.append(img("fig_HW4-2_pipeline.png"))
story.append(fig_caption(
    "图 4　处理流水线：体膜原图 / 含周期噪声 / 陷波滤波器 H（亮=通过、暗=抑制）/ "
    "陷波去噪结果 / 对照：理想低通（无法去除周期噪声）"))
story.append(Spacer(1, 0.2 * cm))
story.append(img("fig_HW4-2_spectrum.png"))
story.append(fig_caption("图 5　频谱对比：含噪频谱（4 个噪声冲击明显）/ 去噪后频谱（冲击被抑制）"))
story.append(Paragraph(
    "结果分析：陷波滤波后，体膜的条纹状周期噪声被有效消除，脑组织与头骨结构完好保留；"
    "而作为对照的理想低通虽能模糊图像，却无法定位并挖除离散的噪声频率，"
    "条纹依旧残留——这正是“频域选择滤波（陷波）”相对“全局低通”的必要性所在。", body))

# ===== 五、结论 =====
story.append(Paragraph("五、结论", h1))
story.append(Paragraph(
    "1）频率域“五步法”可统一实现平滑、锐化与选择滤波；DFT/IDFT 调用库函数、"
    "滤波器本身由手写为宜，便于理解频域运算本质。"
    "2）低通平滑会以振铃/模糊为代价抑制高频；高斯低通比理想低通伪影更轻。"
    "3）非锐化掩模在保留原图的同时增强边缘，是稳健的频域锐化方案。"
    "4）对于规则周期噪声，陷波（带阻）滤波器能在频域精确定位并挖除离散噪声峰，"
    "效果远优于全局低通。", body))
story.append(Spacer(1, 0.3 * cm))
story.append(Paragraph(
    "说明：本报告所有图像滤波算法均为手写实现（仅 DFT/IDFT 调用 NumPy 库函数），"
    "结果图与拼图由本实验脚本自动生成。", small))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(CN, 8)
    canvas.setFillColor(colors.HexColor("#888888"))
    canvas.drawCentredString(A4[0] / 2, 1.0 * cm,
                             "数字图像处理 HW4 实验报告 · 申家辉 24300680275")
    canvas.drawRightString(A4[0] - 1.5 * cm, 1.0 * cm, "第 %d 页" % doc.page)
    canvas.restoreState()


doc = SimpleDocTemplate(OUT, pagesize=A4,
                        leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                        topMargin=2.0 * cm, bottomMargin=1.8 * cm,
                        title="HW4 数字图像处理实验报告",
                        author="申家辉")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("report written:", OUT, os.path.getsize(OUT), "bytes")
