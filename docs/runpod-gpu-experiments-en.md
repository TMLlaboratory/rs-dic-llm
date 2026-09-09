# rs-dic-llm · RunPod GPU Experiments Guide

**Three GPU sessions: E3 (few-shot base), E4 (length control), E5 (no template)**  
Hardware: B200 SXM (180 GB VRAM) recommended · A100 80 GB is sufficient for all models ≤ 32B

> This guide covers only the experiments that require GPU rental.  
> E1 (null model, CPU) and E2 (hand-validation) do not need RunPod.

---

## What you are running and why

| Session | Script | Models | Purpose | Est. time |
|---------|--------|--------|---------|-----------|
| E3 | `experiments/e3_fewshot_base.py` | 5 Gemma3-pt base models | Does few-shot prompting raise base R into instruct range? | 1–2 h |
| E4 | `experiments/e4_length_control.py` | 17 instruct models | Does R survive when definitions are capped at 8 words? | 5–9 h |
| E5 | `experiments/e5_no_template.py` | 17 instruct models | Is R caused by the chat template, or the trained weights? | 5–9 h |

Run E3 first — it is the fastest and its result shapes how you write about E4 and E5.

---

## Phase 0 · Local preflight (do this before opening RunPod)

```bash
cd rs-dic-llm
```

```bash
git status
```

Make sure there are no uncommitted changes you want to keep.

```bash
git add -A && git commit -m "add E3/E4/E5 experiment scripts and fix rs_dic_llm package" && git push
```

Verify the package structure is correct (the glob should return files):

```bash
python -c "import sys; sys.path.insert(0,'src'); from rs_dic_llm.config import MODEL_REGISTRY; print(len(MODEL_REGISTRY), 'models OK')"
```

Expected output: `23 models OK`

Check HuggingFace token and Gemma license:

