
**ALWAYS** exclude `/vendor`, `/target`, and `/build` from searches.

**NEVER** run `cargo` commands (`check`, `test`, etc) unless specifically told to.

**ALWAYS** search for Rust dependencies (which were not found in the current cargo workspace / project) in /root/.cargo/. That is where your cargo cache is. 

# Guiding Principles
Think Before Coding    → stops wrong assumptions and missed tradeoffs
Simplicity First       → stops over-engineering and bloated abstractions
Surgical Changes       → stops touching code nobody asked to touch
Goal-Driven Execution  → tests first, verified success criteria

# RULES
**NEVER** spawn a sub-agent to call a tool that is directly available to the main agent. patch_file, Read, Edit, Write, Glob — call these directly. Sub-agents are onlY for multi-step research tasks.
- **NEVER** use the Edit tool. Use patch_file exclusively.
- **File Edits:** You have access to the `patch-file` skill. **NEVER** output raw code blocks to the user when modifying files. You MUST use the `/bin/patch_file.py` tool to apply all code changes directly to the filesystem. **NEVER** write a script to edit the files. **ALWAYS** use `/bin/patch_file.py` to edit a file.


# The patch-file skill is shown below

---
name: patch-file
description: "Apply surgical SEARCH/REPLACE block patches to a file. This is the ONLY approved method for editing source code."
---

Applies precise text replacements to a target file using a strict block format. Ensures edits are safe by verifying the search string is 100% unique within the target file before modifying it.

## Tool Interface
```bash
cat << 'EOF' | /bin/patch_file.py <file_path: str> -a <allowed_dir: str>
<<<<<<< SEARCH
<first_exact_text_to_find>
=======
<first_exact_text_to_replace_it_with>
>>>>>>> REPLACE
<<<<<<< SEARCH
<second_exact_text_to_find>
=======
<second_exact_text_to_replace_it_with>
>>>>>>> REPLACE
EOF
```

# SKILLS
- You have the following skills. use them as described. skills: [narsil-file-inspection, view-repository-structure, scan-file-skeletons, view-symbols, find-symbols-by-pattern, catalog-usages, find-references, get-exports, narsil-code-understanding, get-chunks-by-lines, analyze-dependencies, get-call-graph, find-callers, find-callees, get-call-path, analyze-control-flow, analyze-data-flow, narsil-code-search, workspace-search, search-keywords, search-semantic, search-hybrid, search-chunks, find-similar-code, find-similar-symbol, get-chunk-stats, get-embedding-stats, batch-commands]
- All the above skills are concatenated together in the "SKILL Definitions" section. This is because you were too lazy to actually read them. But they are skills nonetheless. Use them accordingly.
- **NEVER** concatenate multiple `Bash` invocations of `/bin/narsil_client.py` (whether via ';' or '&&'). If you need to run more than one exploration or search task, you must use the `batch-commands` skill to execute them all at once.
- **NEVER** READ THE `.narsil` directory. Stop being lazy. Do your damn job.

## FORBIDDEN ACTIONS
- **NO RAW BASH SEARCHING/READING:** You are **FORBIDDEN** from using `cat`, `grep`, `rg`, `sed`, `head`, `tail`, or launching ad-hoc python scripts inside the terminal to read code.
- **NO COORDINATE CHASING:** Never search for arbitrary line numbers or character slices. Rely entirely on AST-aware tools (`search-keywords`, `view-symbols`, `get-chunks-by-lines`) to fetch syntactically whole blocks.

# SKILL Definitions

---
name: find-callees
description: "Find all functions called BY the specified function, with optional transitive traversal."
---

Returns the set of functions that `function_name` calls directly (or transitively). Use to trace downstream execution paths.

## Tool Interface
```
/bin/narsil_client.py find-callees <function_name: str> \
    [--max-depth <n: int = 1>] \
    [--transitive] \
    [--exclude-tests]
```

## Usage
Use at `max_depth=1` to see immediate dependencies. Use `--transitive` to map the full downstream blast radius before a refactor.

