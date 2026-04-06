# SRI Project — 2ème ING IMD (2025-2026)

Information Retrieval System project using PyTerrier on a self-built tweet collection.
**Topic: Iran War**

## Team

Group xx — Class 2INLOG2

- Firas Chabbouh
- Ghaya Ammari
- Ines Cherif
- Rihab Gharbi
- Wassim Ouertani

---

## Phase 1 — Building the test collection

**Deadline: 18 April 2026**

### What it produces

| File                  | Description                                         |
| --------------------- | --------------------------------------------------- |
| `phase1/tweets.jsonl` | 500 tweets (100 per query)                          |
| `phase1/queries.txt`  | 5 queries in TREC format                            |
| `phase1/qrels.txt`    | Relevance judgments (first 30 per query = relevant) |

### Setup

**1. Clone the repo**

```bash
git clone https://github.com/inesCherif/IREval-Tweets.git
cd IREval-Tweets
```

**2. Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
playwright install chromium
```

**4. Set up your X (Twitter) session cookies**

Because X blocks standard login automation, we use session tokens from your active browser session to bypass the "infinite loading" bug:

1. Open [x.com](https://x.com/) in your browser and log in.
2. Press **F12** to open Developer Tools.
3. Go to the **Application** tab (Chrome/Edge) or **Storage** tab (Firefox).
4. On the left, expand **Cookies** and click on `https://x.com`.
5. Copy the values for `auth_token` and `ct0`.
6. Run: `cp .env.example .env` (or just create it manually).
7. Open `.env` and paste the tokens:
   ```env
   X_AUTH_TOKEN=your_auth_token_here
   X_CT0=your_ct0_here
   ```

**5. Run Phase 1**

```bash
python -m scripts.main
```

---

## Project structure

```
IREval-Tweets/
├── .env                ← YOUR credentials (never pushed)
├── .env.example        ← Template for teammates
├── config/
│   ├── queries.yaml    ← The 5 queries
│   └── settings.yaml   ← API and collection settings
├── phase1/             ← OUTPUT folder (deliverables)
├── scripts/
│   ├── main.py         ← Entry point
│   ├── fetch_tweets.py
│   ├── build_qrels.py
│   ├── save_corpus.py
│   └── utils.py
└── requirements.txt
```
