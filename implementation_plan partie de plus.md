# Phase 3 Bonus: Neural IR & Semantic Visualization (Machine Learning)

To secure maximum bonus points and wow your professor, I propose adding a new, highly visual **Machine Learning** component to the project. Traditional models like BM25 are "Lexical" (they look for exact word matches). We will introduce "Semantic Search" using Pre-trained Neural Networks to understand the *meaning* of the tweets about the Iran War.

## The Proposal: Dense Retrieval & t-SNE Visualization

We will create a new script (`phase3_bonus_ml.py`) that implements the following pipeline:

### 1. Pre-trained Machine Learning Model (Neural IR)
We will use a pre-trained HuggingFace Transformer model (`sentence-transformers/all-MiniLM-L6-v2`). This is a state-of-the-art Deep Learning model that converts text into dense 384-dimensional vectors (Embeddings). 

### 2. Semantic Search Evaluation
Instead of counting word frequencies (like BM25), the ML model calculates the **Cosine Similarity** between the Query vector and the Tweet vectors. We will evaluate the MAP score of this Neural model and compare it directly against your traditional BM25 model.

### 3. High-End Visual Analysis (t-SNE / PCA)
Humans cannot see 384 dimensions. We will use an unsupervised Machine Learning algorithm called **PCA / t-SNE** (via `scikit-learn`) to compress these vectors into 2D space. 
We will generate a stunning, professional scatter plot (`semantic_space.png`) that displays:
- The **Queries** plotted as large stars.
- The **Tweets** plotted as dots around them.
- Colored specifically by **Relevance** (e.g., Relevant tweets in Blue, Irrelevant in Red).
This visualization will physically show the jury *why* the machine learning model considers certain tweets relevant to the query based on distance!

## Required New Dependencies
This will require installing a few popular ML libraries:
- `sentence-transformers` (for the pre-trained model)
- `scikit-learn` (for t-SNE / PCA dimensionality reduction)
- `seaborn` (for beautiful aesthetic plotting)

## User Review Required

> [!IMPORTANT]  
> **Do you approve this proposal?** 
> This is a classic, highly valued bonus in Modern IR courses because it contrasts old-school statistical IR (Phase 2) with modern Deep Learning IR (Phase 3) and provides a gorgeous chart for your presentation. 
> 
> If you approve, I will automatically write the script, install the libraries, and generate the visualization for you!
