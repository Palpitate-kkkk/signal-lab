import pathlib, re

P = pathlib.Path("views")
pat_single = re.compile(r'(?m)^[ \t]*\$\$([^\n$]+)\$\$[ \t]*$')

for p in sorted(P.glob("*.py")):
    s = p.read_text(encoding="utf-8")
    s2, n1 = pat_single.subn(lambda m: "$$\n" + m.group(1).strip() + "\n$$", s)
    s2, n2 = re.subn(r'\$\$([^$\n]+)\$\$', r'$\1$', s2)
    if n1 or n2:
        p.write_text(s2, encoding="utf-8")
    print(f"{p.name:24s} 单行$$拆成三行: {n1} 处 | 行内$$转$: {n2} 处")
    left = [i for i, l in enumerate(s2.split("\n"), 1) if "$$" in l]
    if left:
        print("     仍含 $$ 的行号:", left)

print()
print("完成 ✅")