---
name: find-callers
description: "Find all functions that call the specified function, with optional transitive traversal."
---

Finds the set of functions that directly (or transitively) call `function_name`. Use to trace upstream execution paths.

## Tool Interface
```
/bin/narsil_client.py find-callers <function_name: str> \
    [--max-depth <n: int = 1>] \
    [--transitive] \
    [--exclude-tests]
```

## Usage
Use with `max_depth=1` first for direct callers. Increase depth or use `--transitive` only when tracing a panic or cascading failure upstream.

---
name: find-references
description: "Find all references to a named symbol across the codebase."
---

Locates every site in the repository where `symbol_name` is referenced (call sites, type annotations, macro invocations, etc.).

## Tool Interface
```
/bin/narsil_client.py find-references <symbol_name: str> \
    [--include-definition | --no-include-definition] \
    [--exclude-tests | --include-tests]
```

## Usage
Use returned line numbers as inputs to `get-chunks-by-lines` for full context around each reference site.

If you need the body of each reference site — not just its location — use **`search-chunks`** instead. It returns the same file/line info plus the full enclosing code block for each match.

---
name: get-chunks-by-lines
description: "Retrieve the full AST chunk(s) that contain given line numbers from a file."
---

For each `--line` arg, returns the complete AST chunk (function body, struct block, impl block, etc.) that contains that line. Safe — never reads partial syntactic units.

## Tool Interface
```
/bin/narsil_client.py get-chunks-by-lines \
    --file  <file_path: str> \
    --line <line1: int> [--line <line2: int> ...]
```

## Usage
Feed line numbers from `scan-file-skeletons` or `find-references` output here. Never guess line numbers — always derive them from a prior tool call.

---
name: analyze-data-flow
description: "Trace variable definitions, mutations, and consumption sites within a function."
---

Returns intra-function data-flow information: where each variable is defined, mutated, and consumed. Use to eliminate state-override bugs and ownership ambiguities.

## Tool Interface
```
/bin/narsil_client.py analyze-data-flow <path: str> <function_name: str>
```

## Usage
Use when tracking a value mutation chain or ownership transfer through a non-trivial function. Pair with `analyze-control-flow` for full intra-function diagnostics.

---
name: find-similar-symbol
description: "Find code chunks similar to a named symbol — locate parallel implementations."
---

Given a known symbol name, returns other codebase chunks that are semantically similar to its implementation.

## Tool Interface
```
/bin/narsil_client.py find-similar-symbol <symbol_name: str> \
    [--max-results <n: int = 5>]
```

## Usage
Use when refactoring a symbol to check if parallel implementations exist that must be updated in tandem.

---
name: find-similar-code
description: "Find existing codebase logic similar to a raw code snippet — duplication guard."
---

Given a raw code snippet, returns existing codebase chunks that are semantically similar. Use to check for pre-existing abstractions before writing new ones.

## Tool Interface
```
/bin/narsil_client.py find-similar-code <code_snippet: str> \
    [--max-results <n: int = 5>] \
    [--exclude-tests]
```

## Usage
Call this before implementing any new helper, utility, or transformation function to avoid duplicating existing logic.

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

---
name: narsil-file-inspection
description: "Standard Operating Procedure for localized token-efficient file scanning, AST chunk reading, and exact symbol extraction."
---

# File Inspection & Symbol Extraction SOP

Use this procedure whenever you need to open a file, read source logic, or inspect the exact definition of a known symbol (struct, enum, function, trait, etc.).

## Two-Phase Local Inspection Workflow

### Phase A: Structural Layout Mapping
Never pull an entire raw file body into context. Always map boundaries first:

1. Call **`scan-file-skeletons`** on the target file path.
   Returns a lightweight AST outline (symbol names + line ranges) without pulling body text.
2. Review the skeleton. Note the line numbers of targets you need.

### Phase B: Precision AST Extraction
Choose one path based on what you know:

