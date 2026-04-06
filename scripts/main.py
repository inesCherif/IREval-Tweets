"""
main.py — Run this to execute Phase 1 end-to-end.

Usage:
    python -m scripts.main
"""

from scripts.utils import get_logger, load_config, get_x_credentials
from scripts.fetch_tweets import fetch_all_queries
from scripts.build_qrels import build_qrels
from scripts.save_corpus import save_all

logger = get_logger("main")

QUERIES_CONFIG  = "config/queries.yaml"
SETTINGS_CONFIG = "config/settings.yaml"


def main():
    logger.info("=== IREval-Tweets — Phase 1: Building the test collection ===")

    # 1. Load config
    queries_cfg  = load_config(QUERIES_CONFIG)
    settings     = load_config(SETTINGS_CONFIG)
    queries      = queries_cfg["queries"]
    auth_token, ct0 = get_x_credentials()

    logger.info(f"Loaded {len(queries)} queries from {QUERIES_CONFIG}")

    # 2. Fetch tweets via Playwright (Cookie Injection)
    all_tweets = fetch_all_queries(
        queries=queries,
        settings=settings,
        auth_token=auth_token,
        ct0=ct0,
    )

    # 3. Build qrels
    relevant_count = settings["collection"]["relevant_count"]
    qrels = build_qrels(all_tweets, relevant_count)

    # 4. Save all output files
    save_all(all_tweets, queries, qrels, settings)

    logger.info("=== Phase 1 complete! Upload the phase1/ folder to your Drive. ===")


if __name__ == "__main__":
    main()