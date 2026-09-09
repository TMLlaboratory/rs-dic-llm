# rs-dic-llm · E3 + E4 Parallel RunPod Guide

**Pod 1: 1× A100 80 GB → E3 (few-shot base models, ~2 h)**  
**Pod 2: 2× A100 80 GB → E4 (length-controlled instruct, ~6–10 h)**  
Both pods share one network volume. Start them at the same time.

---

## Phase 0 · Local preflight (do this first, on your own machine)

```bash
cd rs-dic-llm
```

Confirm the package is importable:

```bash
python -c "import sys; sys.path.insert(0,'src'); from rs_dic_llm.config import MODEL_REGISTRY; print(len(MODEL_REGISTRY), 'models OK')"
```

Expected: `23 models OK`

Push everything to GitHub:

```bash
git add -A
```

```bash
git commit -m "add E3/E4/E5 scripts and fix rs_dic_llm package"
```

```bash
git push
```

HuggingFace preparation (do this in a browser, not the terminal):
- Go to [hf.co/settings/tokens](https://huggingface.co/settings/tokens) → create a **Read** token → copy it somewhere safe (`hf_...`)
- Accept the Gemma 3 license at [hf.co/google/gemma-3-1b-it](https://huggingface.co/google/gemma-3-1b-it) (covers all Gemma 3 sizes)

---

## Phase 1 · Network volume (one time only)

1. RunPod sidebar → **Storage** → **+ New Network Volume**
2. Fill in:

| Field | Value |
|-------|-------|
| Name | `rs-dic-llm-weights` |
| Size | `600` GB |
| Datacenter | pick any region — **write it down** |

3. Click **Deploy** → it appears in the Storage list immediately.

> Both pods must be deployed in the **exact same region** as this volume. If they are in a different region the volume will not appear in the attach list.

---

## Phase 2 · Download weights on a CPU pod (~2–3 h, ~$0.30)

Do this once before starting either GPU pod.

### Deploy the CPU pod

1. RunPod → **Deploy** → switch the filter to **CPU**
2. Select **16 vCPU / 32 GB RAM**
3. **Datacenter**: same region as the network volume
4. **Environment variables** — add both:

```
HUGGINGFACE_HUB_TOKEN = hf_YOUR_TOKEN_HERE
HF_HOME               = /workspace/.cache
```

5. **Volumes** → **Attach** → select `rs-dic-llm-weights` → mount path: `/workspace`
6. Click **Deploy On-Demand**

### SSH into the CPU pod

```bash
git clone https://github.com/YOUR_USERNAME/rs-dic-llm.git && cd rs-dic-llm
```

```bash
pip install huggingface_hub
```

```bash
python -m experiments.download_weights
```

This downloads all 23 models (~435 GB) to `/workspace/.cache`. Wait for it to finish.

Verify:

```bash
du -sh /workspace/.cache
```

Expected output: something close to `435G`

```bash
ls /workspace/.cache/huggingface/hub/ | wc -l
```

Expected output: `23`

### Stop the CPU pod

In the RunPod console, click **Stop** on the CPU pod (not Terminate).  
Billing stops. The volume and weights are safe.

---

## Phase 3 · Deploy both GPU pods

Do this at the same time. Open two browser tabs if it helps.

### Pod 1 — E3 (1× A100 80 GB)

1. RunPod → **Deploy** → GPU tab
2. Search for **A100** → select the **80 GB** single-GPU option
3. **Datacenter**: **same region as the network volume**
4. **Template**: RunPod PyTorch (CUDA 12, PyTorch 2.x)
5. **Pod Storage**: `50` GB
6. **Environment variables**:

```
HUGGINGFACE_HUB_TOKEN = hf_YOUR_TOKEN_HERE
HF_HOME               = /workspace/.cache
```

7. **Volumes** → **Attach** → `rs-dic-llm-weights` → mount path: `/workspace`
8. Click **Deploy On-Demand**

### Pod 2 — E4 (2× A100 80 GB)

1. RunPod → **Deploy** → GPU tab
2. Search for **A100** → select the **2× 80 GB** option (listed as "160 GB" or "2× A100")
3. **Datacenter**: **same region as the network volume**
4. **Template**: RunPod PyTorch (CUDA 12, PyTorch 2.x)
5. **Pod Storage**: `50` GB
6. **Environment variables**:

```
HUGGINGFACE_HUB_TOKEN = hf_YOUR_TOKEN_HERE
HF_HOME               = /workspace/.cache
```

7. **Volumes** → **Attach** → `rs-dic-llm-weights` → mount path: `/workspace`
8. Click **Deploy On-Demand**

---

## Phase 4A · Set up and run E3 on Pod 1

SSH into Pod 1.

Confirm the weights are there:

```bash
du -sh /workspace/.cache
```

Expected: ~435 G. If empty, wrong region — stop and redeploy.

Confirm GPU:

```bash
nvidia-smi
```

Expected: one A100-SXM4-80GB.

Clone and install:

```bash
git clone https://github.com/YOUR_USERNAME/rs-dic-llm.git && cd rs-dic-llm
```

```bash
pip install -e ".[dev]"
```

Smoke test (10 words, no files saved, ~5 min):

```bash
python -m experiments.e3_fewshot_base --smoke
```

Check that:
- No import errors
- Each model prints `OK (X.X GB bf16)`
- R values are printed at the end

If smoke test passes, start the full run inside tmux:

```bash
tmux new -s e3
```

```bash
python -m experiments.e3_fewshot_base
```

Detach: `Ctrl+B` then `D`  
Reattach later: `tmux attach -t e3`

**Expected per-model times on A100 80 GB:**

| Model | Est. time |
|-------|-----------|
| Gemma3-270M-pt | 10–15 min |
| Gemma3-1B-pt | 12–18 min |
| Gemma3-4B-pt | 20–30 min |
| Gemma3-12B-pt | 35–50 min |
| Gemma3-27B-pt | 50–70 min |

**Total E3: ~2–3 hours**

---

## Phase 4B · Set up and run E4 on Pod 2

SSH into Pod 2.

Confirm the weights are there:

```bash
du -sh /workspace/.cache
```

Confirm both GPUs:

```bash
nvidia-smi
```

Expected: two A100-SXM4-80GB listed (160 GB total).

Clone and install:

```bash
git clone https://github.com/YOUR_USERNAME/rs-dic-llm.git && cd rs-dic-llm
```

```bash
pip install -e ".[dev]"
```

Smoke test (10 words, no files saved, ~5 min):

```bash
python -m experiments.e4_length_control --smoke
```

Check that:
- No import errors
- Models load without OOM errors
- When Qwen2.5-72B loads, it splits across both GPUs (`device_map="auto"` does this automatically — you will see it print layers being assigned to cuda:0 and cuda:1)

If smoke test passes, start the full run inside tmux:

```bash
tmux new -s e4
```

```bash
python -m experiments.e4_length_control
```

Detach: `Ctrl+B` then `D`  
Reattach later: `tmux attach -t e4`

**Expected per-model times on 2× A100 80 GB:**

| Size | Est. time |
|------|-----------|
| 0.5B–3B | 10–20 min |
| 7B–14B | 20–35 min |
| 27B–32B | 40–60 min |
| 72B | 60–90 min |

**Total E4: ~6–9 hours**

---

## Phase 5 · Monitor progress

You can check on each pod at any time.

Check E3 (Pod 1):

```bash
tmux attach -t e3
```

Check E4 (Pod 2):

```bash
tmux attach -t e4
```

Check how many definition files have been written so far:

```bash
ls data/definitions/e3_fewshot/*.jsonl 2>/dev/null | wc -l
```

```bash
ls data/definitions/e4_length/*.jsonl 2>/dev/null | wc -l
```

Expected at completion: 5 for E3, 17 for E4.

---

## Phase 6 · Download results

E3 will finish first (~2–3 h). Download it immediately — do not wait for E4.

### Download E3 results (from Pod 1)

Run these on your local machine. Replace `PORT` and `POD_IP` with the values from the RunPod console.

```bash
rsync -avz --progress -e "ssh -i ~/.ssh/id_rsa -p PORT" \
    root@POD_IP:~/rs-dic-llm/data/definitions/e3_fewshot/ \
    ./data/definitions/e3_fewshot/
```

```bash
rsync -avz --progress -e "ssh -i ~/.ssh/id_rsa -p PORT" \
    root@POD_IP:~/rs-dic-llm/results/e3_fewshot/ \
    ./results/e3_fewshot/
```

Verify:

```bash
ls data/definitions/e3_fewshot/*.jsonl | wc -l
```

Expected: `5`

```bash
python -c "
import json
d = json.load(open('results/e3_fewshot/summary.json'))
for m in d['models']:
    print(m['display'], '  R =', round(m.get('reciprocity_excess', 0), 2))
"
```

### Stop Pod 1 immediately after download

In RunPod console → **Stop** Pod 1.

### Download E4 results (from Pod 2)

When E4 finishes:

```bash
rsync -avz --progress -e "ssh -i ~/.ssh/id_rsa -p PORT" \
    root@POD_IP:~/rs-dic-llm/data/definitions/e4_length/ \
    ./data/definitions/e4_length/
```

```bash
rsync -avz --progress -e "ssh -i ~/.ssh/id_rsa -p PORT" \
    root@POD_IP:~/rs-dic-llm/results/e4_length/ \
    ./results/e4_length/
```

Verify:

```bash
ls data/definitions/e4_length/*.jsonl | wc -l
```

Expected: `17`

```bash
python -c "
import json
d = json.load(open('results/e4_length/summary.json'))
for m in d['models']:
    print(m['display'], '  R =', round(m.get('reciprocity_excess', 0), 2))
"
```

### Stop Pod 2 immediately after download

In RunPod console → **Stop** Pod 2.

---

## Phase 7 · Local analysis

Run on your own machine, no GPU needed.

```bash
python -c "
import json

for exp, path in [('E3 fewshot', 'results/e3_fewshot/summary.json'),
                  ('E4 length',  'results/e4_length/summary.json')]:
    d = json.load(open(path))
    Rs = [m.get('reciprocity_excess', 0) for m in d['models']]
    print(f'{exp}: n={len(Rs)}  R_min={min(Rs):.2f}  R_max={max(Rs):.2f}  R_mean={sum(Rs)/len(Rs):.2f}')
    print(f'  instruct range (>=8.9): {sum(1 for r in Rs if r >= 8.9)}/{len(Rs)} models')
    print()
"
```

---

## Cost estimate

| Item | Cost |
|------|------|
| Network volume 600 GB (~1 week) | ~$4–6 |
| CPU pod for download (~3 h) | ~$0.40 |
| Pod 1: 1× A100 80 GB (~3 h) | ~$4–6 |
| Pod 2: 2× A100 80 GB (~10 h) | ~$30–50 |
| **Total** | **~$40–62** |

---

## Quick reference

```
Phase 0  (local)
  python -c "..." → 23 models OK
  git push

Phase 1  Network volume
  RunPod → Storage → +New Network Volume → 600 GB → note region

Phase 2  CPU pod
  Deploy CPU (16 vCPU / 32 GB) → same region → attach volume → HF_HOME=/workspace/.cache
  pip install huggingface_hub
  python -m experiments.download_weights
  → Stop CPU pod when done

Phase 3  Deploy both GPU pods at the same time
  Pod 1: 1× A100 80 GB  → same region → attach volume
  Pod 2: 2× A100 80 GB  → same region → attach volume

Phase 4A  Pod 1 — E3
  git clone && pip install -e ".[dev]"
  python -m experiments.e3_fewshot_base --smoke
  tmux new -s e3
  python -m experiments.e3_fewshot_base

Phase 4B  Pod 2 — E4
  git clone && pip install -e ".[dev]"
  python -m experiments.e4_length_control --smoke
  tmux new -s e4
  python -m experiments.e4_length_control

Phase 6  Download
  rsync E3 results → Stop Pod 1
  rsync E4 results → Stop Pod 2

Phase 7  Local analysis
  python -c "... print R values ..."
```

---

## Troubleshooting

**`No module named 'rs_dic_llm'`**  
→ Run `pip install -e ".[dev]"` from the repo root, not from inside `src/`.

**Pod 2 shows only 1 GPU in `nvidia-smi`**  
→ You deployed a single A100 instead of 2×. Stop and redeploy with the 2× option.

**Volume not visible when attaching**  
→ Pod is in a different region than the volume. Stop and redeploy in the correct region.

**OOM error on 72B even with 2 GPUs**  
→ Run `nvidia-smi` and check that both GPUs show 80 GB. If only one is detected, see above.

**E4 crashes mid-run**  
→ Re-run `python -m experiments.e4_length_control` — completed models are skipped automatically via the `already done, skipping` check.

**Gemma 401 Unauthorized**  
→ `echo $HUGGINGFACE_HUB_TOKEN` — confirm it shows `hf_...` and that you accepted the license at hf.co/google/gemma-3-1b-it.
