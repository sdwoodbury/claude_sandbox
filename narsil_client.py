#!/usr/bin/env python3
import sys
import bisect
import json
import socket
import subprocess
import os
from enum import Enum
from typing import List, Optional
from typing_extensions import Annotated
import typer

sys.stdout.reconfigure(encoding="utf-8")
SOCKET_PATH = "/tmp/narsil_mcp"

# Initialize Typer App
app = typer.Typer(help="Narsil CLI Client", add_completion=False)

# Reusable default repo configuration matching original behavior
DEFAULT_REPO = os.path.basename(os.getcwd())

# ── Shared Enums for Strict CLI Validation ─────────────────────────────────

class SymbolType(str, Enum):
    struct = "struct"
    class_ = "class"
    enum = "enum"
    interface = "interface"
    function = "function"
    method = "method"
    trait = "trait"
    type = "type"
    all = "all"

class Direction(str, Enum):
    imports = "imports"
    imported_by = "imported_by"
    both = "both"

class Kind(str, Enum):
    function = "function"
    class_ = "class"
    struct = "struct"
    interface = "interface"
    enum = "enum"
    variable = "variable"
    all = "all"

class DocType(str, Enum):
    file = "file"
    function = "function"
    class_ = "class"
    struct = "struct"
    method = "method"

class HybridMode(str, Enum):
    hybrid = "hybrid"
    bm25 = "bm25"
    tfidf = "tfidf"

class ChunkType(str, Enum):
    function = "function"
    method = "method"
    class_ = "class"
    trait = "trait"
    module = "module"
    all = "all"


# ── Core Communication and Utility Logic ────────────────────────────────────

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
            text = content[0].get("text", "")
            try:
              text = text.encode('cp1252').decode('utf-8')
            except (UnicodeEncodeError, UnicodeDecodeError):
              pass
            return text
        return "No content retuned"

    except FileNotFoundError:
        return f"Error: Socket {SOCKET_PATH} not found. Is narsil-mcp running?"
    except Exception as e:
        return f"Communication error: {e}"

def get_document_symbols(file_path: str) -> dict:
    """Executes ra_tool.py to retrieve document symbols for a given file
    and parses the result into a dict of {line_number -> {name, container}}.
    """
    cmd = ["/bin/ra_tool.py", "documentSymbols", file_path]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    if data.get("status") != "success":
        error_msg = data.get("message", "Unknown error reported by tool")
        raise RuntimeError(f"ra_tool.py execution failed: {error_msg}")

    ra_map = {}
    symbols = data.get("result", [])

    for sym in symbols:
        location = sym.get("location", {})
        line = location.get("line")

        if line is not None:
            ra_map[int(line)] = {
                "name": sym.get("name"),
                "container": sym.get("containerName"),
            }

    return ra_map

