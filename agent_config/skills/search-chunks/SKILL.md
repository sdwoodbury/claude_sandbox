---
name: search-chunks
description: "Search strictly over AST-aware code chunks by type (function, method, class, etc.)."
---

Searches directly over AST chunk boundaries, restricting results to a specific structural type. Results are syntactically whole units, never partial lines.

## Tool Interface
```
/bin/narsil_client.py search-chunks <query: str> \
    [--chunk-type <function|method|class|trait|module|all = "all">] \
    [--max-results <n: int = 10>] \
    [--file <path>] ...   (repeat to filter to multiple files)
    [--exclude-tests]
```

## Usage
Use when you want results scoped to a specific structural unit type (e.g., only functions, only traits). Results are complete AST blocks with full body text — not just file/line pointers.

**Prefer over `find-references`** when you need to *read* each matching site, not just locate it. `find-references` returns file + line; `search-chunks` returns file + line + the full code body of each matching chunk. Ideal for "find all functions that handle X and show me their implementation."

**Use `--file` to scope to specific files** — pair with `find-references` to get exhaustive locations first, then pass the files you care about to `search-chunks` to retrieve the code bodies at those sites.
