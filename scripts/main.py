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

    # 2. Find already processed queries to avoid duplicates
    import os
    processed_qids = set()
    queries_file = os.path.join(settings["output"]["phase1_dir"], settings["output"]["queries_file"])
    if os.path.exists(queries_file):
        with open(queries_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    processed_qids.add(line.split("\t")[0])
    
    remaining_queries = [q for q in queries if q["id"] not in processed_qids]
    logger.info(f"Skipping {len(processed_qids)} already processed queries. {len(remaining_queries)} remaining to scrape.")

    if not remaining_queries:
        logger.info("All queries have been scraped. Phase 1 is completely finished!")
        return

    # 3. Process remaining queries ONE BY ONE and save incrementally
    import time
    import random
    
    for i, query in enumerate(remaining_queries):
        logger.info(f"--- Starting Query {query['id']} ({i+1}/{len(remaining_queries)}) ---")
        
        # We call fetch_all_queries but pass only ONE query. 
        # This launches the browser, fetches 100, and closes the browser (good for avoiding bot detection)
        tweets = fetch_all_queries(
            queries=[query],
            settings=settings,
            auth_token=auth_token,
            ct0=ct0,
        )

        if tweets:
            # Build qrels for this batch
            relevant_count = settings["collection"]["relevant_count"]
            qrels = build_qrels(tweets, relevant_count)

            # Append to files immediately
            save_all(tweets, [query], qrels, settings)
            logger.info(f"Progress Saved: {query['id']} successfully appended to disk.")
        else:
            logger.warning(f"No tweets found for {query['id']}. Skipping save.")
            # Even if empty, we might want to save the query itself to mark it done, but we'll skip for safety.

        # 4. Long Anti-Bot Delay between queries (except the last one)
        if i < len(remaining_queries) - 1:
            delay = random.randint(15, 35)
            logger.info(f"Anti-Bot cooldown: waiting {delay} seconds before next query...")
            time.sleep(delay)

    logger.info("=== Phase 1 scraping complete! Upload the phase1/ folder to your Drive. ===")


if __name__ == "__main__":
    main()