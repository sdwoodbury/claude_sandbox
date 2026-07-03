---
name: narsil_code_tracing
description: "Standard Operating Procedure for tracking execution paths, call graphs, and variable data flows."
---

# Code Tracing & Flow Analysis SOP

Use these tools when debugging errors, tracking down panics, or mapping out the execution ripple-effects of a code change. Do not attempt to manually trace function calls across files.

## 1. Mapping the Call Hierarchy (Upstream & Downstream)
* **What calls this?** If you need to see what triggers a function or method (e.g., to find the origin of an unhandled error), use `find_callers`.
* **What does this execute?** To trace the execution path downstream from a specific entry point, use `find_callees`.
* **Visualizing Hierarchy:** For a clean, structured overview of a function's deeper dependency execution chain, call `get_call_graph`. Do not guess execution order.
* **The Bridge Check:** If you need to know exactly how execution gets from Point A to Point B across the repository, use `get_call_path`. This eliminates manual file-hopping to find middleware or glue code.

## 2. Advanced Intra-Function Analysis (Deep Debugging)
When a bug is localized inside a specific complex function, do not guess branch conditions or variable mutations. Use flow analysis:
* **Branching & Loops:** Use `analyze_control_flow` to map out basic blocks, conditional logic splits, and loops. This exposes edge cases where logic might get stuck or bypassed.
* **State & Mutation Tracking:** Use `analyze_data_flow` to trace where variables are defined, where they are mutated, and where they are consumed. Use this to pinpoint unexpected mutations or lifetime/ownership issues.
