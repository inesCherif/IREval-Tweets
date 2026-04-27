"""
generate_spec.py — Generates collection.spec containing absolute paths of all corpus files.
"""

import os
from scripts.utils import get_logger

logger = get_logger(__name__)

CORPUS_DIR = "corpus"
OUTPUT_FILE = "collection.spec"

def main():
    logger.info("Generating collection.spec...")
    
    if not os.path.exists(CORPUS_DIR):
        logger.error(f"Directory '{CORPUS_DIR}' does not exist.")
        return
        
    # Get absolute path of the corpus directory
    abs_corpus_dir = os.path.abspath(CORPUS_DIR)
    
    # Collect all .txt files
    txt_files = []
    for filename in os.listdir(abs_corpus_dir):
        if filename.endswith(".txt"):
            txt_files.append(os.path.join(abs_corpus_dir, filename))
            
    if not txt_files:
        logger.warning(f"No .txt files found in {abs_corpus_dir}")
        return
        
    # Write to collection.spec
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for filepath in txt_files:
            f.write(f"{filepath}\n")
            
    logger.info(f"Successfully wrote {len(txt_files)} file paths to '{OUTPUT_FILE}'")

if __name__ == "__main__":
    main()
