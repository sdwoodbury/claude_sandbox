#!/usr/bin/env python3
"""
Smoke-test every command exposed by narsil_client.py.

Usage:
    python test_client.py [--repo REPO_PATH]

The script calls narsil_client.py for each subcommand, checks that the
response is non-empty and does not start with "Error:", and prints a
pass/fail summary.

Requires: narsil-mcp running and its UDS socket present at /tmp/narsil_mcp.
"""

import argparse
import subprocess
import sys
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

SCRIPT = str(Path(__file__).parent / "narsil_client.py")

# A real symbol and file inside this repo so queries return results.
REPO        = "narsil-mcp"
SRC_FILE    = "src/main.rs"          # relative to repo root
SYMBOL      = "main"                 # a function that definitely exists
CALLEE_FN   = "main"
CALLER_FN   = "send_request"        # Python-side; use a Rust one for Rust callers
CTRL_FN     = "main"
DATA_FN     = "main"
SEARCH_Q    = "socket"
WORKSPACE_Q = "main"

# ── Helpers ───────────────────────────────────────────────────────────────────

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
SKIP = "\033[33mSKIP\033[0m"

results: list[tuple[str, str, str]] = []   # (command, status, detail)


def run(args: list[str], label: str | None = None) -> tuple[bool, str]:
    """Run narsil_client.py with *args*, return (ok, output)."""
    cmd = [sys.executable, SCRIPT] + args
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        out = (proc.stdout + proc.stderr).strip()
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, str(e)

    if not out:
        return False, "empty response"
    if out.startswith("Error:"):
        return False, out
    return True, out[:120]   # truncate for display


def check(label: str, args: list[str]) -> None:
    ok, detail = run(args)
    status = PASS if ok else FAIL
    results.append((label, status, detail))
    indicator = "✓" if ok else "✗"
    print(f"  {indicator} {label:<35}  {detail[:80]}")


# ── Test cases ────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="Smoke-test narsil_client.py")
    ap.add_argument("--repo", default=REPO, help="Repo path passed to commands")
    args = ap.parse_args()
    repo = args.repo

    print(f"\nNarsil client smoke-test  (repo={repo})\n{'─'*60}")

    # ── Symbol search and navigation ──────────────────────────────────────────
    print("\n[Symbol search & navigation]")
    check("symbol",
          ["symbol", repo, SYMBOL])
    check("symbol --context-lines",
          ["symbol", repo, SYMBOL, "--context-lines", "5"])
    check("excerpt",
          ["excerpt", repo, SRC_FILE, "1"])
    check("refs",
          ["refs", repo, SYMBOL])
    check("refs --exclude-tests",
          ["refs", repo, SYMBOL, "--exclude-tests"])
    check("find-symbols (all)",
          ["find-symbols", repo])
    check("find-symbols (functions)",
          ["find-symbols", repo, "--type", "function"])
    check("find-symbols --pattern",
          ["find-symbols", repo, "--pattern", "main"])
    check("find-symbols --file-pattern",
          ["find-symbols", repo, "--file-pattern", "*.rs"])
    check("deps (both)",
          ["deps", repo, SRC_FILE])
    check("deps (imports)",
          ["deps", repo, SRC_FILE, "--direction", "imports"])
    check("deps (imported_by)",
          ["deps", repo, SRC_FILE, "--direction", "imported_by"])
    check("workspace-search",
          ["workspace-search", WORKSPACE_Q])
    check("workspace-search --kind function",
          ["workspace-search", WORKSPACE_Q, "--kind", "function"])
    check("usages",
          ["usages", repo, SYMBOL])
    check("usages --no-imports",
          ["usages", repo, SYMBOL, "--no-imports"])
    check("exports",
          ["exports", repo, SRC_FILE])

    # ── Call graph analysis ───────────────────────────────────────────────────
    print("\n[Call graph analysis]")
    check("call-graph (repo-wide)",
          ["call-graph", repo])
    check("call-graph --function",
          ["call-graph", repo, CALLEE_FN, "--depth", "2"])
    check("call-graph --exclude-tests",
          ["call-graph", repo, "--exclude-tests"])
    check("callers",
          ["callers", repo, CALLER_FN])
    check("callers --transitive",
          ["callers", repo, CALLER_FN, "--transitive", "--max-depth", "2"])
    check("callees",
          ["callees", repo, CALLEE_FN])
    check("callees --transitive",
          ["callees", repo, CALLEE_FN, "--transitive", "--max-depth", "2"])
    check("call-path",
          ["call-path", repo, "main", "send_request"])

    # ── Flow analysis ─────────────────────────────────────────────────────────
    print("\n[Flow analysis]")
    check("control-flow",
          ["control-flow", repo, SRC_FILE, CTRL_FN])
    check("data-flow",
          ["data-flow", repo, SRC_FILE, DATA_FN])

    # ── AST-aware chunking ────────────────────────────────────────────────────
    print("\n[AST chunking]")
    check("chunks",
          ["chunks", repo, SRC_FILE])
    check("chunks --no-imports",
          ["chunks", repo, SRC_FILE, "--no-imports"])
    check("chunk-stats",
          ["chunk-stats", repo])
    check("embedding-stats",
          ["embedding-stats"])

    # ── Code search ───────────────────────────────────────────────────────────
    print("\n[Code search]")
    check("search",
          ["search", SEARCH_Q, "--repo", repo])
    check("search --file-pattern",
          ["search", SEARCH_Q, "--repo", repo, "--file-pattern", "*.rs"])
    check("search --max-results",
          ["search", SEARCH_Q, "--repo", repo, "--max-results", "5"])
    check("search --exclude-tests",
          ["search", SEARCH_Q, "--repo", repo, "--exclude-tests"])
    check("semantic",
          ["semantic", SEARCH_Q, "--repo", repo])
    check("semantic --doc-type function",
          ["semantic", SEARCH_Q, "--repo", repo, "--doc-type", "function"])
    check("hybrid",
          ["hybrid", SEARCH_Q, "--repo", repo])
    check("hybrid --mode bm25",
          ["hybrid", SEARCH_Q, "--repo", repo, "--mode", "bm25"])
    check("hybrid --mode tfidf",
          ["hybrid", SEARCH_Q, "--repo", repo, "--mode", "tfidf"])
    check("search-chunks",
          ["search-chunks", SEARCH_Q, "--repo", repo])
    check("search-chunks --chunk-type function",
          ["search-chunks", SEARCH_Q, "--repo", repo, "--chunk-type", "function"])
    check("similar-code",
          ["similar-code", "fn main()", "--repo", repo])
    check("similar-symbol",
          ["similar-symbol", repo, SYMBOL])

    # ── Repository management ─────────────────────────────────────────────────
    print("\n[Repository management]")
    check("structure",
          ["structure", repo])
    check("structure --max-depth 2",
          ["structure", repo, "--max-depth", "2"])

    # ── Summary ───────────────────────────────────────────────────────────────
    passed = sum(1 for _, s, _ in results if "PASS" in s)
    failed = sum(1 for _, s, _ in results if "FAIL" in s)
    total  = len(results)

    print(f"\n{'─'*60}")
    print(f"Results: {passed}/{total} passed", end="")
    if failed:
        print(f"  ({failed} FAILED)")
        failed_names = [label for label, s, _ in results if "FAIL" in s]
        print("Failed commands:")
        for name in failed_names:
            print(f"  - {name}")
    else:
        print("  — all green!")
    print()

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
