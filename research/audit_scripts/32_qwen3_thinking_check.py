"""Was thinking really off in the Qwen3 outputs? (review of 2026-10-02, 'nice to have' item; CPU only)

The draft says the Qwen3 models were run with thinking disabled. This searches the stored definitions of all six Qwen3 instruct models in the main run, the
length control (E4) and the no-template control (E5) for think tags and for typical reasoning openings. The search is a heuristic (a regular expression), not a
classifier: it can miss reasoning text that does not look like these openings and can flag ordinary text. Output is recorded in outputs/32_qwen3_thinking_check.txt.
"""
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.stdout.reconfigure(encoding="utf-8")
PATTERN = re.compile(r"</?think|<\|?(?:think|reasoning)|\bthinking process\b|^\s*okay, (?:let|so|the user)|let me (?:think|start)|<\|im_start\|>", re.I)
GROUPS = {
    "main run": "data/definitions/Qwen3-*_42.jsonl",
    "length control (E4)": "results_2026-09-09_Runpod/results_e4 (lenght)/definitions/Qwen3-*_42.jsonl",
    "no-template control (E5)": "results_2026-09-09_Runpod/results_e5 (no template)/definitions/Qwen3-*_42.jsonl",
}
print("pattern:", PATTERN.pattern)
for group, pattern in GROUPS.items():
    files = sorted(glob.glob(str(ROOT / pattern)))
    assert len(files) == 6, (group, len(files))
    total = flagged = 0
    print(f"\n{group}: records with think tags or a reasoning opening, per model")
    for f in files:
        n = hit = 0
        example = None
        for line in open(f, encoding="utf-8"):
            if line.strip():
                n += 1
                text = json.loads(line).get("definition") or ""
                if PATTERN.search(text):
                    hit += 1
                    example = example or text[:100].replace("\n", " ")
        total += n
        flagged += hit
        print(f"   {Path(f).name[:-len('_42.jsonl')]:26} {hit:4d} of {n}" + (f"   e.g. {example!r}" if example else ""))
    print(f"   all six models: {flagged} of {total} ({100 * flagged / total:.2f} %)")
