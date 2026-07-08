---
name: search-keywords
description: "Exact keyword/token search with relevance ranking across the codebase."
---

Performs an exact text/keyword search across indexed source files, returning results ranked by relevance.

## Tool Interface
```
/bin/narsil_client.py search-keywords <query: str> \
    [--file-pattern <glob: str>] \
    [--max-results <n: int = 10>] \
    [--exclude-tests]
```

## Usage
Use for exact string matches (error codes, string literals, attribute names). For natural language or conceptual queries, prefer `search-semantic` or `search-hybrid`.
