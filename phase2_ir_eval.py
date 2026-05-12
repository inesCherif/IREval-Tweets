"""
phase2_ir_eval.py — Complete Phase 2: Indexing, Retrieval & Evaluation with PyTerrier.

Project structure expected:
    project/
    ├── corpus/              # 2500 .txt files named {doc_id}.txt
    ├── phase1/
    │   ├── queries.txt      # format: "Q1\thormuz strait iran"
    │   └── qrels.txt        # format: "Q1 0 {doc_id} 1"
    └── phase2_ir_eval.py    ← this file

Outputs (created automatically):
    results/
    ├── evaluation.csv       # Summary table of all models × metrics
    ├── PR_curve.png         # Precision-Recall curves for every model
    └── {index}_{model}.csv  # Top-30 ranked results per model

Run:
    python phase2_ir_eval.py
"""

# ──────────────────────────────────────────────────────────────────────────────
# 0. DEPENDENCIES — install if missing
# ──────────────────────────────────────────────────────────────────────────────
import subprocess, sys

def _pip(*pkgs):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", *pkgs])

try:
    import pyterrier as pt
except ImportError:
    print("[setup] pyterrier not found — installing …")
    _pip("python-terrier")
    import pyterrier as pt

try:
    import pandas as pd
except ImportError:
    _pip("pandas")
    import pandas as pd

try:
    import matplotlib
    matplotlib.use("Agg")          # non-interactive backend — safe on any machine
    import matplotlib.pyplot as plt
except ImportError:
    _pip("matplotlib")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

import os, logging, warnings
warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("phase2")

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION  — change paths here if your layout differs
# ──────────────────────────────────────────────────────────────────────────────
CORPUS_DIR    = "corpus"                  # folder with {doc_id}.txt files
QUERIES_FILE  = "phase1/queries.txt"      # tab-separated: qid \t query_text
QRELS_FILE    = "phase1/qrels.txt"        # TREC format:   qid 0 docno label
RESULTS_DIR   = "results"                 # all outputs land here
TOP_K         = 100                       # documents to retrieve per query

INDEX_CONFIGS = {
    "raw": {
        "path":      "./index_raw",
        "stemmer":   "none",
        "stopwords": "none",
        "label":     "No stemming, no stopwords",
    },
    "stem": {
        "path":      "./index_stem",
        "stemmer":   "PorterStemmer",
        "stopwords": "none",
        "label":     "Porter Stemmer",
    },
    "nostop": {
        "path":      "./index_nostop",
        "stemmer":   "none",
        "stopwords": "terrier",          # Terrier's built-in English stoplist
        "label":     "No stemmer + stopword removal",
    },
}

MODELS = ["BM25", "TF_IDF", "Hiemstra_LM"]

# ──────────────────────────────────────────────────────────────────────────────
# 1. INIT PyTerrier
# ──────────────────────────────────────────────────────────────────────────────
def init_pyterrier():
    if not pt.java.started():
        log.info("Initialising PyTerrier (downloads Terrier jar on first run) …")
        pt.java.init()
    log.info("PyTerrier ready.")

