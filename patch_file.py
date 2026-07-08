#! /usr/bin/env python3
import sys
import re
from pathlib import Path
from typing import List, Optional
import typer

# Force Typer to pretend Rich isn't installed
import typer.core
import typer.main
typer.core.HAS_RICH = False
typer.main.HAS_RICH = False

app = typer.Typer(
    help="Apply SEARCH/REPLACE block patches to a file.",
    add_completion=False,
    epilog="""
Example block format:
<<<<<<< SEARCH
Text to find in the file
=======
Text to replace it with
>>>>>>> REPLACE
"""
)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def validate_block_integrity(patch_content: str):
    """
    Validate the integrity of patch blocks before parsing.
    Checks for balanced markers and correct sequence.
    """
    search_count = patch_content.count("<<<<<<< SEARCH")
    separator_count = patch_content.count("=======")
    replace_count = patch_content.count(">>>>>>> REPLACE")
    
    if not (search_count == separator_count == replace_count):
        raise ValueError(
            f"Malformed patch format: Unbalanced markers - "
            f"{search_count} SEARCH, {separator_count} separator, {replace_count} REPLACE markers"
        )

    markers = []
    for line in patch_content.splitlines():
        line = line.strip()
        if line in ["<<<<<<< SEARCH", "=======", ">>>>>>> REPLACE"]:
            markers.append(line)
    
    for i in range(0, len(markers), 3):
        if i+2 < len(markers):
            if markers[i] != "<<<<<<< SEARCH" or markers[i+1] != "=======" or markers[i+2] != ">>>>>>> REPLACE":
                raise ValueError(
                    f"Malformed patch format: Incorrect marker sequence at position {i}: "
                    f"Expected [SEARCH, SEPARATOR, REPLACE], got {markers[i:i+3]}"
                )
    
    sections = patch_content.split("<<<<<<< SEARCH")
    for i, section in enumerate(sections[1:], 1):
        if "<<<<<<< SEARCH" in section and section.find(">>>>>>> REPLACE") > section.find("<<<<<<< SEARCH"):
            raise ValueError(f"Malformed patch format: Nested SEARCH marker in block {i}")

def parse_search_replace_blocks(patch_content: str):
    """
    Parse multiple search-replace blocks from the patch content.
    Returns a list of tuples (search_text, replace_text).
    """
    search_marker = "<<<<<<< SEARCH"
    separator = "======="
    replace_marker = ">>>>>>> REPLACE"
    
    validate_block_integrity(patch_content)

    pattern = f"{search_marker}\\n(.*?)\\n{separator}\\n(.*?)\\n{replace_marker}"
    matches = re.findall(pattern, patch_content, re.DOTALL)

    if not matches:
        blocks = []
        lines = patch_content.splitlines()
        i = 0
        while i < len(lines):
            if lines[i] == search_marker:
                search_start = i + 1
                separator_idx = -1
                replace_end = -1

                for j in range(search_start, len(lines)):
                    if lines[j] == separator:
                        separator_idx = j
                        break

                if separator_idx == -1:
                    raise ValueError("Invalid format: missing separator")

                for j in range(separator_idx + 1, len(lines)):
                    if lines[j] == replace_marker:
                        replace_end = j
                        break

                if replace_end == -1:
                    raise ValueError("Invalid format: missing replace marker")

                search_text = "\n".join(lines[search_start:separator_idx])
                replace_text = "\n".join(lines[separator_idx + 1:replace_end])
                
                if any(marker in search_text for marker in [search_marker, separator, replace_marker]):
                    raise ValueError(f"Block {len(blocks)+1}: Search text contains patch markers")
                if any(marker in replace_text for marker in [search_marker, separator, replace_marker]):
                    raise ValueError(f"Block {len(blocks)+1}: Replace text contains patch markers")
                
                blocks.append((search_text, replace_text))
                i = replace_end + 1
            else:
                i += 1

        if blocks:
            return blocks
        else:
            raise ValueError("Invalid patch format. Expected block format with SEARCH/REPLACE markers.")

    for i, (search_text, replace_text) in enumerate(matches):
        if any(marker in search_text for marker in [search_marker, separator, replace_marker]):
            raise ValueError(f"Block {i+1}: Search text contains patch markers")
        if any(marker in replace_text for marker in [search_marker, separator, replace_marker]):
            raise ValueError(f"Block {i+1}: Replace text contains patch markers")

    return matches


@app.command()
def main(
    file: Path = typer.Argument(
        ..., 
        help="The path to the file to patch", 
        exists=True, 
        dir_okay=False, 
        resolve_path=True
    ),
    allowed_dir: List[Path] = typer.Option(
        ..., 
        "--allowed-dir", 
        "-a",
        help="Allowed base directory for project paths (can be used multiple times)",
        resolve_path=True
    ),
    patch_file: Optional[Path] = typer.Option(
        None, 
        "--patch-file", 
        "-p",
        help="Path to the patch file (if omitted, reads from stdin)",
        exists=True,
        dir_okay=False,
        resolve_path=True
    )
):
    """
    Apply a block-format patch to a local file.
    """
    # Ensure allowed directories exist or fallback to home
    valid_allowed_dirs = [str(d) for d in allowed_dir if d.exists()]
    if not valid_allowed_dirs:
        valid_allowed_dirs = [str(Path.home().resolve())]

    if not any(str(file).startswith(base) for base in valid_allowed_dirs):
        eprint(f"PermissionError: File {file} is not in allowed directories.")
        raise typer.Exit(code=1)

    # Read patch content
    try:
        if patch_file:
            patch_content = patch_file.read_text(encoding='utf-8')
        else:
            if sys.stdin.isatty():
                eprint("Error: No patch content provided via stdin or --patch-file.")
                raise typer.Exit(code=1)
            patch_content = sys.stdin.read()
    except Exception as e:
        eprint(f"Failed to read patch content: {e}")
        raise typer.Exit(code=1)

    # Read the current file content
    try:
        original_content = file.read_text(encoding='utf-8')
    except Exception as e:
        eprint(f"Error reading target file: {e}")
        raise typer.Exit(code=1)

    # Parse and Apply Patch
    try:
        blocks = parse_search_replace_blocks(patch_content)
        if not blocks:
            raise ValueError("No valid search-replace blocks found in the patch content")

        eprint(f"Found {len(blocks)} search-replace blocks")

        current_content = original_content
        applied_blocks = 0

        for i, (search_text, replace_text) in enumerate(blocks):
            eprint(f"Processing block {i+1}/{len(blocks)}")
            count = current_content.count(search_text)

            if count == 1:
                eprint(f"Block {i+1}: Found exactly one exact match")
                current_content = current_content.replace(search_text, replace_text)
                applied_blocks += 1
            elif count > 1:
                raise ValueError(f"Block {i+1}: The search text appears {count} times in the file. "
                                 "Provide more context to identify the specific occurrence.")
            else:
                raise ValueError(f"Block {i+1}: Could not find the search text in the file. "
                                 "Ensure the search text exactly matches the content in the file.")

        # Write the final content back
        file.write_text(current_content, encoding='utf-8')
        print(f"Successfully applied {applied_blocks} patch blocks to {file}")

    except Exception as e:
        eprint(f"Error: {str(e)}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
