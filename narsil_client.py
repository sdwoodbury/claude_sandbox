#!/usr/bin/env python3
import sys
import json
import socket
import argparse
import os

sys.stdout.reconfigure(encoding="utf-8")
SOCKET_PATH = "/tmp/narsil_mcp"

def send_request(tool_name, params):
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(SOCKET_PATH)
        f = sock.makefile("rwb")

        _id = 0

        def rpc(method, rpc_params):
            nonlocal _id
            _id += 1
            msg = json.dumps({"jsonrpc": "2.0", "id": _id, "method": method, "params": rpc_params}) + "\n"
            f.write(msg.encode())
            f.flush()
            return json.loads(f.readline())

        rpc("initialize", {
            "protocolVersion": "2024-11-05",
            "clientInfo": {"name": "narsil_client", "version": "0.1"},
            "capabilities": {}
        })
        f.write(b'{"jsonrpc":"2.0","method":"initialized","params":{}}\n')
        f.flush()

        resp = rpc("tools/call", {"name": tool_name, "arguments": params})

        f.close()
        sock.close()

        if "error" in resp:
            return f"Error: {resp['error']}"

        content = resp.get("result", {}).get("content", [])
        if content:
            return content[0].get("text", "")
        return "No content returned."

    except FileNotFoundError:
        return f"Error: Socket {SOCKET_PATH} not found. Is narsil-mcp running?"
    except Exception as e:
        return f"Communication error: {e}"

