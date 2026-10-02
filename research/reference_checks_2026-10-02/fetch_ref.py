"""Download a source and turn it into plain text: PDFs with pdftotext, HTML with a crude tag strip.

usage: python fetch_ref.py URL name [URL name ...]     -> refs/<name>.raw and refs/<name>.txt
       python grep_ref.py name "regex" [width]         (see grep_ref.py)
"""
import html
import pathlib
import re
import subprocess
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
D = pathlib.Path(__file__).parent / "refs"
D.mkdir(exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (rs-dic-llm reference check; research notes)"}


def fetch(url, name):
    raw = D / f"{name}.raw"
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=90) as r:
            data = r.read()
    except Exception as e:  # noqa: BLE001
        print(f"{name}: FAILED {url} -> {e}")
        return
    raw.write_bytes(data)
    txt = D / f"{name}.txt"
    if data[:5] == b"%PDF-":
        subprocess.run(["pdftotext", "-layout", str(raw), str(txt)], check=False)
    else:
        t = data.decode("utf-8", errors="replace")
        t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S | re.I)
        t = re.sub(r"<br\s*/?>|</p>|</div>|</h\d>|</li>|</tr>", "\n", t, flags=re.I)
        t = re.sub(r"<[^>]+>", " ", t)
        t = html.unescape(t)
        t = re.sub(r"[ \t\r\f\v]+", " ", t)
        t = re.sub(r"\n\s*\n+", "\n\n", t)
        txt.write_text(t, encoding="utf-8")
    print(f"{name}: {len(data)} bytes raw ({'pdf' if data[:5] == b'%PDF-' else 'html'}), {txt.stat().st_size if txt.exists() else 0} bytes text  <- {url}")


args = sys.argv[1:]
for i in range(0, len(args) - 1, 2):
    fetch(args[i], args[i + 1])
