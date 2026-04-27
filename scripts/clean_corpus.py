"""
clean_corpus.py — Cleans the raw tweets and generates the format required for PyTerrier.

This script reads phase1/tweets.jsonl, cleans the text, and:
1. Creates individual `<doc_id>.txt` files in the root `corpus/` directory.
2. Generates a new `phase1/tweets_clean.jsonl` file with the cleaned text.
"""

import json
import os
import re
from scripts.utils import get_logger, ensure_dir

logger = get_logger(__name__)

INPUT_FILE = "phase1/tweets.jsonl"
OUTPUT_CLEAN_JSONL = "phase1/tweets_clean.jsonl"
CORPUS_DIR = "corpus"

def clean_text(text: str) -> str:
    """
    Cleans tweet text by removing URLs, mentions, hashtags, newlines, 
    all punctuation, and extra spaces. Converts to lowercase.
    """
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove @mentions
    text = re.sub(r'@\w+', '', text)
    
    # Remove hashtags
    text = re.sub(r'#\w+', '', text)
    
    # Remove newlines and carriage returns
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    # Remove all punctuation (anything that is not a word character or whitespace)
    # \w matches [a-zA-Z0-9_]. If we want to keep only letters/numbers, we can use [^\w\s].
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Lowercase all text
    text = text.lower()
    
    # Remove extra spaces (squash multiple spaces into one)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def main():
    logger.info("Starting corpus cleaning process...")
    
    if not os.path.exists(INPUT_FILE):
        logger.error(f"Input file not found: {INPUT_FILE}")
        return
        
    ensure_dir(CORPUS_DIR)
    
    cleaned_tweets = []
    
    with open(INPUT_FILE, "r", encoding="utf-8") as infile:
        for line_num, line in enumerate(infile):
            if not line.strip():
                continue
                
            try:
                tweet = json.loads(line)
                
                # 1. Clean the text
                original_text = tweet.get("text", "")
                cleaned = clean_text(original_text)
                
                # 2. Save individual .txt file
                doc_id = tweet.get("doc_id", f"unknown_{line_num}")
                txt_path = os.path.join(CORPUS_DIR, f"{doc_id}.txt")
                
                with open(txt_path, "w", encoding="utf-8") as txt_file:
                    txt_file.write(cleaned)
                    
                # 3. Update the json object with cleaned text
                tweet["text"] = cleaned
                cleaned_tweets.append(tweet)
                
            except json.JSONDecodeError as e:
                logger.warning(f"Skipping invalid JSON on line {line_num}: {e}")
                
    # 4. Save the cleaned JSONL file
    with open(OUTPUT_CLEAN_JSONL, "w", encoding="utf-8") as outfile:
        for ct in cleaned_tweets:
            outfile.write(json.dumps(ct, ensure_ascii=False) + "\n")
            
    logger.info(f"Cleaning complete! Processed {len(cleaned_tweets)} tweets.")
    logger.info(f"Saved {len(cleaned_tweets)} .txt files to '{CORPUS_DIR}/'")
    logger.info(f"Saved cleaned JSONL to '{OUTPUT_CLEAN_JSONL}'")

if __name__ == "__main__":
    main()
