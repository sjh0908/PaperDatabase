import sys
sys.stdout.reconfigure(encoding='utf-8')
import os, zipfile

BASE = r"C:\Users\s\Desktop\HW4"
OUT = r"C:\Users\s\Desktop\24300680275-申家辉-hw4.zip"

# 收集待打包文件（不含脚本自身，避免自包含膨胀）
files = []
for name in ["HW4_report.pdf", "README.md"]:
    p = os.path.join(BASE, name)
    if os.path.exists(p):
        files.append((p, name))

for d, arc in [("results", "results"), ("report", "report"), ("data", "data"), ("src", "src")]:
    dp = os.path.join(BASE, d)
    if not os.path.isdir(dp):
        continue
    for fn in os.listdir(dp):
        fp = os.path.join(dp, fn)
        if os.path.isfile(fp):
            files.append((fp, f"{arc}/{fn}"))

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for fp, arcname in files:
        z.write(fp, arcname)
        print("added", arcname)

# 校验
with zipfile.ZipFile(OUT, "r") as z:
    bad = z.testzip()
    print("members:", len(z.namelist()), "testzip:", "OK" if bad is None else f"BAD {bad}")
print("zip size:", os.path.getsize(OUT), "bytes")
print("OUT:", OUT)
