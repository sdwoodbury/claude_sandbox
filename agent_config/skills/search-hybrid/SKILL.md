---
name: search-hybrid
description: "Combined BM25 + TF-IDF search with rank fusion — the default general-purpose search."
---

Runs both BM25 and TF-IDF search and fuses the ranked results. Balances exact token matching with conceptual similarity.

## Tool Interface
```
/bin/narsil_client.py hybrid <query: str> \
    [--mode <hybrid|bm25|tfidf = "hybrid">] \
    [--max-results <n: int = 10>] \
    [--exclude-tests]
```

## Usage
Default choice for general queries. Use `search-semantic` for pure natural-language intent queries; use `search-keywords` for exact literal matches.
