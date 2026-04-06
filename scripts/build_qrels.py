"""
build_qrels.py — Generates qrels from tweet records.

Rule (from project spec):
  The first 30 tweets fetched per query = relevant (score 1)
  The remaining 70 per query           = not relevant (score 0)

TREC qrels format:
  query_id  0  doc_id  relevance
"""

from scripts.utils import get_logger

logger = get_logger(__name__)


def build_qrels(all_tweets: list[dict], relevant_count: int) -> list[dict]:
    """
    Given all tweet records, return a list of qrel judgments.
    Each judgment: { query_id, doc_id, relevance }
    """
    qrels = []

    for tweet in all_tweets:
        relevance = 1 if tweet["rank"] <= relevant_count else 0
        qrels.append({
            "query_id":  tweet["query_id"],
            "doc_id":    tweet["doc_id"],
            "relevance": relevance,
        })

    relevant = sum(1 for q in qrels if q["relevance"] == 1)
    logger.info(f"Built {len(qrels)} qrel entries — {relevant} relevant, "
                f"{len(qrels) - relevant} not relevant.")
    return qrels