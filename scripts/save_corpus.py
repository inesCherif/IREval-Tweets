"""
save_corpus.py — Writes the 3 output files:
  - tweets.jsonl   (one tweet per line as JSON)
  - queries.txt    (tab-separated: id <TAB> text)
  - qrels.txt      (TREC format: qid 0 docid relevance)
"""

import json
import os
from scripts.utils import get_logger, ensure_dir

logger = get_logger(__name__)


def save_tweets_jsonl(all_tweets: list[dict], output_path: str) -> None:
    """Write tweets as JSON Lines file (one tweet per line)."""
    ensure_dir(os.path.dirname(output_path))
    with open(output_path, "w", encoding="utf-8") as f:
        for tweet in all_tweets:
            f.write(json.dumps(tweet, ensure_ascii=False) + "\n")
    logger.info(f"Saved {len(all_tweets)} tweets → {output_path}")


def save_queries_txt(queries: list[dict], output_path: str) -> None:
    """Write queries file in tab-separated format: id <TAB> text."""
    ensure_dir(os.path.dirname(output_path))
    with open(output_path, "w", encoding="utf-8") as f:
        for q in queries:
            f.write(f"{q['id']}\t{q['text']}\n")
    logger.info(f"Saved {len(queries)} queries → {output_path}")


def save_qrels_txt(qrels: list[dict], output_path: str) -> None:
    """Write qrels file in TREC format: qid 0 docid relevance."""
    ensure_dir(os.path.dirname(output_path))
    with open(output_path, "w", encoding="utf-8") as f:
        for q in qrels:
            f.write(f"{q['query_id']} 0 {q['doc_id']} {q['relevance']}\n")
    logger.info(f"Saved {len(qrels)} qrel entries → {output_path}")


def save_all(
    all_tweets: list[dict],
    queries: list[dict],
    qrels: list[dict],
    settings: dict,
) -> None:
    """Convenience wrapper that saves all three output files."""
    out_dir = settings["output"]["phase1_dir"]

    save_tweets_jsonl(
        all_tweets,
        os.path.join(out_dir, settings["output"]["corpus_file"]),
    )
    save_queries_txt(
        queries,
        os.path.join(out_dir, settings["output"]["queries_file"]),
    )
    save_qrels_txt(
        qrels,
        os.path.join(out_dir, settings["output"]["qrels_file"]),
    )