# ──────────────────────────────────────────────────────────────────────────────
# 2. BUILD CORPUS DATAFRAME
# ──────────────────────────────────────────────────────────────────────────────
def load_corpus(corpus_dir: str) -> pd.DataFrame:
    """
    Read every .txt file in corpus_dir.
    Returns DataFrame with columns: docno (str), text (str).
    Files that cannot be read are skipped with a warning.
    """
    log.info(f"Loading corpus from '{corpus_dir}' …")

    if not os.path.isdir(corpus_dir):
        raise FileNotFoundError(
            f"Corpus directory '{corpus_dir}' not found. "
            "Make sure you run this script from the project root."
        )

    records = []
    skipped = 0

    for fname in os.listdir(corpus_dir):
        if not fname.endswith(".txt"):
            continue
        docno = fname[:-4]                        # strip .txt extension
        fpath = os.path.join(corpus_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as fh:
                text = fh.read().strip()
            if not text:                          # skip empty files
                skipped += 1
                continue
            records.append({"docno": docno, "text": text})
        except Exception as exc:
            log.warning(f"  Could not read '{fname}': {exc}")
            skipped += 1

    if not records:
        raise ValueError("No valid documents found in corpus. Aborting.")

    df = pd.DataFrame(records)
    log.info(f"  Loaded {len(df):,} documents ({skipped} skipped).")
    return df

# ──────────────────────────────────────────────────────────────────────────────
# 3. BUILD / LOAD INDEXES
# ──────────────────────────────────────────────────────────────────────────────
def build_index(corpus_df: pd.DataFrame, cfg: dict) -> pt.IndexRef:
    """
    Build a Terrier index from corpus_df according to cfg.
    If the index already exists on disk it is reused (skip rebuild).
    Returns a PyTerrier IndexRef.
    """
    index_path = os.path.abspath(cfg["path"])
    data_props = os.path.join(index_path, "data.properties")

    if os.path.exists(data_props):
        log.info(f"  Index already exists at '{index_path}' — loading.")
        return pt.IndexRef.of(index_path)

    log.info(f"  Building index → '{index_path}' [{cfg['label']}] …")
    os.makedirs(index_path, exist_ok=True)

    # Build indexer properties
    indexer_props = {
        "termpipelines": _termpipeline(cfg["stemmer"], cfg["stopwords"]),
    }

    indexer = pt.DFIndexer(
        index_path,
        overwrite=True,
        properties=indexer_props,
        verbose=True,
    )
    index_ref = indexer.index(corpus_df["text"], corpus_df["docno"])
    log.info(f"  Done — index built at '{index_path}'.")
    return index_ref


def _termpipeline(stemmer: str, stopwords: str) -> str:
    """
    Compose a Terrier termpipelines string from stemmer / stopwords settings.

    Terrier termpipelines examples:
        "Stopwords,PorterStemmer"   → remove stopwords then stem
        "PorterStemmer"             → stem only
        "Stopwords"                 → stopwords only
        ""                          → raw tokens
    """
    stages = []
    if stopwords != "none":
        stages.append("Stopwords")
    if stemmer != "none":
        stages.append(stemmer)
    return ",".join(stages) if stages else ""


def build_all_indexes(corpus_df: pd.DataFrame) -> dict:
    """Build (or load) all three indexes. Returns {name: IndexRef}."""
    log.info("=== STEP 3: Building indexes ===")
    indexes = {}
    for name, cfg in INDEX_CONFIGS.items():
        log.info(f"--- Index: {name} ({cfg['label']}) ---")
        indexes[name] = build_index(corpus_df, cfg)
    return indexes

# ──────────────────────────────────────────────────────────────────────────────
# 4. LOAD QUERIES
# ──────────────────────────────────────────────────────────────────────────────
def load_queries(queries_file: str) -> pd.DataFrame:
    """
    Read queries.txt (tab-separated: qid \t query_text).
    Returns DataFrame with columns: qid (str), query (str).
    """
    log.info(f"Loading queries from '{queries_file}' …")

    if not os.path.isfile(queries_file):
        raise FileNotFoundError(f"Queries file '{queries_file}' not found.")

    rows = []
    with open(queries_file, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t", 1)
            if len(parts) != 2:
                log.warning(f"  Skipping malformed query line: {line!r}")
                continue
            rows.append({"qid": parts[0].strip(), "query": parts[1].strip()})

    if not rows:
        raise ValueError("No valid queries found.")

    df = pd.DataFrame(rows)
    log.info(f"  Loaded {len(df)} queries.")
    return df

# ──────────────────────────────────────────────────────────────────────────────
# 5. LOAD QRELS
# ──────────────────────────────────────────────────────────────────────────────
def load_qrels(qrels_file: str) -> pd.DataFrame:
    """
    Read qrels.txt in TREC format: qid 0 docno label.
    Returns DataFrame with columns: qid (str), docno (str), label (int).
    """
    log.info(f"Loading qrels from '{qrels_file}' …")

    if not os.path.isfile(qrels_file):
        raise FileNotFoundError(f"Qrels file '{qrels_file}' not found.")

    rows = []
    with open(qrels_file, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 4:
                log.warning(f"  Skipping malformed qrels line: {line!r}")
                continue
            rows.append({
                "qid":   parts[0],
                "docno": parts[2],
                "label": int(parts[3]),
            })

    if not rows:
        raise ValueError("No valid qrels found.")

    df = pd.DataFrame(rows)
    log.info(f"  Loaded {len(df):,} qrel judgments ({df['label'].sum():,} relevant).")
    return df

# ──────────────────────────────────────────────────────────────────────────────
# 6. RUN RETRIEVAL
# ──────────────────────────────────────────────────────────────────────────────
def retrieve_all(indexes: dict, queries_df: pd.DataFrame) -> dict:
    """
    Run every (index × model) combination.
    Returns nested dict: results[index_name][model_name] = DataFrame of ranked results.
    """
    log.info("=== STEP 6: Running retrieval ===")
    all_results = {}

    for idx_name, index_ref in indexes.items():
        log.info(f"--- Retrieval with index: {idx_name} ---")
        all_results[idx_name] = {}

        for model_name in MODELS:
            log.info(f"    Model: {model_name} …")
            try:
                retriever = pt.BatchRetrieve(
                    index_ref,
                    wmodel=model_name,
                    num_results=TOP_K,
                    verbose=False,
                )
                results_df = retriever.transform(queries_df)
                all_results[idx_name][model_name] = results_df
                log.info(f"      → {len(results_df):,} result rows.")
            except Exception as exc:
                log.error(f"      Retrieval failed for {idx_name}/{model_name}: {exc}")
                all_results[idx_name][model_name] = pd.DataFrame()

    return all_results

# ──────────────────────────────────────────────────────────────────────────────
# 7. EVALUATE  (manual judged-pool — works on all PyTerrier versions)
# ──────────────────────────────────────────────────────────────────────────────
def _build_qrel_index(qrels_df: pd.DataFrame):
    """
    Pre-compute lookup structures from qrels so metric functions run fast.

    Returns:
        rel_map   : {(qid, docno): label}   — relevance of every judged doc
        total_rel : {qid: int}              — number of relevant docs per query
        judged    : {qid: set(docno)}       — set of judged docnos per query
    """
    rel_map   = {(str(r.qid), str(r.docno)): int(r.label) for r in qrels_df.itertuples()}
    total_rel = (qrels_df[qrels_df["label"] > 0]
                 .groupby("qid").size().to_dict())
    judged    = {qid: set(grp["docno"].astype(str))
                 for qid, grp in qrels_df.groupby("qid")}
    return rel_map, total_rel, judged


def _metrics_for_run(run_df: pd.DataFrame, rel_map, total_rel, judged) -> dict:
    """
    Judged-pool evaluation (standard TREC convention):
      - Unjudged documents count as non-relevant for P@k and Recall.
      - AP is computed over the condensed judged-only list.

    Returns mean metrics across all queries that have at least one relevant doc.
    """
    per_query = []

    for qid, grp in run_df.groupby("qid"):
        qid = str(qid)
        grp = grp.sort_values("rank").reset_index(drop=True)
        docs = grp["docno"].astype(str).tolist()

        n_rel = total_rel.get(qid, 0)
        if not n_rel:
            continue

        # Full relevance list (unjudged → 0)
        rels_full = [rel_map.get((qid, d), 0) for d in docs]

        # Condensed judged list for AP
        judged_q     = judged.get(qid, set())
        judged_rels  = [rel_map.get((qid, d), 0) for d in docs if d in judged_q]

        # Average Precision (judged-only condensed ranking)
        ap, rel_seen = 0.0, 0
        for i, r in enumerate(judged_rels):
            if r:
                rel_seen += 1
                ap += rel_seen / (i + 1)
        ap = ap / n_rel if n_rel else 0.0

        # Precision@k on full list
        def p_at(k):
            return sum(rels_full[:k]) / k if len(rels_full) >= k else 0.0

        # Recall@30
        rec30 = sum(rels_full[:30]) / n_rel if n_rel else 0.0

        per_query.append({
            "AP": ap,
            "P@1":  p_at(1),
            "P@5":  p_at(5),
            "P@10": p_at(10),
            "R@30": rec30,
        })

    if not per_query:
        return {}
    tmp = pd.DataFrame(per_query)
    return {col: round(float(tmp[col].mean()), 4) for col in tmp.columns}


def evaluate_all(all_results: dict, qrels_df: pd.DataFrame) -> pd.DataFrame:
    """
    Evaluate every (index × model) run against qrels using manual judged-pool
    metrics. Works independently of the PyTerrier version installed.
    Returns a summary DataFrame with one row per (index, model).
    """
    log.info("=== STEP 7: Evaluating (manual judged-pool) ===")

    rel_map, total_rel, judged = _build_qrel_index(qrels_df)
    rows = []

    for idx_name, model_results in all_results.items():
        for model_name, results_df in model_results.items():
            label = f"{idx_name}_{model_name}"

            if results_df.empty:
                log.warning(f"  Skipping empty results for {label}.")
                continue

            # Ensure docno is string so lookup keys match
            results_df = results_df.copy()
            results_df["docno"] = results_df["docno"].astype(str)

            metrics = _metrics_for_run(results_df, rel_map, total_rel, judged)
            if not metrics:
                log.warning(f"  No judged docs found for {label} — skipping.")
                continue

            row = {"Index": idx_name, "Model": model_name, **metrics}
            rows.append(row)
            log.info(
                f"  {label:25s}: MAP={metrics['AP']:.4f}  "
                f"P@1={metrics['P@1']:.4f}  P@5={metrics['P@5']:.4f}  "
                f"P@10={metrics['P@10']:.4f}  R@30={metrics['R@30']:.4f}"
            )

    summary = pd.DataFrame(rows).sort_values(["Index", "Model"]).reset_index(drop=True)
    return summary

# ──────────────────────────────────────────────────────────────────────────────
# 8. PRINT COMPARISON TABLE
# ──────────────────────────────────────────────────────────────────────────────
def print_comparison(summary_df: pd.DataFrame):
    """Pretty-print the evaluation summary to stdout."""
    log.info("=== STEP 8: Results comparison ===")
    if summary_df.empty:
        print("No evaluation results to display.")
        return

    print("\n" + "="*80)
    print("  EVALUATION SUMMARY — all models across all indexes")
    print("="*80)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 120)
    pd.set_option("display.float_format", "{:.4f}".format)
    print(summary_df.to_string(index=False))
    print("="*80 + "\n")

# ──────────────────────────────────────────────────────────────────────────────
# 9. SAVE RESULTS
# ──────────────────────────────────────────────────────────────────────────────
def save_results(
    summary_df: pd.DataFrame,
    all_results: dict,
    qrels_df: pd.DataFrame,
    out_dir: str,
):
    """
    Save:
      - results/evaluation.csv
      - results/{index}_{model}.csv  (top-30 per run)
      - results/PR_curve.png
    """
    log.info(f"=== STEP 9: Saving results to '{out_dir}/' ===")
    os.makedirs(out_dir, exist_ok=True)

    # 9a. Evaluation CSV
    eval_path = os.path.join(out_dir, "evaluation.csv")
    summary_df.to_csv(eval_path, index=False)
    log.info(f"  Saved evaluation table → {eval_path}")

    # 9b. Per-run ranked results
    for idx_name, model_results in all_results.items():
        for model_name, results_df in model_results.items():
            if results_df.empty:
                continue
            fname = f"{idx_name}_{model_name}.csv"
            fpath = os.path.join(out_dir, fname)
            results_df.to_csv(fpath, index=False)
            log.info(f"  Saved ranked results  → {fpath}")

    # 9c. Precision-Recall curve
    _plot_pr_curve(all_results, qrels_df, out_dir)


def _plot_pr_curve(all_results: dict, qrels_df: pd.DataFrame, out_dir: str):
    """
    Compute interpolated 11-point Precision-Recall curves for every run
    and save a single PNG with all curves overlaid.
    """
    log.info("  Computing Precision-Recall curves …")

    # Build a lookup: {(qid, docno): label}
    relevance_map = {
        (row["qid"], row["docno"]): row["label"]
        for _, row in qrels_df.iterrows()
    }

    # For each (index × model) compute mean P-R curve across queries
    pr_data = {}

    for idx_name, model_results in all_results.items():
        for model_name, results_df in model_results.items():
            if results_df.empty:
                continue
            label = f"{idx_name}_{model_name}"

            # Collect per-query PR curves then average
            recall_points = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            interp_precisions = []   # list of lists, one per query

            for qid, grp in results_df.groupby("qid"):
                grp = grp.sort_values("rank").reset_index(drop=True)

                # Count total relevant docs for this query
                total_rel = sum(
                    1 for _, r in qrels_df[qrels_df["qid"] == qid].iterrows()
                    if r["label"] > 0
                )
                if total_rel == 0:
                    continue

                # Build precision/recall arrays step by step
                rel_seen = 0
                precisions, recalls = [], []
                for i, row in grp.iterrows():
                    is_rel = relevance_map.get((qid, row["docno"]), 0) > 0
                    if is_rel:
                        rel_seen += 1
                    rank = i + 1
                    precisions.append(rel_seen / rank)
                    recalls.append(rel_seen / total_rel)

                # Interpolate at standard recall levels
                interp = []
                for r_thresh in recall_points:
                    p_at_r = max(
                        (p for p, r in zip(precisions, recalls) if r >= r_thresh),
                        default=0.0,
                    )
                    interp.append(p_at_r)
                interp_precisions.append(interp)

            if not interp_precisions:
                continue

            # Average across queries
            mean_prec = [
                sum(col) / len(col)
                for col in zip(*interp_precisions)
            ]
            pr_data[label] = (recall_points, mean_prec)

    if not pr_data:
        log.warning("  No PR data to plot.")
        return

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(10, 7))
    linestyles = ["-", "--", "-."]
    colours    = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
                  "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22"]
    for i, (label, (recalls, precisions)) in enumerate(pr_data.items()):
        ax.plot(
            recalls,
            precisions,
            marker="o",
            markersize=4,
            linestyle=linestyles[i % len(linestyles)],
            color=colours[i % len(colours)],
            label=label,
        )

    ax.set_xlabel("Recall", fontsize=13)
    ax.set_ylabel("Precision", fontsize=13)
    ax.set_title("Interpolated 11-Point Precision-Recall Curves\n(mean over all queries)", fontsize=14)
    ax.legend(fontsize=8, loc="upper right", ncol=2)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    pr_path = os.path.join(out_dir, "PR_curve.png")
    fig.savefig(pr_path, dpi=150)
    plt.close(fig)
    log.info(f"  Saved PR curve → {pr_path}")

