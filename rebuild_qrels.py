import json
import os
from scripts.build_qrels import build_qrels
from scripts.utils import load_config

settings = load_config('config/settings.yaml')
relevant_count = settings['collection']['relevant_count']
phase1_dir = settings['output']['phase1_dir']

tweets_file = os.path.join(phase1_dir, settings['output']['corpus_file'])
qrels_file = os.path.join(phase1_dir, settings['output']['qrels_file'])

tweets = []
with open(tweets_file, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            tweets.append(json.loads(line))

qrels = build_qrels(tweets, relevant_count)

with open(qrels_file, 'w', encoding='utf-8') as f:
    for q in qrels:
        f.write(f"{q['query_id']} 0 {q['doc_id']} {q['relevance']}\n")

print("Successfully rebuilt qrels.txt with relevant_count =", relevant_count)