def main():
    parser = argparse.ArgumentParser(description="Narsil CLI Client")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Shared --repo flag: defaults to the current directory name
    repo_parent = argparse.ArgumentParser(add_help=False)
    repo_parent.add_argument("--repo", default=os.path.basename(os.getcwd()),
                             help="Repository name (default: current directory name)")

    # ── Symbol search and navigation ──────────────────────────────────────────

    p_sym = subparsers.add_parser("symbol", help="Get symbol source with surrounding context", parents=[repo_parent])
    p_sym.add_argument("symbol")
    p_sym.add_argument("--context-lines", type=int, default=0)

    p_exc = subparsers.add_parser("excerpt", help="Read a line, auto-expanded to its full scope", parents=[repo_parent])
    p_exc.add_argument("path")
    p_exc.add_argument("lines", type=int, nargs="+", help="One or more line numbers to extract around")
    
    p_ref = subparsers.add_parser("refs", help="Find all references to a symbol", parents=[repo_parent])
    p_ref.add_argument("symbol")
    p_ref.add_argument("--include-definition", action="store_true", default=True)
    p_ref.add_argument("--exclude-tests", action="store_true", default=False)

    p_fsym = subparsers.add_parser("find-symbols", help="Find structs, classes, functions by type/pattern", parents=[repo_parent])
    p_fsym.add_argument("--type", dest="symbol_type", default="all",
                        choices=["struct", "class", "enum", "interface", "function", "method", "trait", "type", "all"])
    p_fsym.add_argument("--pattern", default=None)
    p_fsym.add_argument("--file-pattern", default=None)
    p_fsym.add_argument("--exclude-tests", action="store_true", default=False)

    p_dep = subparsers.add_parser("deps", help="Analyze imports and dependents", parents=[repo_parent])
    p_dep.add_argument("path")
    p_dep.add_argument("--direction", default="both", choices=["imports", "imported_by", "both"])

    p_wss = subparsers.add_parser("workspace-search", help="Fuzzy search symbols across workspace")
    p_wss.add_argument("query")
    p_wss.add_argument("--kind", default="all",
                       choices=["function", "class", "struct", "interface", "enum", "variable", "all"])
    p_wss.add_argument("--limit", type=int, default=20)

    p_usg = subparsers.add_parser("usages", help="Cross-file symbol usage with imports", parents=[repo_parent])
    p_usg.add_argument("symbol")
    p_usg.add_argument("--no-imports", action="store_true", default=False)
    p_usg.add_argument("--exclude-tests", action="store_true", default=False)

    p_exp = subparsers.add_parser("exports", help="Get exported symbols from a file/module", parents=[repo_parent])
    p_exp.add_argument("path")

    # ── Call graph analysis ───────────────────────────────────────────────────

    p_cg = subparsers.add_parser("call-graph", help="Get call graph for repository/function", parents=[repo_parent])
    p_cg.add_argument("function", nargs="?", default=None)
    p_cg.add_argument("--depth", type=int, default=3)
    p_cg.add_argument("--exclude-tests", action="store_true", default=False)

    p_callers = subparsers.add_parser("callers", help="Find functions that call a function", parents=[repo_parent])
    p_callers.add_argument("function")
    p_callers.add_argument("--transitive", action="store_true", default=False)
    p_callers.add_argument("--max-depth", type=int, default=5)
    p_callers.add_argument("--exclude-tests", action="store_true", default=False)

    p_callees = subparsers.add_parser("callees", help="Find functions called by a function", parents=[repo_parent])
    p_callees.add_argument("function")
    p_callees.add_argument("--transitive", action="store_true", default=False)
    p_callees.add_argument("--max-depth", type=int, default=5)
    p_callees.add_argument("--exclude-tests", action="store_true", default=False)

    p_cp = subparsers.add_parser("call-path", help="Find path between two functions", parents=[repo_parent])
    p_cp.add_argument("from_fn", metavar="from")
    p_cp.add_argument("to_fn", metavar="to")

    # ── Flow analysis ─────────────────────────────────────────────────────────

    p_cf = subparsers.add_parser("control-flow", help="Analyze basic blocks, branches, loops", parents=[repo_parent])
    p_cf.add_argument("path")
    p_cf.add_argument("function")

    p_df = subparsers.add_parser("data-flow", help="Trace variable definitions and uses", parents=[repo_parent])
    p_df.add_argument("path")
    p_df.add_argument("function")

    # ── AST-aware chunking ────────────────────────────────────────────────────

    p_chunks = subparsers.add_parser("chunks", help="Get AST-aware chunks for a file", parents=[repo_parent])
    p_chunks.add_argument("path")
    p_chunks.add_argument("--no-imports", action="store_true", default=False)

    p_cstats = subparsers.add_parser("chunk-stats", help="Statistics about code chunks", parents=[repo_parent])

    subparsers.add_parser("embedding-stats", help="Embedding index statistics")

    # ── Code search ───────────────────────────────────────────────────────────

    p_sc = subparsers.add_parser("search", help="Keyword search with relevance ranking", parents=[repo_parent])
    p_sc.add_argument("query")
    p_sc.add_argument("--file-pattern", default=None)
    p_sc.add_argument("--max-results", type=int, default=10)
    p_sc.add_argument("--exclude-tests", action="store_true", default=False)

    p_sem = subparsers.add_parser("semantic", help="BM25-ranked semantic search", parents=[repo_parent])
    p_sem.add_argument("query")
    p_sem.add_argument("--doc-type", default=None,
                       choices=["file", "function", "class", "struct", "method"])
    p_sem.add_argument("--max-results", type=int, default=10)
    p_sem.add_argument("--exclude-tests", action="store_true", default=False)

    p_hyb = subparsers.add_parser("hybrid", help="Combined BM25 + TF-IDF search with rank fusion", parents=[repo_parent])
    p_hyb.add_argument("query")
    p_hyb.add_argument("--max-results", type=int, default=10)
    p_hyb.add_argument("--mode", default="hybrid", choices=["hybrid", "bm25", "tfidf"])
    p_hyb.add_argument("--exclude-tests", action="store_true", default=False)

    p_sch = subparsers.add_parser("search-chunks", help="Search over AST-aware code chunks", parents=[repo_parent])
    p_sch.add_argument("query")
    p_sch.add_argument("--chunk-type", default=None,
                       choices=["function", "method", "class", "trait", "module", "all"])
    p_sch.add_argument("--max-results", type=int, default=10)
    p_sch.add_argument("--exclude-tests", action="store_true", default=False)

    p_fsc = subparsers.add_parser("similar-code", help="Find code similar to a snippet (TF-IDF)", parents=[repo_parent])
    p_fsc.add_argument("query")
    p_fsc.add_argument("--max-results", type=int, default=10)
    p_fsc.add_argument("--exclude-tests", action="store_true", default=False)

    p_fss = subparsers.add_parser("similar-symbol", help="Find code similar to a symbol", parents=[repo_parent])
    p_fss.add_argument("symbol")
    p_fss.add_argument("--max-results", type=int, default=10)

    # ── Repository management ─────────────────────────────────────────────────

    p_ps = subparsers.add_parser("structure", help="Get directory tree with file icons and sizes", parents=[repo_parent])
    p_ps.add_argument("--max-depth", type=int, default=4)

    # ─────────────────────────────────────────────────────────────────────────

    args = parser.parse_args()

    if args.command == "symbol":
        res = send_request("get_symbol_definition", {
            "repo": args.repo, "symbol": args.symbol, "context_lines": args.context_lines,
        })
    elif args.command == "excerpt":
        lines = []
        for x in args.lines:
            lines.append(x)
        res = send_request("get_excerpt", {
            "repo": args.repo, "path": args.path, "lines": lines, "expand_to_scope": True,
        })
    elif args.command == "refs":
        res = send_request("find_references", {
            "repo": args.repo, "symbol": args.symbol,
            "include_definition": args.include_definition,
            "exclude_tests": args.exclude_tests,
        })
    elif args.command == "find-symbols":
        params = {"repo": args.repo, "symbol_type": args.symbol_type, "exclude_tests": args.exclude_tests}
        if args.pattern: params["pattern"] = args.pattern
        if args.file_pattern: params["file_pattern"] = args.file_pattern
        res = send_request("find_symbols", params)
    elif args.command == "deps":
        res = send_request("get_dependencies", {
            "repo": args.repo, "path": args.path, "direction": args.direction,
        })
    elif args.command == "workspace-search":
        res = send_request("workspace_symbol_search", {
            "query": args.query, "kind": args.kind, "limit": args.limit,
        })
    elif args.command == "usages":
        res = send_request("find_symbol_usages", {
            "repo": args.repo, "symbol": args.symbol,
            "include_imports": not args.no_imports,
            "exclude_tests": args.exclude_tests,
        })
    elif args.command == "exports":
        res = send_request("get_export_map", {"repo": args.repo, "path": args.path})
    elif args.command == "call-graph":
        params = {"repo": args.repo, "depth": args.depth, "exclude_tests": args.exclude_tests}
        if args.function: params["function"] = args.function
        res = send_request("get_call_graph", params)
    elif args.command == "callers":
        res = send_request("get_callers", {
            "repo": args.repo, "function": args.function,
            "transitive": args.transitive, "max_depth": args.max_depth,
            "exclude_tests": args.exclude_tests,
        })
    elif args.command == "callees":
        res = send_request("get_callees", {
            "repo": args.repo, "function": args.function,
            "transitive": args.transitive, "max_depth": args.max_depth,
            "exclude_tests": args.exclude_tests,
        })
    elif args.command == "call-path":
        res = send_request("find_call_path", {
            "repo": args.repo, "from": args.from_fn, "to": args.to_fn,
        })
    elif args.command == "control-flow":
        res = send_request("get_control_flow", {
            "repo": args.repo, "path": args.path, "function": args.function,
        })
    elif args.command == "data-flow":
        res = send_request("get_data_flow", {
            "repo": args.repo, "path": args.path, "function": args.function,
        })
    elif args.command == "chunks":
        res = send_request("get_chunks", {
            "repo": args.repo, "path": args.path, "include_imports": not args.no_imports,
        })
    elif args.command == "chunk-stats":
        res = send_request("get_chunk_stats", {"repo": args.repo})
    elif args.command == "embedding-stats":
        res = send_request("get_embedding_stats", {})
    elif args.command == "search":
        params = {"query": args.query, "max_results": args.max_results, "exclude_tests": args.exclude_tests,
                  "repo": args.repo}
        if args.file_pattern: params["file_pattern"] = args.file_pattern
        res = send_request("search_code", params)
    elif args.command == "semantic":
        params = {"query": args.query, "max_results": args.max_results, "exclude_tests": args.exclude_tests,
                  "repo": args.repo}
        if args.doc_type: params["doc_type"] = args.doc_type
        res = send_request("semantic_search", params)
    elif args.command == "hybrid":
        params = {"query": args.query, "max_results": args.max_results,
                  "mode": args.mode, "exclude_tests": args.exclude_tests, "repo": args.repo}
        res = send_request("hybrid_search", params)
    elif args.command == "search-chunks":
        params = {"query": args.query, "max_results": args.max_results, "exclude_tests": args.exclude_tests,
                  "repo": args.repo}
        if args.chunk_type: params["chunk_type"] = args.chunk_type
        res = send_request("search_chunks", params)
    elif args.command == "similar-code":
        params = {"query": args.query, "max_results": args.max_results, "exclude_tests": args.exclude_tests,
                  "repo": args.repo}
        res = send_request("find_similar_code", params)
    elif args.command == "similar-symbol":
        res = send_request("find_similar_to_symbol", {
            "repo": args.repo, "symbol": args.symbol, "max_results": args.max_results,
        })
    elif args.command == "structure":
        res = send_request("get_project_structure", {"repo": args.repo, "max_depth": args.max_depth})

    print(res)

if __name__ == "__main__":
    main()
