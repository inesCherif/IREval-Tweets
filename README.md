# IREval-Tweets
 
Information Retrieval evaluation system built with PyTerrier on a self-constructed tweet corpus.
 
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)
![PyTerrier](https://img.shields.io/badge/PyTerrier-0.13-green)
![TREC-style](https://img.shields.io/badge/Evaluation-TREC--style-orange)
 
**Topic:** Iran War &nbsp;·&nbsp; **Corpus:** 2 500 tweets · 25 queries · TREC qrels
 
---
 
## Overview
 
This project builds and evaluates a complete Information Retrieval pipeline from scratch — scraping a real tweet corpus, indexing it three ways, running three retrieval models, and measuring performance with standard TREC metrics.
 
It is structured in two phases:
 
| Phase | Goal | Output |
|-------|------|--------|
| **Phase 1** | Build the test collection | `tweets.jsonl` · `queries.txt` · `qrels.txt` |
| **Phase 2** | Index, retrieve & evaluate | `evaluation.csv` · ranked results · PR curve |
 
---
 
## Phase 1 — Building the test collection
 
> Deadline: 18 April 2026
 
### What it produces
 
| File | Description |
|------|-------------|
| `phase1/tweets.jsonl` | 2 500 tweets (100 per query × 25 queries) |
| `phase1/tweets_clean.jsonl` | Cleaned version (no URLs, mentions, hashtags) |
| `phase1/queries.txt` | 25 queries in TREC tab-separated format |
| `phase1/qrels.txt` | Relevance judgments — first 30 per query = relevant (1), next 70 = not relevant (0) |
| `corpus/` | 2 391 individual `{doc_id}.txt` files (cleaned tweet text) |
| `collection.spec` | Absolute paths of all corpus files for Terrier |
 
### Setup
 
**1. Clone the repo**
```bash
git clone https://github.com/inesCherif/IREval-Tweets.git
cd IREval-Tweets
```
 
**2. Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows
```
 
**3. Install dependencies**
```bash
pip install -r requirements.txt
playwright install chromium
```
 
**4. Set up your X (Twitter) session cookies**
 
X blocks standard login automation. We inject session tokens from your active browser session instead:
 
1. Open [x.com](https://x.com) and log in.
2. Press **F12** → **Application** tab (Chrome/Edge) or **Storage** tab (Firefox).
3. Expand **Cookies** → click `https://x.com`.
4. Copy the values for `auth_token` and `ct0`.
5. Run `cp .env.example .env` then paste your tokens:
```env
X_AUTH_TOKEN=your_auth_token_here
X_CT0=your_ct0_here
```
 
**5. Run Phase 1**
```bash
python -m scripts.main
```
 
The script runs queries one by one, saves results incrementally, and resumes automatically if interrupted.
 
---
 
## Phase 2 — Indexing, retrieval & evaluation
 
> Deadline: 02 May 2026
 
### What it produces
 
| File | Description |
|------|-------------|
| `index_raw/` | Terrier index — raw lexemes (no stemming, no stopword removal) |
| `index_stem/` | Terrier index — Porter Stemmer |
| `index_nostop/` | Terrier index — stopword removal (Terrier English list) |
| `results/evaluation.csv` | MAP · P@1 · P@5 · P@10 · R@30 for all 9 combinations |
| `results/{index}_{model}.csv` | Top-30 ranked results per run (9 files) |
| `results/PR_curve.png` | Interpolated 11-point Precision-Recall curves (mean over 25 queries) |
 
### Models evaluated
 
| Model | Type | Notes |
|-------|------|-------|
| `BM25` | Probabilistic | Default params: k1=1.2, b=0.75 |
| `TF_IDF` | Vector space | Best overall MAP on this corpus |
| `Hiemstra_LM` | Language model | Jelinek-Mercer smoothing λ=0.15 |
 
### Requirements
 
Phase 2 requires **Java 11+** on your PATH. Set `JAVA_HOME` before running:
 
```powershell
# Windows (PowerShell)
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.18.8-hotspot"
```
 
```bash
# Mac / Linux
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
```
 
### Run Phase 2
 
```bash
python phase2_ir_eval.py
```
 
Indexes are built once and reused on subsequent runs. Delete `index_*/` folders to force a rebuild.
 
### Key results
 
| Index | Model | MAP | P@5 | P@10 | R@30 |
|-------|-------|-----|-----|------|------|
| **nostop** | **TF_IDF** | **0.0938** | **0.280** | 0.260 | 0.260 |
| nostop | Hiemstra_LM | 0.0885 | 0.232 | **0.272** | 0.248 |
| stem | TF_IDF | 0.0919 | 0.224 | 0.240 | **0.264** |
| raw | BM25 | 0.0764 | 0.144 | 0.192 | 0.235 |
 
Best overall: **nostop + TF_IDF**. Stemming degrades precision on this corpus due to heavy use of named entities (IRGC, Khamenei, Hormuz).
 
---
 
## Project structure
 
```
IREval-Tweets/
├── .env                    ← Your credentials (never committed)
├── .env.example            ← Credentials template
├── phase2_ir_eval.py       ← Phase 2 entry point (single file)
├── config/
│   ├── queries.yaml        ← 25 queries
│   └── settings.yaml       ← Collection & output settings
├── scripts/                ← Phase 1 modules
│   ├── main.py
│   ├── fetch_tweets.py
│   ├── clean_corpus.py
│   ├── build_qrels.py
│   ├── save_corpus.py
│   ├── generate_spec.py
│   └── utils.py
├── phase1/                 ← Phase 1 outputs
│   ├── tweets.jsonl
│   ├── tweets_clean.jsonl
│   ├── queries.txt
│   └── qrels.txt
├── corpus/                 ← 2 391 cleaned tweet .txt files
├── index_raw/              ← Terrier index (raw)
├── index_stem/             ← Terrier index (stemmed)
├── index_nostop/           ← Terrier index (no stopwords)
├── results/                ← Phase 2 outputs
│   ├── evaluation.csv
│   ├── PR_curve.png
│   └── *.csv               ← Ranked results per run
├── collection.spec
└── requirements.txt
```
 
---
 
## Evaluation methodology
 
Evaluation follows the **TREC judged-pool convention**. Since PyTerrier retrieves from a global index (all 2 391 tweets mixed), documents not present in a query's judged pool are treated as non-relevant. Average Precision is computed over the condensed judged-only ranking — consistent with standard TREC Microblog evaluation practice.
 
---
 
## Dependencies
 
| Package | Version | Purpose |
|---------|---------|---------|
| `python-terrier` | ≥ 0.11 | Indexing & retrieval (wraps Terrier Java) |
| `playwright` | ≥ 1.40 | Tweet scraping |
| `pandas` | ≥ 2.0 | DataFrames throughout |
| `matplotlib` | ≥ 3.8 | PR curve plot |
| `python-dotenv` | any | Credentials from `.env` |
| `pyyaml` | any | Config files |
| Java JDK | 11 – 21 | Required by Terrier |
 
---
 
*ISAMM · Université de la Manouba · Systèmes de Recherche d'Information 2025–2026*
 