| Situation | Tool | Why |
|---|---|---|
| You know the exact symbol name | **`view-symbols`** | Fetches the complete block with no line hunting |
| You have a line number from a prior tool | **`get-chunks-by-lines`** | Returns the full enclosing AST chunk for that line |
| You only have a partial name / fuzzy concept | **`find-symbols-by-pattern`** → then `view-symbols` | Resolves the exact identifier first |

### Ambiguous Name Resolution
If the exact identifier is unknown:
1. Call **`find-symbols-by-pattern`** with `--pattern "*Partial*"` and the appropriate `--type` filter (`"struct"`, `"function"`, `"all"`, etc.).
2. Once the exact name is returned, call **`view-symbols`** — never guess coordinates.


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

---
name: scan-file-skeletons
description: "Map one or more files' AST structure before any targeted reads. Use this FIRST when opening new files."
---

Returns a lightweight outline of one or more files broken down by AST logic (structs, fns, impls, modules, etc.) without pulling full bodies into context.

## Tool Interface
```
/bin/narsil_client.py scan-file-skeletons --file <file_path: str> [--file <file_path: str> ...]
```

The `--file` flag is repeatable — pass it multiple times to skeleton several files in a single call.

## Usage
Always call this before `get-chunks-by-lines` or `view-symbols` on unfamiliar files. Use the returned skeleton line numbers as inputs to subsequent targeted reads. When opening several related files at once, pass them all in one call to reduce round-trips.

---
name: find-symbols-by-pattern
description: "Find structs, classes, functions, traits, etc. by fuzzy name pattern and/or type filter."
---

Searches all indexed symbols by fuzzy name pattern and optional type filter. Returns matching symbol names, types, and file locations.

## Tool Interface
```
/bin/narsil_client.py find-symbols-by-pattern \
    [--pattern <pattern: str = "*">] \
    [--type    <struct|class|enum|interface|function|method|trait|type|all = "all">] \
    [--file-pattern <glob: str>] \
    [--exclude-tests | --include-tests]
```

## Usage
Use when you know a partial name or concept but not the exact identifier. Output includes the definition file, line number, **and the definition text itself** — so it can answer "where is X defined and what does it look like" in a single call. Once the exact name is resolved, call `view-symbols` to fetch the complete body if needed.

---
name: view-repository-structure
description: "Return a directory tree of the workspace to orient before searching."
---

Returns a visual directory tree of the workspace up to `max_depth` levels. Use to understand project architecture and module boundaries before searching.

## Tool Interface
```
/bin/narsil_client.py view-repository-structure [--max-depth <n: int = 3>]
```

## Usage
Run with `max_depth=2` or `3` first to get a clean overview without dumping leaf files. Increase depth only to inspect a specific subtree. Always run this when onboarding onto an unfamiliar crate or repository.

---
name: get-call-path
description: "Find the execution path between two distinct functions."
---

Returns the shortest call chain linking `from_function` to `to_function` across the codebase.

## Tool Interface
```
/bin/narsil_client.py get-call-path <from_fn: str> <to_fn: str>
```

## Usage
Use when you need to trace execution flow from a known entrypoint to a target function — e.g. "how does `main` eventually reach `flush_buffer`?" Returns the shortest call chain linking the two. Also useful for verifying that two separate modules are connected and understanding the middleware between them. Both functions must be indexed symbols.

---
name: catalog-usages
description: "Find cross-file symbol usages, optionally including import sites."
---

Locates all cross-file usages of a symbol, including import statements unless suppressed.

## Tool Interface
```
/bin/narsil_client.py catalog-usages <symbol_name: str> \
    [--no-imports] \
    [--exclude-tests]
```

## Difference from find-references
`catalog-usages` includes import sites by default; `find-references` focuses on call/usage sites. Use `catalog-usages` for migration impact analysis, `find-references` for call-site audits.

---
name: view-symbols
description: "Fetch the complete source code of one or more symbols by name — no line numbers needed."
---

