"""Extract the partial findings of the stopped agents: their own text, and each web call with a truncated result."""
import json, pathlib, sys

TASKS = pathlib.Path(r"C:\Users\josel\.claude\projects\S--Documents-ZZZ------\6b73f9e2-9dad-4f8f-b67a-a9bf2f287bd9\subagents")
AGENTS = [
    ("a6b2ed38b0c0eeb77", "Dictionary-graph references (VL16, Lev12, BM08, Har25, Eschrich & Liu, Goulet et al.)"),
    ("ae0ce7076906a4bc4", "Alignment and tuning references (Lin24, Res24, Lak25, Gud26, Price of Format, Ivgi24, 2606.20632)"),
    ("aa67658b5adffad8e", "Definition and competitor references (Bou26, Baa25, Sch23, Suresh23, Gammelgaard23, Pham23, Periti, Noraset, Giulianelli, OpenGloss, Ide)"),
    ("a036a3ab5c3618f0c", "Models, tools and networks (Gemma 3, Qwen2.5, Qwen3, WordNet, Brown, NLTK, NetworkX, Newman, Garlaschelli, Milo, Fosdick, Garwood)"),
    ("a37f67376630ac63b", "Venues (NLP2027, IPSJ SIG-NL, TopiCS, Cognitive Science, CogSci 2027, TACL/ARR, COLING 2027, workshops, JNLP)"),
]
LIMIT = int(sys.argv[2]) if len(sys.argv) > 2 else 1500


def text_of(content):
    if isinstance(content, str):
        return content
    out = []
    for c in content or []:
        if isinstance(c, dict):
            if c.get("type") == "text":
                out.append(c.get("text", ""))
            elif c.get("type") == "tool_result":
                out.append(text_of(c.get("content")))
    return "\n".join(out)


lines = []
for aid, title in AGENTS:
    path = TASKS / f"agent-{aid}.jsonl"
    lines.append(f"\n\n## {title}\n")
    if not path.exists():
        lines.append("(no transcript found)\n")
        continue
    pending = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            rec = json.loads(raw)
        except Exception:
            continue
        msg = rec.get("message") or {}
        role = msg.get("role") or rec.get("type")
        content = msg.get("content")
        if role == "assistant" and isinstance(content, list):
            for c in content:
                if c.get("type") == "text" and c.get("text", "").strip():
                    lines.append(f"\n**Agent note:** {c['text'].strip()}\n")
                elif c.get("type") == "tool_use":
                    inp = c.get("input", {})
                    desc = inp.get("url") or inp.get("query") or inp.get("command") or json.dumps(inp)[:200]
                    pending[c.get("id")] = (c.get("name"), desc, inp.get("prompt", ""))
        elif role == "user" and isinstance(content, list):
            for c in content:
                if c.get("type") == "tool_result":
                    name, desc, prompt = pending.get(c.get("tool_use_id"), ("?", "?", ""))
                    if name in ("ToolSearch",):
                        continue
                    res = text_of(c.get("content")).strip().replace("\r", "")
                    if len(res) > LIMIT:
                        res = res[:LIMIT] + " [...truncated]"
                    lines.append(f"\n- **{name}** `{str(desc)[:200]}`\n\n  " + res.replace("\n", "\n  ") + "\n")

out = pathlib.Path(sys.argv[1])
out.write_text("".join(lines), encoding="utf-8")
print(out, len("".join(lines)), "chars")