def get_file_symbols(file_path: str, raw_output: str) -> str:
    """Parses find-symbols output by splitting chunks on '##'."""
    ra_map = {}
    try:
        ra_map = get_document_symbols(file_path)
    except subprocess.CalledProcessError as e:
        return f"Subprocess error invoking ra_tools.py: {e.stderr.strip()}"
    except json.JSONDecodeError:
        return "Error: ra_tools.py stdout was not valid JSON."
    except FileNotFoundError:
        return "Error: /bin/ra_tools.py could not be found."
    except RuntimeError as e:
        return f"Error: {e}"

    sorted_ra_lines = sorted(ra_map.keys())
    output_sections = [f"# Line Number: Symbol for {file_path}", ""]
    sections = raw_output.split("##")

    for section in sections:
        lines = section.splitlines()
        if not lines:
            continue

        section_name = lines[0].strip()
        if not section_name or "symbols" in section_name.lower():
            continue

        output_sections.append(f"## {section_name}")

        for line in lines[1:]:
            line = line.strip()
            if not line.startswith("-"):
                continue

            parts = line.split(")")
            if len(parts) > 1:
                before_bracket = parts[0]
                idx_colon = before_bracket.rfind(":")

                if idx_colon != -1:
                    idx_backtick = before_bracket.find("`", idx_colon)
                    if idx_backtick != -1:
                        line_num = before_bracket[idx_colon + 1 : idx_backtick].strip()
                    else:
                        line_num = before_bracket[idx_colon + 1 :].strip()
                else:
                    return f"Error: could not parse line number from {before_bracket}"

                definition = ")".join(parts[1:]).strip()
                line_key = int(line_num)
                
                if line_key not in ra_map:
                    maybe_idx = bisect.bisect_left(sorted_ra_lines, line_key)
                    if maybe_idx > 0:
                        line_key = sorted_ra_lines[maybe_idx - 1]
                ra_info = ra_map.get(line_key)

                if ra_info and ra_info["name"] in definition and ra_info.get("container"):
                    ra_name = ra_info["name"]
                    container = ra_info["container"]
    
                    for kw in ["fn ", "struct ", "enum ", "type ", "const "]:
                        if f"{kw}{ra_name}" in definition:
                            definition = definition.replace(f"{kw}{ra_name}", f"{kw}{container}::{ra_name}")
                            break
                output_sections.append(f"- {line_num}: {definition}")

        output_sections.append("")

    return "\n".join(output_sections).strip()

def filter_chunks_by_files(raw_chunks_output: str, files: list[str]) -> str:
    """Filters search-chunks output to only include chunks whose header contains one of the given file paths."""
    sections = raw_chunks_output.split("---")
    matched_chunks = []

    for section in sections:
        chunk_text = section.strip()
        if not chunk_text or "Chunk" not in chunk_text:
            continue
        header = chunk_text.split("```")[0]
        if any(f in header for f in files):
            matched_chunks.append(f"---\n\n{chunk_text}\n\n---")

    if matched_chunks:
        return "\n\n".join(matched_chunks)

    return f"Error: No chunks found matching files {files}."

def get_chunks_by_lines(raw_chunks_output: str, target_lines: list[int]) -> str:
    """Splits Narsil chunks by '---' and returns matching chunk blocks."""
    sorted_lines = sorted(list(set(target_lines)))
    if not sorted_lines:
        return "Error: No line numbers provided."

    sections = raw_chunks_output.split("---")
    matched_chunks = []

    for section in sections:
        chunk_text = section.strip()
        if not chunk_text or "Chunk" not in chunk_text:
            continue

        start_line, end_line = None, None

        for line in chunk_text.splitlines():
            line_str = line.strip()
            if "Lines" in line_str:
                cleaned_line = line_str.replace("**", "")
                parts = cleaned_line.split(":")
                if len(parts) >= 2:
                    range_parts = parts[1].strip().split("-")
                    if len(range_parts) == 2:
                        try:
                            start_line = int(range_parts[0].strip())
                            end_line = int(range_parts[1].strip())
                            break
                        except ValueError:
                            pass

        if start_line is not None and end_line is not None:
            if any(start_line <= t_line <= end_line for t_line in sorted_lines):
                matched_chunks.append(f"---\n\n{chunk_text}\n\n---")

    if matched_chunks:
        return "\n\n".join(matched_chunks)

    return f"Error: None of the lines {sorted_lines} fall within any indexed chunk boundaries."


# ── Typer CLI Command Map Implementation ───────────────────────────────────