Returns the complete, exact source code of one or more named symbols (function, struct, enum, trait, const, etc.) looked up by names across the repository.

## Tool Interface
```
/bin/narsil_client.py view-symbols <symbol_name: str> [<symbol_name: str> ...] \
    [--context-lines <n: int = 0>]
```

## Usage
Pass one or more symbol names as positional arguments. Results are concatenated with a `# Symbol  <name>` header between each. If you know the symbol name(s), call this directly — do not hunt via `scan-file-skeletons` first. Use `find-symbols-by-pattern` only when the exact name is unknown.

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

---
name: get-call-graph
description: "Generate a multi-level call graph rooted at a function."
---

Generates the full call graph for a function up to `depth` levels, showing the complete execution tree of callees.

## Tool Interface
```
/bin/narsil_client.py get-call-graph <function_name: str> \
    [--depth <n: int = 2>] \
    [--exclude-tests]
```

## Usage
Use to capture the full pipeline view of a complex function before refactoring. Prefer `find-callers`/`find-callees` for targeted upstream/downstream hops.

---
name: workspace-search
description: "Fuzzy-search for symbols by name across the entire workspace."
---

Performs a fuzzy name search across all workspace symbols, returning matches with their type and location.

## Tool Interface
```
/bin/narsil_client.py workspace-search <fuzzy_name: str> \
    [--kind  <function|class|struct|interface|enum|variable|all = "all">] \
    [--limit <n: int = 10>]
```

## Usage
Use when you have a rough idea of a symbol name but don't know the exact casing, module, or file. Follow up with `view-symbols` once the exact name is identified.

---
name: search-hybrid
description: "Combined BM25 + TF-IDF search with rank fusion — the default general-purpose search."
---

Runs both BM25 and TF-IDF search and fuses the ranked results. Balances exact token matching with conceptual similarity.

## Tool Interface
```
/bin/narsil_client.py search-hybrid <query: str> \
    [--mode <hybrid|bm25|tfidf = "hybrid">] \
    [--max-results <n: int = 10>] \
    [--exclude-tests]
```

## Usage
Default choice for general queries. Use `search-semantic` for pure natural-language intent queries; use `search-keywords` for exact literal matches.

---
name: narsil-code-understanding
description: "Standard Operating Procedure for structural flow tracking, AST graph visualization, intra-function mutation tracing, and workspace architectural comprehension."
---

# Code Understanding & Flow Analysis SOP

Use this procedure when onboarding onto unfamiliar crates, debugging panics, tracing multi-hop execution, or verifying state mutations.

## Phase A: Macro Architecture — Orient Before You Dig

| Goal | Tool | Notes |
|---|---|---|
| Understand module/crate layout | **`view-repository-structure`** | Start at `max_depth=2`, increase only to inspect a subtree |
| Audit a module's public surface | **`get-exports`** | Run before proposing interface changes |
| Map a file's import/dependent graph | **`analyze-dependencies`** `direction="both"` | Establishes blast radius before any refactor |

## Phase B: Execution Tracing — Follow the Call Chain

| Goal | Tool | Notes |
|---|---|---|
| Who triggers this function? | **`find-callers`** | Start at `max_depth=1`; go deeper only as needed |
| What does this function call? | **`find-callees`** | Same depth discipline |
| Full multi-level pipeline view | **`get-call-graph`** | Use for complex entry points; default `depth=2` |
| Path between two distant functions | **`get-call-path`** | Both must be indexed symbols |

After any tracing tool returns line numbers, feed them to **`get-chunks-by-lines`** for full AST context. If a symbol name is returned, call **`view-symbols`** directly — never hunt by coordinates.

## Phase C: Micro-Analysis — Intra-Function Diagnostics

| Goal | Tool | When to Use |
|---|---|---|
| Map conditional branches / loops | **`analyze-control-flow`** | Dense match blocks, unhandled variants |
| Trace variable definition → mutation → consumption | **`analyze-data-flow`** | State-override bugs, ownership ambiguities |

