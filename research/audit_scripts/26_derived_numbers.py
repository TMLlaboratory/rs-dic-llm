"""Derived numbers that the manuscript quotes and no earlier output prints (added 2026-10-02 after the draft review).

1. What the default filter keeps from the four matched pretrained models (1B-27B) on the 50 test words: read from the per-model lines of
   outputs/14_test_scored.txt (columns: n, non-definitions, dropped, correct drops, false drops, missed). Kept records = n - dropped;
   kept non-definitions = missed; kept definitions = kept - missed.
2. How much of each few-shot model's mutual-pair count involves one of the 12 words of the three examples: read from
   outputs/23_e3_example_words.txt (section 2). Removing every such pair would lower the count by this share at most.
Output: outputs/26_derived_numbers.txt. Descriptive; no reading was fixed in advance.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
OUT = ROOT / "research" / "audit_scripts" / "outputs"

print("1. WHAT THE DEFAULT FILTER KEEPS ON THE 50 TEST WORDS (first sentence), four matched pretrained models")
text14 = (OUT / "14_test_scored.txt").read_text(encoding="utf-8")
pattern = re.compile(r"^\s+(Gemma3-(?:1B|4B|12B|27B)-pt)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s", re.M)
rows = [(m.group(1), *map(int, m.groups()[1:])) for m in pattern.finditer(text14)]
assert len(rows) == 4, rows
tot_kept = tot_missed = 0
for name, n, nondef, dropped, correct, false, missed in rows:
    kept = n - dropped
    assert nondef == correct + missed
    tot_kept += kept
    tot_missed += missed
    print(f"   {name:15} n {n}  dropped {dropped}  kept {kept}  of which not definitions (missed) {missed}  definitions {kept - missed}")
print(f"   total kept {tot_kept}: definitions {tot_kept - tot_missed} ({100 * (tot_kept - tot_missed) / tot_kept:.1f} %), not definitions {tot_missed} "
      f"({100 * tot_missed / tot_kept:.1f} %, about 1 in {tot_kept / tot_missed:.1f})")

print("\n2. FEW-SHOT MUTUAL PAIRS THAT INVOLVE ONE OF THE 12 EXAMPLE WORDS (share of each model's mutual-pair count)")
text23 = (OUT / "23_e3_example_words.txt").read_text(encoding="utf-8")
shares = {}
for m in re.finditer(r"Gemma3-(\w+)\s+E3 base:.*?mutual pairs involving a word (\d+) of (\d+)", text23):
    size, k, n = m.group(1), int(m.group(2)), int(m.group(3))
    shares[size] = (k, n)
    print(f"   Gemma3-{size:5} {k} of {n} = {100 * k / n:.1f} %")
main = {s: 100 * k / n for s, (k, n) in shares.items() if s in ("1B", "4B", "12B", "27B")}
print(f"   at 1B-27B the reduction would be at most {max(main.values()):.1f} % (1B) and {min(v for s, v in main.items() if s != '1B'):.1f}-{max(v for s, v in main.items() if s != '1B'):.1f} % (4B-27B)")
