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

After any tracing tool returns line numbers, feed them to **`read-excerpts`** for full AST context. If a symbol name is returned, call **`read-symbols`** directly — never hunt by coordinates.

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
`find-callers` (transitive=true) → `get-call-graph` → `read-excerpts` on suspect lines → `analyze-control-flow`

**Find all implementations of a pattern:**
`search-chunks --chunk-type function` (concept query) → `read-excerpts` for deep context on matches

**Refactor blast-radius audit:**
`analyze-dependencies` → `find-usages` → `find-callers` → `get-exports` to verify API surface

**Debug a state mutation bug:**
`analyze-data-flow` → `analyze-control-flow` → `read-excerpts` on mutation sites
