---
name: search-semantic
description: "BM25-ranked semantic search for natural language queries about what code does."
---

BM25-ranked semantic search. Best for natural language queries describing behaviour rather than exact symbol names.

## Tool Interface
```
/bin/narsil_client.py search-semantic <query: str> \
    [--doc-type <file|function|class|struct|method = "function">] \
    [--max-results <n: int = 5>] \
    [--exclude-tests]
```

## Usage
Use when you know **what** you're looking for conceptually but not the identifier name. For mixed keyword+concept queries, use `search-hybrid` instead.