@app.command("symbol", help="Get symbol source with surrounding context")
def cmd_symbol(
    symbols: Annotated[List[str], typer.Argument(help="One or more named symbols to view")],
    context_lines: Annotated[int, typer.Option("--context-lines", help="Number of context lines")] = 0,
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    parts = []
    for symbol in symbols:
        res = send_request("get_symbol_definition", {
            "repo": repo, "symbol": symbol, "context_lines": context_lines,
        })
        parts.append(f"# Symbol  {symbol}\n{res}")
    print("\n---\n\n".join(parts))

@app.command("excerpt", help="Read a line, auto-expanded to its full scope")
def cmd_excerpt(
    path: Annotated[str, typer.Argument(help="Target file path")],
    lines: Annotated[List[int], typer.Argument(help="One or more line numbers to extract around")],
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    res = send_request("get_excerpt", {
        "repo": repo, "path": path, "lines": list(lines), "expand_to_scope": True,
    })
    print(res)

@app.command("refs", help="Find all references to a symbol")
def cmd_refs(
    symbol: Annotated[str, typer.Argument(help="Target symbol")],
    include_definition: Annotated[bool, typer.Option("--include-definition/--no-include-definition")] = True,
    exclude_tests: Annotated[bool, typer.Option("--exclude-tests/--include-tests")] = False,
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    res = send_request("find_references", {
        "repo": repo, "symbol": symbol,
        "include_definition": include_definition,
        "exclude_tests": exclude_tests,
    })
    print(res)

@app.command("find-symbols", help="Find structs, classes, functions by type/pattern")
def cmd_find_symbols(
    symbol_type: Annotated[SymbolType, typer.Option("--type", help="Filter by symbol structure type")] = SymbolType.all,
    pattern: Annotated[Optional[str], typer.Option("--pattern", help="Fuzzy name pattern matching")] = None,
    file_pattern: Annotated[Optional[str], typer.Option("--file-pattern", help="Filter by file architecture patterns")] = None,
    exclude_tests: Annotated[bool, typer.Option("--exclude-tests/--include-tests")] = False,
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    params = {"repo": repo, "symbol_type": symbol_type.value, "exclude_tests": exclude_tests}
    if pattern: params["pattern"] = pattern
    if file_pattern: params["file_pattern"] = file_pattern
    res = send_request("find_symbols", params)
    print(res)

@app.command("deps", help="Analyze imports and dependents")
def cmd_deps(
    path: Annotated[str, typer.Argument(help="Target module or file path")],
    direction: Annotated[Direction, typer.Option("--direction", help="The search path orientation orientation")] = Direction.both,
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    res = send_request("get_dependencies", {
        "repo": repo, "path": path, "direction": direction.value,
    })
    print(res)

@app.command("workspace-search", help="Fuzzy search symbols across workspace")
def cmd_workspace_search(
    query: Annotated[str, typer.Argument(help="Search pattern string")],
    kind: Annotated[Kind, typer.Option("--kind", help="Kind classification filters")] = Kind.all,
    limit: Annotated[int, typer.Option("--limit", help="Cap total results returned")] = 20,
):
    res = send_request("workspace_symbol_search", {
        "query": query, "kind": kind.value, "limit": limit,
    })
    print(res)

@app.command("usages", help="Cross-file symbol usage with imports")
def cmd_usages(
    symbol: Annotated[str, typer.Argument(help="Symbol name query")],
    no_imports: Annotated[bool, typer.Option("--no-imports")] = False,
    exclude_tests: Annotated[bool, typer.Option("--exclude-tests")] = False,
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    res = send_request("find_symbol_usages", {
        "repo": repo, "symbol": symbol,
        "include_imports": not no_imports,
        "exclude_tests": exclude_tests,
    })
    print(res)

@app.command("exports", help="Get exported symbols from a file/module")
def cmd_exports(
    path: Annotated[str, typer.Argument(help="Module or file target path")],
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    res = send_request("get_export_map", {"repo": repo, "path": path})
    print(res)

@app.command("call-graph", help="Get call graph for repository/function")
def cmd_call_graph(
    function: Annotated[Optional[str], typer.Argument(help="Target entry function name")] = None,
    depth: Annotated[int, typer.Option("--depth", help="Maximum lookup hierarchy depth boundaries")] = 3,
    exclude_tests: Annotated[bool, typer.Option("--exclude-tests")] = False,
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    params = {"repo": repo, "depth": depth, "exclude_tests": exclude_tests}
    if function: params["function"] = function
    res = send_request("get_call_graph", params)
    print(res)

@app.command("callers", help="Find functions that call a function")
def cmd_callers(
    function: Annotated[str, typer.Argument(help="Target function leaf node")],
    transitive: Annotated[bool, typer.Option("--transitive")] = False,
    max_depth: Annotated[int, typer.Option("--max-depth")] = 5,
    exclude_tests: Annotated[bool, typer.Option("--exclude-tests")] = False,
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    res = send_request("get_callers", {
        "repo": repo, "function": function,
        "transitive": transitive, "max_depth": max_depth,
        "exclude_tests": exclude_tests,
    })
    print(res)

@app.command("callees", help="Find functions called by a function")
def cmd_callees(
    function: Annotated[str, typer.Argument(help="Root function identifier")],
    transitive: Annotated[bool, typer.Option("--transitive")] = False,
    max_depth: Annotated[int, typer.Option("--max-depth")] = 5,
    exclude_tests: Annotated[bool, typer.Option("--exclude-tests")] = False,
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    res = send_request("get_callees", {
        "repo": repo, "function": function,
        "transitive": transitive, "max_depth": max_depth,
        "exclude_tests": exclude_tests,
    })
    print(res)

@app.command("call-path", help="Find path between two functions")
def cmd_call_path(
    from_fn: Annotated[str, typer.Argument(help="Starting trace node path identifier")],
    to_fn: Annotated[str, typer.Argument(help="Destination search node execution target")],
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    res = send_request("find_call_path", {
        "repo": repo, "from": from_fn, "to": to_fn,
    })
    print(res)

@app.command("control-flow", help="Analyze basic blocks, branches, loops")
def cmd_control_flow(
    path: Annotated[str, typer.Argument(help="Module file target path location")],
    function: Annotated[str, typer.Argument(help="Target logic wrapper scope")],
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    res = send_request("get_control_flow", {
        "repo": repo, "path": path, "function": function,
    })
    print(res)

@app.command("data-flow", help="Trace variable definitions and uses")
def cmd_data_flow(
    path: Annotated[str, typer.Argument(help="Target source code execution file path")],
    function: Annotated[str, typer.Argument(help="Target function block identifier definition")],
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    res = send_request("get_data_flow", {
        "repo": repo, "path": path, "function": function,
    })
    print(res)

@app.command("chunks", help="Get AST-aware chunks for a file")
def cmd_chunks(
    path: Annotated[str, typer.Argument(help="File structure lookup target path")],
    no_imports: Annotated[bool, typer.Option("--no-imports")] = False,
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    res = send_request("get_chunks", {
        "repo": repo, "path": path, "include_imports": not no_imports,
    })
    print(res)

@app.command("chunk-stats", help="Statistics about code chunks")
def cmd_chunk_stats(
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    res = send_request("get_chunk_stats", {"repo": repo})
    print(res)

@app.command("embedding-stats", help="Embedding index statistics")
def cmd_embedding_stats():
    res = send_request("get_embedding_stats", {})
    print(res)

@app.command("search", help="Keyword search with relevance ranking")
def cmd_search(
    query: Annotated[str, typer.Argument(help="Lexical match query payload string")],
    file_pattern: Annotated[Optional[str], typer.Option("--file-pattern")] = None,
    max_results: Annotated[int, typer.Option("--max-results")] = 10,
    exclude_tests: Annotated[bool, typer.Option("--exclude-tests")] = False,
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    params = {"query": query, "max_results": max_results, "exclude_tests": exclude_tests, "repo": repo}
    if file_pattern: params["file_pattern"] = file_pattern
    res = send_request("search_code", params)
    print(res)

@app.command("semantic", help="BM25-ranked semantic search")
def cmd_semantic(
    query: Annotated[str, typer.Argument(help="Natural syntax context description string query")],
    doc_type: Annotated[Optional[DocType], typer.Option("--doc-type", help="Structural module filter context parameters")] = None,
    max_results: Annotated[int, typer.Option("--max-results")] = 10,
    exclude_tests: Annotated[bool, typer.Option("--exclude-tests")] = False,
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    params = {"query": query, "max_results": max_results, "exclude_tests": exclude_tests, "repo": repo}
    if doc_type: params["doc_type"] = doc_type.value
    res = send_request("semantic_search", params)
    print(res)

@app.command("hybrid", help="Combined BM25 + TF-IDF search with rank fusion")
def cmd_hybrid(
    query: Annotated[str, typer.Argument(help="Multi-model index engine target match data query string")],
    max_results: Annotated[int, typer.Option("--max-results")] = 10,
    mode: Annotated[HybridMode, typer.Option("--mode")] = HybridMode.hybrid,
    exclude_tests: Annotated[bool, typer.Option("--exclude-tests")] = False,
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    params = {"query": query, "max_results": max_results, "mode": mode.value, "exclude_tests": exclude_tests, "repo": repo}
    res = send_request("hybrid_search", params)
    print(res)

@app.command("search-chunks", help="Search over AST-aware code chunks")
def cmd_search_chunks(
    query: Annotated[str, typer.Argument(help="Strict logical code search parameter queries")],
    chunk_type: Annotated[Optional[ChunkType], typer.Option("--chunk-type")] = None,
    max_results: Annotated[int, typer.Option("--max-results")] = 10,
    exclude_tests: Annotated[bool, typer.Option("--exclude-tests")] = False,
    files: Annotated[Optional[List[str]], typer.Option("--file", help="Filter results to chunks from these files")] = None,
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    params = {"query": query, "max_results": max_results, "exclude_tests": exclude_tests, "repo": repo}
    if chunk_type: params["chunk_type"] = chunk_type.value
    res = send_request("search_chunks", params)
    if files:
        res = filter_chunks_by_files(res, list(files))
    print(res)

@app.command("similar-code", help="Find code similar to a snippet (TF-IDF)")
def cmd_similar_code(
    query: Annotated[str, typer.Argument(help="Raw sample template block validation text context source string")],
    max_results: Annotated[int, typer.Option("--max-results")] = 10,
    exclude_tests: Annotated[bool, typer.Option("--exclude-tests")] = False,
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    params = {"query": query, "max_results": max_results, "exclude_tests": exclude_tests, "repo": repo}
    res = send_request("find_similar_code", params)
    print(res)

@app.command("similar-symbol", help="Find code similar to a symbol")
def cmd_similar_symbol(
    symbol: Annotated[str, typer.Argument(help="Existing codebase module search reference label key")],
    max_results: Annotated[int, typer.Option("--max-results")] = 10,
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    res = send_request("find_similar_to_symbol", {
        "repo": repo, "symbol": symbol, "max_results": max_results,
    })
    print(res)

@app.command("structure", help="Get directory tree with file icons and sizes")
def cmd_structure(
    max_depth: Annotated[int, typer.Option("--max-depth")] = 4,
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    res = send_request("get_project_structure", {"repo": repo, "max_depth": max_depth})
    print(res)

@app.command("file-skeleton", help="Get the symbols for a file")
def cmd_file_skeleton(
    file: Annotated[str, typer.Option("--file", help="Path to the source file", show_default=False)],
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    params = {"repo": repo, "symbol_type": "all", "exclude_tests": False, "file_pattern": file}
    raw_output = send_request("find_symbols", params)
    res = get_file_symbols(file, raw_output)
    print(res)

@app.command("get-chunks-by-lines", help="For each line: get the chunk that contains the line")
def cmd_get_chunks_by_lines(
    file: Annotated[str, typer.Option("--file", help="Path to the source file", show_default=False)],
    lines: Annotated[List[int], typer.Option("--line", help="Line numbers to retrieve chunks for", show_default=False)],
    repo: Annotated[str, typer.Option("--repo", help="Repository name")] = DEFAULT_REPO,
):
    raw_output = send_request("get_chunks", {
        "repo": repo, "path": file, "include_imports": True,
    })
    res = get_chunks_by_lines(raw_output, list(lines))
    print(res)


if __name__ == "__main__":
    app()
