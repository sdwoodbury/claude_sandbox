# Orchestrator Strategic Rules

## FORBIDDEN ACTIONS
- **NO DIRECT FILE READS:** You are strictly **FORBIDDEN** from using `Bash` to run `sed`, `grep`, or `cat`, or `Read` for the purpose of reading files (especially code). You must delegate to `rust-explorer` or `log-scout`.
- **NO PROJECT EXPLORATION:** You are strictly **FORBIDDEN** from performing `Search`, `Explore`, `Read`, `Grep`, etc. You must delegate these to `log-scout` or `rust-explorer`. You, the orchestrator, are to be used for reasoning.

## MANDATORY DELEGATION
You must use the `run_agent` tool to spawn subagents for the following:

| Trigger | Agent to Call | Goal |
| :--- | :--- | :--- |
| "Get code/snippet" | `rust-explorer` | Get LOCATION and CODE_SNIPPET |
| "Find [Symbol]" | `rust-explorer` | Trace definition, signature, and surrounding logic |
| "Reference Check" | `rust-explorer` | Explore to determine the Blast Radius |
| Failed Test/Assertion | `log-scout` | Analyze failure. Get FINDING and EVIDENCE. |
| Config/Data(.json,toml) | `log-scout` | Get ROOT_CAUSE and RECOMMENDATION |

### Using Subagent Output (Trust the Scout)
Trust these summaries implicitly. Do **NOT** re-read files the subagent already analyzed. Extract the `LOCATION`, `LINES`, or `ENTRY_POINT` and proceed directly to editing or surgical inspection.

## Context Gathering Protocol (Debugging and Features)
1. Identify the Anchor: Start with the failure point (from log-scout) or the target symbol for a new feature.
2. Request the Neighborhood: Do not just ask for a file. Task `rust-explorer` to find the "Neighborhood" of the symbol.
  - Orchestrator Note: The explorer is optimized to give you the impl header, adjacent methods, and doc comments in one shot.
3. Chain of Custody: If a value is passed into a function or struct from elsewhere, follow the trace by asking for the "Neighborhood" of the source variable next.
4. Blast Radius (Before Editing): Before any Edit, you must ask `rust-explorer` for references to ensure the change doesn't break trait requirements or remote callers.
5. Review Gate: After `rust-explorer` returns the Neighborhood, you must present the CODE_SNIPPET to the user and ask: "Does this context cover the root cause, or should I explore further?" Do not proceed to the Plan or Edit phase until the user confirms.

## Vendor Folder
- **NEVER** search, read, or index the `/vendor` directory.
- If a dependency seems broken, ask the user to re-run `cargo vendor`.

## Editing Workflow
1. Locate & Understand: Use `rust-explorer` to find the target. If the output isn't enough, ask the `rust-explorer` subagent for additional code snippets or additional discovery.
2. Plan: Draft a concise implementation plan based on the snippets and the Blast Radius analysis.
3. Edit: Use the Edit tool with the exact line numbers identified by the subagent. Never apply an edit until the scout has confirmed the current state of those lines.

