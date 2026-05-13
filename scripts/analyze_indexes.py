"""
analyze_indexes.py — Extracts indexation statistics for the presentation.
"""
import sys
import os

# Add project root to sys.path so we can import phase2_ir_eval
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pyterrier as pt
import pandas as pd
import logging
from phase2_ir_eval import INDEX_CONFIGS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("analyze_indexes")

def main():
    if not pt.java.started():
        log.info("Initialising PyTerrier...")
        pt.java.init()

    stats = []

    for name, cfg in INDEX_CONFIGS.items():
        idx_path = os.path.abspath(cfg["path"])
        if not os.path.exists(idx_path):
            log.warning(f"Index {name} not found at {idx_path}. Did you run phase2_ir_eval.py?")
            continue
        
        try:
            indexref = pt.IndexRef.of(idx_path)
            index = pt.IndexFactory.of(indexref)
            collStats = index.getCollectionStatistics()
            
            stats.append({
                "Index Strategy": cfg["label"],
                "Documents": collStats.numberOfDocuments,
                "Total Tokens": collStats.numberOfTokens,
                "Vocabulary Size (Unique Terms)": collStats.numberOfUniqueTerms,
                "Total Postings": collStats.numberOfPointers
            })
            log.info(f"Loaded stats for {name}")
        except Exception as e:
            log.error(f"Error loading {name}: {e}")

    if stats:
        df = pd.DataFrame(stats)
        os.makedirs("results", exist_ok=True)
        out_path = "results/index_statistics.csv"
        df.to_csv(out_path, index=False)
        log.info(f"\nSaved statistics to {out_path}\n")
        
        # Pretty print for the console
        print("\n" + "="*80)
        print("  INDEXATION STATISTICS")
        print("="*80)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", 120)
        print(df.to_string(index=False))
        print("="*80 + "\n")
    else:
        log.warning("No statistics were generated.")

if __name__ == "__main__":
    main()