- Log in at [hf.co/settings/tokens](https://huggingface.co/settings/tokens) → create a **Read** token (`hf_...`)
- Accept the Gemma 3 license at [hf.co/google/gemma-3-1b-it](https://huggingface.co/google/gemma-3-1b-it)  
  (one acceptance covers all Gemma 3 sizes in the same family)

---

## Phase 1 · Network volume (one time, reuse across all sessions)

1. RunPod sidebar → **Storage** → **+ New Network Volume**

| Setting | Value |
|---------|-------|
| Name | `rs-dic-llm-weights` |
| Size | `600` GB |
| Datacenter | any region — **write it down** |

2. Click **Deploy** → volume appears in Storage list immediately.

> All GPU pods in this guide must be deployed in the **same region** as this volume.

---

## Phase 2 · Download model weights (CPU pod, ~$0.12, ~2–3 h)

Do this once. All three GPU sessions share the same cached weights.

### Deploy a CPU pod

1. RunPod → **Deploy** → switch filter from **GPU** to **CPU**
2. Select **16 vCPU / 32 GB RAM** (~$0.10–0.15/hr)
3. **Datacenter**: same region as the network volume
4. **Environment variables**:

```
HUGGINGFACE_HUB_TOKEN = hf_YOUR_TOKEN_HERE
HF_HOME               = /workspace/.cache
```

5. **Volumes** → Attach → `rs-dic-llm-weights` → mount path `/workspace`
6. Click **Deploy On-Demand**

### SSH into the CPU pod and download

```bash
git clone https://github.com/YOUR_USERNAME/rs-dic-llm.git && cd rs-dic-llm
```

```bash
pip install huggingface_hub
```

```bash
python -m experiments.download_weights
```

This downloads all 23 models (~435 GB) to `/workspace/.cache`. Takes 1–3 hours depending on region bandwidth.

Check completion:

```bash
du -sh /workspace/.cache
```

Expected: ~435 GB

```bash
ls /workspace/.cache/huggingface/hub/ | wc -l
```

Expected: 23 directories (one per model)

### Stop the CPU pod

In the RunPod console, click **Stop** (NOT Terminate) on the CPU pod.  
Billing stops. The network volume and weights are preserved.

---

## Phase 3A · Session 1 — E3: Few-shot base models

**Goal**: Run 5 Gemma3-pt base models with few-shot prompts. Check if R enters the instruct range.  
**Time**: ~1–2 hours on B200

### Deploy GPU pod (E3)

1. RunPod → **Deploy** → GPU tab
2. Search **B200** or **A100 80GB** → select
3. **Datacenter**: same region as network volume (critical)
4. **Template**: RunPod PyTorch (CUDA 12, PyTorch 2.x)
5. **Pod Storage**: 50 GB (weights are on the network volume)
6. **Environment variables**:

```
HUGGINGFACE_HUB_TOKEN = hf_YOUR_TOKEN_HERE
HF_HOME               = /workspace/.cache
```

7. **Volumes** → Attach → `rs-dic-llm-weights` → mount path `/workspace`
8. Click **Deploy On-Demand**

### Connect and install

```bash
du -sh /workspace/.cache
```

Should show ~435 GB. If empty, the wrong region was selected — stop and redeploy.

```bash
nvidia-smi
```

Confirm GPU model and CUDA version.

```bash
git clone https://github.com/YOUR_USERNAME/rs-dic-llm.git && cd rs-dic-llm
```

```bash
pip install -e ".[dev]"
```

### Smoke test E3

```bash
python -m experiments.e3_fewshot_base --smoke
```

Expected output (10 words, no files written):
- No import errors
- Each model loads with `OK (X.X GB bf16)`
- R values are printed

### Run E3

```bash
tmux new -s e3
```

```bash
python -m experiments.e3_fewshot_base
```

Detach with `Ctrl+B → D`. Reattach with `tmux attach -t e3`.

**Per-model time estimates (B200)**:

| Model | Est. time |
|-------|-----------|
| Gemma3-270M-pt | 10–15 min |
| Gemma3-1B-pt | 12–18 min |
| Gemma3-4B-pt | 20–30 min |
| Gemma3-12B-pt | 35–50 min |
| Gemma3-27B-pt | 50–70 min |

### Download E3 results

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

Expected: 5 files

```bash
python -c "import json; d=json.load(open('results/e3_fewshot/summary.json')); [print(m['display'], 'R=', round(m.get('reciprocity_excess',0),2)) for m in d['models']]"
```

### Stop the GPU pod

In RunPod console → **Stop** (not Terminate) immediately after rsync completes.

---

## Phase 3B · Session 2 — E4: Length-controlled instruct models

**Goal**: Run all 17 instruct models with 8-word definition limit. Prove R is not verbosity.  
**Time**: ~5–9 hours on B200

### Deploy GPU pod (E4)

Same settings as E3 GPU pod. Make sure to attach `rs-dic-llm-weights` to the same region.

### Install and smoke test

```bash
git clone https://github.com/YOUR_USERNAME/rs-dic-llm.git && cd rs-dic-llm
```

```bash
pip install -e ".[dev]"
```

```bash
python -m experiments.e4_length_control --smoke
```

### Run E4

```bash
tmux new -s e4
```

```bash
python -m experiments.e4_length_control
```

Detach with `Ctrl+B → D`. Reattach with `tmux attach -t e4`.

If the session crashes mid-run, restart with the same command — completed models are skipped automatically.

**Per-model time estimates (B200)**:

| Size range | Est. time |
|------------|-----------|
| 0.5B–3B | 10–20 min |
| 7B–14B | 20–35 min |
| 27B–32B | 40–60 min |
| 72B | 80–110 min |

Total: ~5–8 hours for all 17 models.

### Download E4 results

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

Expected: 17 files

```bash
python -c "import json; d=json.load(open('results/e4_length/summary.json')); [print(m['display'], 'R=', round(m.get('reciprocity_excess',0),2)) for m in d['models']]"
```

### Stop the GPU pod

Stop immediately after rsync. Do not leave the B200 running overnight.

---

## Phase 3C · Session 3 — E5: Instruct models without chat template

**Goal**: Run all 17 instruct models without applying the chat template. Rules out template as the cause of R.  
**Time**: ~5–9 hours on B200

### Deploy GPU pod (E5)

Same settings as E4. Attach same network volume.

### Install and smoke test

```bash
git clone https://github.com/YOUR_USERNAME/rs-dic-llm.git && cd rs-dic-llm
```

```bash
pip install -e ".[dev]"
```

```bash
python -m experiments.e5_no_template --smoke
```

Note: without chat templates, instruct models may produce less structured output.  
The smoke test may show lower ok-rates than the main experiment — this is expected.

### Run E5

```bash
tmux new -s e5
```

```bash
python -m experiments.e5_no_template
```

Detach with `Ctrl+B → D`. Reattach with `tmux attach -t e5`.

Same per-model timing as E4.

### Download E5 results

```bash
rsync -avz --progress -e "ssh -i ~/.ssh/id_rsa -p PORT" \
    root@POD_IP:~/rs-dic-llm/data/definitions/e5_notemplate/ \
    ./data/definitions/e5_notemplate/
```

```bash
rsync -avz --progress -e "ssh -i ~/.ssh/id_rsa -p PORT" \
    root@POD_IP:~/rs-dic-llm/results/e5_notemplate/ \
    ./results/e5_notemplate/
```

Verify:

```bash
ls data/definitions/e5_notemplate/*.jsonl | wc -l
```

Expected: 17 files

```bash
python -c "import json; d=json.load(open('results/e5_notemplate/summary.json')); [print(m['display'], 'R=', round(m.get('reciprocity_excess',0),2)) for m in d['models']]"
```

### Stop the GPU pod

Stop immediately. The network volume persists for future sessions if needed.

---

## Phase 4 · Local analysis (after all three sessions)

Run locally — no GPU needed.

```bash
python -m experiments.analyse_results
```

Compare E3/E4/E5 against the main experiment baseline:

```bash
python -c "
import json, glob

experiments = {
    'main': 'results/full_summary.json',
    'e3_fewshot': 'results/e3_fewshot/summary.json',
    'e4_length': 'results/e4_length/summary.json',
    'e5_notemplate': 'results/e5_notemplate/summary.json',
}

for exp_name, path in experiments.items():
    try:
        d = json.load(open(path))
        models = d.get('models', [])
        if models:
            Rs = [m.get('reciprocity_excess', 0) for m in models if m.get('reciprocity_excess')]
            print(f'{exp_name:20} n={len(Rs):2}  R min={min(Rs):.2f}  max={max(Rs):.2f}  mean={sum(Rs)/len(Rs):.2f}')
    except FileNotFoundError:
        print(f'{exp_name:20} not found')
"
```

---

## Quick reference

```
Phase 0  (local)
  python -c "import sys; sys.path.insert(0,'src'); from rs_dic_llm.config import MODEL_REGISTRY; print(len(MODEL_REGISTRY))"
  git push

Phase 1  Network volume
  RunPod → Storage → +New Network Volume → 600 GB → note region

Phase 2  CPU download
  Deploy CPU pod → attach volume at /workspace → HF_HOME=/workspace/.cache
  pip install huggingface_hub
  python -m experiments.download_weights
  → Stop CPU pod

Phase 3A  E3  (1–2 h, B200)
  Deploy GPU pod (same region) → attach volume
  pip install -e ".[dev]"
  python -m experiments.e3_fewshot_base --smoke
  tmux new -s e3
  python -m experiments.e3_fewshot_base
  rsync results back
  → Stop GPU pod

Phase 3B  E4  (5–9 h, B200)
  Deploy GPU pod → attach volume
  pip install -e ".[dev]"
  python -m experiments.e4_length_control --smoke
  tmux new -s e4
  python -m experiments.e4_length_control
  rsync results back
  → Stop GPU pod

Phase 3C  E5  (5–9 h, B200)
  Deploy GPU pod → attach volume
  pip install -e ".[dev]"
  python -m experiments.e5_no_template --smoke
  tmux new -s e5
  python -m experiments.e5_no_template
  rsync results back
  → Stop GPU pod

Phase 4  Local analysis
  python -m experiments.analyse_results
```

---

## Cost estimate

| Component | Cost |
|-----------|------|
| Network volume (600 GB, ~2 weeks) | ~$8–12 |
| CPU pod for download (~2–3 h) | ~$0.30 |
| E3 GPU session (~2 h B200) | ~$6–10 |
| E4 GPU session (~9 h B200) | ~$27–40 |
| E5 GPU session (~9 h B200) | ~$27–40 |
| **Total** | **~$70–105** |

An A100 80GB at ~$1.50–2.00/hr would roughly halve the GPU cost at the expense of ~1.3× longer runtime.

---

## Troubleshooting

**Import error `No module named 'rs_dic_llm'`**  
→ Make sure you ran `pip install -e ".[dev]"` from the repo root (not from `src/`).

**Gemma model gives 401 Unauthorized**  
→ Check `echo $HUGGINGFACE_HUB_TOKEN` shows `hf_...`.  
→ Confirm you accepted the license at hf.co/google/gemma-3-1b-it.

**GPU pod cannot find the network volume**  
→ The pod and volume are in different regions. Terminate the pod, redeploy in the correct region.

**E5 ok-rate is very low (< 30%)**  
→ Expected for large instruct models without templates. The graph still forms from whatever definitions do appear. Do not re-run with a template — the low ok-rate is part of the result.

**Session disconnected mid-run**  
→ Re-SSH and `tmux attach -t <session_name>`. If the tmux session is gone (pod restarted), re-run the same command — completed models are skipped via the `already done, skipping` check.
