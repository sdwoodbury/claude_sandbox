# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp",
# ]
# ///

"""
I had trouble getting Claude to use this and opted for skills instead.
"""
 
import asyncio
import subprocess
from typing import List, Optional, Literal
from mcp.server.fastmcp import FastMCP

# Initialize the MCP Server
mcp = FastMCP("NarsilMiddleman")

def run_narsil_cli(args: List[str]) -> str:
    """Helper function to execute the underlying narsil CLI and capture output."""
    try:
        # Filter out empty strings or None values
        clean_args = [str(arg) for arg in args if arg is not None and arg != ""]
        result = subprocess.run(
            ["/bin/narsil_client.py"] + clean_args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error executing Narsil CLI: {e.stderr}\nOutput: {e.stdout}"

# ==========================================
# 1. AST-Aware Chunking & File Reading
# ==========================================

@mcp.tool()
async def scan_file_skeleton(file_path: str) -> str:
    """
    CRITICAL: Use this FIRST when exploring a new file.
    Returns a lightweight outline of the file's structure broken down by AST logic.
    Use this to map out the file before doing targeted reads.
    """
    args = ["file-skeleton", "--file", file_path]  
    raw_chunks = run_narsil_cli(args)
    return raw_chunks

@mcp.tool()
async def read_excerpt(file_path: str, target_lines: List[int]) -> str:
    """
    CRITICAL: Use this to retrieve needed context to follow up after scan_file_skeleton, find_references, etc.
    For each line in line_numbers, get the AST chunk that contains that line.
    You MUST pass an array of integers for the target_lines.
    """
    # note that narsil provides an excerpt function. but the targeted chunk reading is desired here.
    # Flattens the array of ints into string arguments for the CLI
    args = ["get-chunks-by-lines", file_path, "--lines"] + [str(line) for line in target_lines]
    return run_narsil_cli(args)

@mcp.tool()
async def get_chunk_stats() -> str:
    """Returns statistics about AST code chunks for the entire repository."""
    return run_narsil_cli(["chunk-stats"])

@mcp.tool()
async def get_embedding_stats() -> str:
    """Returns statistics about the current embedding index."""
    return run_narsil_cli(["embedding-stats"])


# ==========================================
# 2. Symbol Search and Navigation
# ==========================================

@mcp.tool()
async def read_symbol(symbol_name: str, context_lines: int = 0) -> str:
    """
    Fetches the complete, exact source code of a named symbol (function, class, etc.).
    """
    args = ["symbol", symbol_name]
    if context_lines > 0:
        args.extend(["--context-lines", str(context_lines)])
    return run_narsil_cli(args)

@mcp.tool()
async def find_references(symbol_name: str, exclude_tests: bool = False) -> str:
    """Finds all references to a specific symbol across the codebase."""
    args = ["refs", symbol_name]
    if exclude_tests:
        args.append("--exclude-tests")
    return run_narsil_cli(args)

@mcp.tool()
async def find_symbols_by_pattern(
    pattern: str = "*", 
    type_filter: Literal["struct", "class", "enum", "interface", "function", "method", "trait", "type", "all"] = "all",
    file_pattern: Optional[str] = None,
    exclude_tests: bool = False
) -> str:
    """Finds structs, classes, and functions by fuzzy type or string pattern."""
    args = ["find-symbols", "--type", type_filter, "--pattern", pattern]
    if file_pattern:
        args.extend(["--file-pattern", file_pattern])
    if exclude_tests:
        args.append("--exclude-tests")
    return run_narsil_cli(args)

@mcp.tool()
async def analyze_dependencies(path: str, direction: Literal["imports", "imported_by", "both"] = "both") -> str:
    """Analyzes imports and dependents for a specific file."""
    return run_narsil_cli(["deps", path, "--direction", direction])

@mcp.tool()
async def workspace_search(
    fuzzy_name: str, 
    kind: Literal["function", "class", "struct", "interface", "enum", "variable", "all"] = "all",
    limit: int = 10
) -> str:
    """Fuzzy searches for symbols across the entire workspace."""
    return run_narsil_cli(["workspace-search", fuzzy_name, "--kind", kind, "--limit", str(limit)])

@mcp.tool()
async def find_usages(symbol_name: str, no_imports: bool = False, exclude_tests: bool = False) -> str:
    """Finds cross-file symbol usage."""
    args = ["usages", symbol_name]
    if no_imports:
        args.append("--no-imports")
    if exclude_tests:
        args.append("--exclude-tests")
    return run_narsil_cli(args)

@mcp.tool()
async def get_exports(path: str) -> str:
    """Gets all exported symbols from a specific file or module."""
    return run_narsil_cli(["exports", path])


# ==========================================
# 3. Call Graph Analysis
# ==========================================

@mcp.tool()
async def get_call_graph(function_name: str, depth: int = 2, exclude_tests: bool = False) -> str:
    """Generates a call graph for a specific function."""
    args = ["call-graph", function_name, "--depth", str(depth)]
    if exclude_tests:
        args.append("--exclude-tests")
    return run_narsil_cli(args)

@mcp.tool()
async def find_callers(function_name: str, max_depth: int = 1, transitive: bool = False, exclude_tests: bool = False) -> str:
    """Finds functions that call the specified function."""
    args = ["callers", function_name, "--max-depth", str(max_depth)]
    if transitive:
        args.append("--transitive")
    if exclude_tests:
        args.append("--exclude-tests")
    return run_narsil_cli(args)

@mcp.tool()
async def find_callees(function_name: str, max_depth: int = 1, transitive: bool = False, exclude_tests: bool = False) -> str:
    """Finds functions that are called BY the specified function."""
    args = ["callees", function_name, "--max-depth", str(max_depth)]
    if transitive:
        args.append("--transitive")
    if exclude_tests:
        args.append("--exclude-tests")
    return run_narsil_cli(args)

@mcp.tool()
async def get_call_path(from_function: str, to_function: str) -> str:
    """Finds the execution path between two distinct functions."""
    return run_narsil_cli(["call-path", from_function, to_function])


# ==========================================
# 4. Flow Analysis
# ==========================================

@mcp.tool()
async def analyze_control_flow(path: str, function_name: str) -> str:
    """Analyzes basic blocks, branches, and loops for a function."""
    return run_narsil_cli(["control-flow", path, function_name])

@mcp.tool()
async def analyze_data_flow(path: str, function_name: str) -> str:
    """Traces variable definitions and use sites within a function."""
    return run_narsil_cli(["data-flow", path, function_name])


# ==========================================
# 5. Code Search
# ==========================================

@mcp.tool()
async def search_keywords(query: str, file_pattern: Optional[str] = None, max_results: int = 10, exclude_tests: bool = False) -> str:
    """Exact keyword text search with relevance ranking."""
    args = ["search", query, "--max-results", str(max_results)]
    if file_pattern:
        args.extend(["--file-pattern", file_pattern])
    if exclude_tests:
        args.append("--exclude-tests")
    return run_narsil_cli(args)

@mcp.tool()
async def search_semantic(
    query: str, 
    doc_type: Literal["file", "function", "class", "struct", "method"] = "function",
    max_results: int = 5,
    exclude_tests: bool = False
) -> str:
    """
    BM25-ranked semantic search. Best for natural language queries about what code DOES.
    Example: "deserialize JSON into user struct"
    """
    args = ["semantic", query, "--doc-type", doc_type, "--max-results", str(max_results)]
    if exclude_tests:
        args.append("--exclude-tests")
    return run_narsil_cli(args)

@mcp.tool()
async def search_hybrid(
    query: str, 
    mode: Literal["hybrid", "bm25", "tfidf"] = "hybrid",
    max_results: int = 10,
    exclude_tests: bool = False
) -> str:
    """Combined search utilizing rank fusion."""
    args = ["hybrid", query, "--mode", mode, "--max-results", str(max_results)]
    if exclude_tests:
        args.append("--exclude-tests")
    return run_narsil_cli(args)

@mcp.tool()
async def search_chunks(
    query: str, 
    chunk_type: Literal["function", "method", "class", "trait", "module", "all"] = "all",
    max_results: int = 5,
    exclude_tests: bool = False
) -> str:
    """Searches strictly over AST-aware code chunks."""
    args = ["search-chunks", query, "--chunk-type", chunk_type, "--max-results", str(max_results)]
    if exclude_tests:
        args.append("--exclude-tests")
    return run_narsil_cli(args)

@mcp.tool()
async def find_similar_code(code_snippet: str, max_results: int = 5, exclude_tests: bool = False) -> str:
    """Finds existing codebase logic similar to a provided raw code snippet."""
    args = ["similar-code", code_snippet, "--max-results", str(max_results)]
    if exclude_tests:
        args.append("--exclude-tests")
    return run_narsil_cli(args)

@mcp.tool()
async def find_similar_symbol(symbol_name: str, max_results: int = 5) -> str:
    """Finds code similar to a named symbol."""
    return run_narsil_cli(["similar-symbol", symbol_name, "--max-results", str(max_results)])


# ==========================================
# 6. Repository View
# ==========================================

@mcp.tool()
async def view_repository_structure(max_depth: int = 3) -> str:
    """
    Returns a directory tree mapping of the workspace.
    Use this to understand project architecture before searching.
    """
    return run_narsil_cli(["structure", "--max-depth", str(max_depth)])

def main():
    # Runs the server using standard stdio transport
    mcp.run()

if __name__ == "__main__":
    main()