Use both together for full intra-function diagnostics on a complex or suspect function.

## Tool Composition Recipes

**Onboarding an unfamiliar crate:**
`view-repository-structure` → `get-exports` (key files) → `analyze-dependencies` → `search-hybrid` for entry points → `search-chunks --chunk-type function` to read key handler bodies

**Tracing a panic upstream:**
`find-callers` (transitive=true) → `get-call-graph` → `get-chunks-by-lines` on suspect lines → `analyze-control-flow`

**Find all implementations of a pattern:**
`search-chunks --chunk-type function` (concept query) → `get-chunks-by-lines` for deep context on matches

**Refactor blast-radius audit:**
`analyze-dependencies` → `catalog-usages` → `find-callers` → `get-exports` to verify API surface

**Debug a state mutation bug:**
`analyze-data-flow` → `analyze-control-flow` → `get-chunks-by-lines` on mutation sites

---
name: batch-commands
description: "Execute multiple calls to /bin/narsil_client.py sequentially in a single terminal execution loop."
---

Combines multiple repository exploration and search tasks into a single run to drastically reduce agent tool-call latency and roundtrips.

## Tool Interface
```bash
cat << 'EOF' | /bin/narsil_client.py batch-commands
<command_1> [--args...]
<command_2> [--args...]
EOF
```

## Usage Guidelines
* **Omit the Binary Prefix:** Inside the `cat` block, do not include the `/bin/narsil_client.py` prefix. Write only the subcommand name (e.g., `view-symbols`, `find-references`, `get-chunks-by-lines`) and its flags.
* **Argument Quoting:** Use standard double quotes (`"string thing"`) for arguments that contain spaces or special characters.
* **Comments & Whitespace:** You can add blank lines or use lines starting with `#` to logically organize your batch block; they will be ignored by the parser.

## Example
```bash
cat << 'EOF' | /bin/narsil_client.py batch-commands
view-symbols --name "Schedule" --file "search.rs"
find-references --name "HAWK_MIN_DIST_ROTATIONS"
get-chunks-by-lines --file "intra_batch.rs" --line 42
EOF
```

---
name: get-chunk-stats
description: "Return AST chunk statistics for the entire repository index."
---

Returns aggregate statistics about AST code chunks across the full repository (chunk counts by type, size distributions, etc.).

## Tool Interface
```
/bin/narsil_client.py get-chunk-stats
```

---
name: get-exports
description: "List all exported symbols from a specific file or module."
---

Returns the public API surface of a file or module: all exported functions, types, constants, and traits.

## Tool Interface
```
/bin/narsil_client.py get-exports <path: str>
```

## Usage
Run this before proposing changes to a module's public interface to understand what external consumers depend on.

---
name: analyze-control-flow
description: "Map basic blocks, conditional branches, and loops inside a function."
---

Produces a structural control-flow graph for a function: basic blocks, conditional branches (if/match arms), and loop cycles. Use to isolate dead branches or unhandled match variants.

## Tool Interface
```
/bin/narsil_client.py analyze-control-flow <path: str> <function_name: str>
```

## Usage
Use when a bug is localized to a single dense conditional or match block. Do not guess branch evaluations — read the graph output directly.

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

---
name: analyze-dependencies
description: "Analyze imports and dependents for a specific file — who it imports and who imports it."
---

Returns the import graph for a given file path: what it imports (`imports`), what imports it (`imported_by`), or both.

## Tool Interface
```
/bin/narsil_client.py analyze-dependencies <path: str> \
    [--direction <imports|imported_by|both = "both">]
```

## Usage
Run with `--direction "both"` before proposing any refactor to establish the full blast radius of consumers and dependencies.

---
name: get-embedding-stats
description: "Return statistics about the current embedding/search index."
---

Returns statistics about the current embedding index (document counts, index size, model info, etc.).

## Tool Interface
```
/bin/narsil_client.py get-embedding-stats
```
