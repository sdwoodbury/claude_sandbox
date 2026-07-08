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
