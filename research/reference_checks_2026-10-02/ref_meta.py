"""Primary-source metadata for the references of manuscript/draft_v0.md: Crossref (DOIs) and the arXiv API (arXiv ids)."""
import json
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "rs-dic-llm-reference-check/1.0 (research notes; no contact given)"}


def get(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def crossref(doi):
    try:
        d = json.loads(get("https://api.crossref.org/works/" + doi))["message"]
    except Exception as e:  # noqa: BLE001
        print(f"[crossref {doi}] ERROR {e}")
        return
    authors = "; ".join(f"{a.get('given', '')} {a.get('family', a.get('name', ''))}".strip() for a in d.get("author", []))
    issued = d.get("issued", {}).get("date-parts", [[None]])[0]
    print(f"[crossref {doi}]\n  title: {' '.join(d.get('title', []))}\n  authors: {authors}\n  container: {' '.join(d.get('container-title', []))}"
          f" | vol {d.get('volume')} issue {d.get('issue')} pages {d.get('page') or d.get('article-number')} | issued {issued} | type {d.get('type')}")


def arxiv(ids):
    xml = get("http://export.arxiv.org/api/query?max_results=50&id_list=" + ",".join(ids))
    ns = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(xml)
    for e in root.findall("a:entry", ns):
        t = " ".join(e.find("a:title", ns).text.split())
        authors = "; ".join(a.find("a:name", ns).text for a in e.findall("a:author", ns))
        pub = e.find("a:published", ns).text[:10]
        upd = e.find("a:updated", ns).text[:10]
        jr = e.find("x:journal_ref", ns)
        cm = e.find("x:comment", ns)
        doi = e.find("x:doi", ns)
        eid = e.find("a:id", ns).text
        print(f"[arxiv {eid}]\n  title: {t}\n  authors: {authors}\n  published {pub}, updated {upd} | journal_ref: {jr.text if jr is not None else None}"
              f" | doi: {doi.text if doi is not None else None}\n  comment: {' '.join(cm.text.split()) if cm is not None else None}")


which = sys.argv[1]
if which == "crossref":
    for doi in sys.argv[2:]:
        crossref(doi)
        time.sleep(0.4)
else:
    arxiv(sys.argv[2:])
