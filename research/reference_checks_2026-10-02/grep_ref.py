"""Search a downloaded source for a regex, across line breaks, and print each hit with some context.

usage: python grep_ref.py name "regex" [context_chars=220] [max_hits=6]
"""
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
D = pathlib.Path(__file__).parent / "refs"
name, pattern = sys.argv[1], sys.argv[2]
ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 220
max_hits = int(sys.argv[4]) if len(sys.argv) > 4 else 6
text = (D / f"{name}.txt").read_text(encoding="utf-8", errors="replace")
flat = re.sub(r"\s+", " ", text)
hits = list(re.finditer(pattern, flat, flags=re.I))
print(f"[{name}] /{pattern}/ -> {len(hits)} hit(s)")
for m in hits[:max_hits]:
    a, b = max(0, m.start() - ctx), min(len(flat), m.end() + ctx)
    print("   ..." + flat[a:b] + "...\n")
