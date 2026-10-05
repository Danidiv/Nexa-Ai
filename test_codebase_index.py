#!/usr/bin/env python3
"""
Real codebase index demo - no model needed, pure static analysis.

Point it at any project folder you already generated (e.g. one of your
workspace/multi-<timestamp> or workspace/backend-<timestamp> folders) and
it will show you:
  - every file found, and what real symbols it extracted from each
  - the real dependency graph between files
  - how a natural-language instruction routes to a file

Usage:
    python3 test_codebase_index.py workspace/multi-1789560974
    python3 test_codebase_index.py workspace/multi-1789560974 "add a signup link to the login page"
"""
import sys
from pathlib import Path

from services.real_codebase_index import index_project, find_relevant_file


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 test_codebase_index.py <project_folder> ["optional query"]')
        sys.exit(1)

    project_dir = Path(sys.argv[1])
    if not project_dir.exists():
        print(f"Folder not found: {project_dir}")
        sys.exit(1)

    query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None

    print(f"Indexing: {project_dir}\n")
    index = index_project(project_dir)

    if not index.files:
        print("No indexable files found (looking for .html, .css, .js, .py).")
        sys.exit(1)

    print(f"=== Files found: {len(index.files)} ===")
    for path, symbols in sorted(index.files.items()):
        print(f"\n[{symbols.file_type}] {path}")
        if symbols.ids:
            print(f"  ids:            {sorted(symbols.ids)}")
        if symbols.classes:
            print(f"  classes:        {sorted(symbols.classes)}")
        if symbols.css_selectors:
            print(f"  css selectors:  {sorted(symbols.css_selectors)}")
        if symbols.py_functions:
            print(f"  py functions:   {sorted(symbols.py_functions)}")
        if symbols.py_classes:
            print(f"  py classes:     {sorted(symbols.py_classes)}")
        if symbols.py_imports:
            print(f"  py imports:     {sorted(symbols.py_imports)}")
        if symbols.js_functions:
            print(f"  js functions:   {sorted(symbols.js_functions)}")
        if symbols.references:
            print(f"  references:     {sorted(symbols.references)}")

    print(f"\n=== Dependency graph ===")
    edges = index.dependency_edges()
    if edges:
        for src, dst in edges:
            print(f"  {src}  ->  {dst}")
    else:
        print("  (no cross-file references found)")

    if query:
        print(f"\n=== Routing query: {query!r} ===")
        target = find_relevant_file(index, query)
        print(f"  -> {target if target else '(no confident match)'}")
    else:
        print(f"\n(Add a query as an extra argument to test routing, e.g.:")
        print(f'   python3 test_codebase_index.py "{project_dir}" "add a signup link to the login page")')


if __name__ == "__main__":
    main()
