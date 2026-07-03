---
name: narsil_code_search
description: "Standard Operating Procedure for global search, semantic concept mapping, and cross-file dependencies."
---

# Code Discovery & Search SOP

Use these tools when exploring an unfamiliar codebase, looking for architectural patterns, or locating where a feature concept is implemented. 

## 1. Intent-Based Searching (Semantic Over Keyword)
* **Natural Language Queries:** If you are looking for a conceptual feature but don't know the exact variable or function names, use `search_semantic`. Use query descriptions like `"handling WebRTC connection fallback"` or `"parsing protocol frames"`.
* **Code Intent Matching:** Use `search_chunks` to search directly over logical AST-aware boundaries. This ensures results match the functional context of structural components.
* **The Hybrid Fallback:** For general queries where you want a balance of exact string tokens and concept matching, default to `search_hybrid`.

## 2. Impact Analysis & Workspace Context
Before modifying an existing file or module, you must analyze its immediate Blast Radius:
* **Inbound/Outbound Deps:** Use `analyze_dependencies` with `direction="both"` to see what a file relies on and what files rely on it.
* **Public Interface Check:** Use `get_exports` on a target file to instantly audit its public API surface before making changes.
* **Duplication Guard:** If you are about to write a new helper function or utility, use `find_similar_code` with a rough snippet of your intent. Check if a clean abstraction already exists in the repo to prevent codebase fragmentation.
