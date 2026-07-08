---
name: narsil-code-search
description: "Standard Operating Procedure for global search, semantic concept mapping, and cross-file dependencies."
---

# Code Discovery & Search SOP

Use this procedure when exploring an unfamiliar codebase, locating where a feature is implemented, or auditing cross-file symbol usage.

## 1. Choosing the Right Search Tool

| Query type | Tool | Example |
|---|---|---|
| Natural language / behavioural intent | **`search-semantic`** | `"deserialize JSON into user struct"` |
| Mixed keyword + concept | **`search-hybrid`** (default) | `"connection pool timeout retry"` |
| Exact string / token / attribute | **`search-keywords`** | `"#[derive(Serialize)]"` |
| Scoped to a structural type + need to read bodies | **`search-chunks`** with `chunk-type` | functions that handle auth — returns full code, not just locations |
| Duplication check before writing new code | **`find-similar-code`** | rough snippet of intended logic |
| Find parallel implementations of a symbol | **`find-similar-symbol`** | existing symbol name |

**Default to `search-hybrid`** when unsure. Use `search-semantic` when you know the behaviour but not the identifier. Use `search-keywords` only for exact literal matches.

## 2. Cross-File Symbol Navigation

Once a symbol is located via search, follow up with:
- **`find-references`** — exhaustive list of all call/usage sites (file + line, no result cap)
- **`search-chunks`** — ranked top-N with full code bodies; use `--file` to scope to files returned by `find-references`
- **`catalog-usages`** — same as find-references but includes import sites (use for migration impact)
- **`analyze-dependencies`** with `direction="both"` — full import graph for a file

## 3. Duplication Guard
Before writing any new helper or utility, call **`find-similar-code`** with a rough snippet of your intended logic. If a match exists, use `view-symbols` to retrieve it instead of duplicating.
