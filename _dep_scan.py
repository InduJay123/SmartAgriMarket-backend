import ast
import json
from pathlib import Path
from collections import defaultdict

root = Path(r"c:\Users\User\OneDrive\Documents\GitHub\SmartAgriMarket-backend")
skip_parts = {".git", ".venv", "venv", "__pycache__", "node_modules"}

imports = defaultdict(list)
module_counts = defaultdict(int)
files_scanned = 0
parse_errors = []

for path in root.rglob("*.py"):
    if any(part in skip_parts for part in path.parts):
        continue
    files_scanned += 1
    rel = path.relative_to(root).as_posix()
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="latin-1")
    try:
        tree = ast.parse(text)
    except Exception as exc:
        parse_errors.append({"file": rel, "error": str(exc)})
        continue

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                full = alias.name
                root_mod = full.split('.')[0]
                entry = {
                    "file": rel,
                    "line": getattr(node, "lineno", None),
                    "kind": "import",
                    "full": full,
                }
                imports[root_mod].append(entry)
                module_counts[root_mod] += 1
        elif isinstance(node, ast.ImportFrom) and node.module:
            full = node.module
            root_mod = full.split('.')[0]
            entry = {
                "file": rel,
                "line": getattr(node, "lineno", None),
                "kind": "from",
                "full": full,
            }
            imports[root_mod].append(entry)
            module_counts[root_mod] += 1

summary_lines = [
    f"files_scanned={files_scanned}",
    f"parse_errors={len(parse_errors)}",
]
for mod in sorted(module_counts):
    summary_lines.append(f"{mod}\t{module_counts[mod]}")

(root / "_dep_summary.txt").write_text("\n".join(summary_lines), encoding="utf-8")
(root / "_dep_imports.json").write_text(json.dumps(imports, indent=2), encoding="utf-8")
(root / "_dep_parse_errors.json").write_text(json.dumps(parse_errors, indent=2), encoding="utf-8")
print("WROTE _dep_summary.txt, _dep_imports.json, _dep_parse_errors.json")
