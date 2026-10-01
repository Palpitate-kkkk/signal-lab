import pathlib, re, shutil

views = pathlib.Path("views")
bak = pathlib.Path(".fix_backup")
bak.mkdir(exist_ok=True)

# 行首 $$ 后面还有内容  ->  把内容挪到下一行
open_pat = re.compile(r'(?m)^[ \t]*\$\$(?=\S)(.*?)[ \t]*$')
# 行尾 $$ 前面还有内容  ->  把 $$ 挪到下一行
close_pat = re.compile(r'(?m)^(.*\S)[ \t]*\$\$[ \t]*$')

for p in sorted(views.glob("*.py")):
    s = p.read_text(encoding="utf-8")
    shutil.copy(p, bak / p.name)          # 先备份，改坏了能找回
    s2, n1 = open_pat.subn(lambda m: "$$\n" + m.group(1).strip(), s)
    s2, n2 = close_pat.subn(lambda m: m.group(1).strip() + "\n$$", s2)
    if n1 or n2:
        p.write_text(s2, encoding="utf-8")
    print(f"{p.name:22s} 开头$$拆行 {n1} 处 | 结尾$$拆行 {n2} 处")

print("\n—— 复查 ——")
bad = 0
for p in sorted(views.glob("*.py")):
    for i, l in enumerate(p.read_text(encoding="utf-8").split("\n"), 1):
        if "$$" in l and l.strip() != "$$":
            print(f"⚠️  {p.name}:{i}  {l.strip()[:70]}")
            bad += 1
print("✅ 所有 $$ 都已独占一行" if not bad else f"还有 {bad} 行需要处理")