# ──────────────────────────────────────────────────────────────────────────────
# MAIN ORCHESTRATOR
# ──────────────────────────────────────────────────────────────────────────────
def main():
    log.info("=== IREval-Tweets — Phase 2: Indexing, Retrieval & Evaluation ===\n")

    # Step 1 — init PyTerrier
    init_pyterrier()

    # Step 2 — load corpus
    log.info("=== STEP 2: Loading corpus ===")
    corpus_df = load_corpus(CORPUS_DIR)

    # Step 3 — build indexes
    indexes = build_all_indexes(corpus_df)

    # Step 4 — load queries
    log.info("=== STEP 4: Loading queries ===")
    queries_df = load_queries(QUERIES_FILE)

    # Step 5 — load qrels
    log.info("=== STEP 5: Loading qrels ===")
    qrels_df = load_qrels(QRELS_FILE)

    # Step 6 — retrieval
    all_results = retrieve_all(indexes, queries_df)

    # Step 7 — evaluation
    summary_df = evaluate_all(all_results, qrels_df)

    # Step 8 — print table
    print_comparison(summary_df)

    # Step 9 — save everything
    save_results(summary_df, all_results, qrels_df, RESULTS_DIR)

    log.info("=== Phase 2 complete! Check the 'results/' folder. ===")


if __name__ == "__main__":
    main()