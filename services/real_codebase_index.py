"""
Real Codebase Intelligence — Stage 65-75% of the build path.

Builds a REAL index of what's actually in a generated multi-file project:
- what symbols (HTML ids/classes, CSS selectors, Python functions/classes)
  each file defines
- which files reference which other files (a real dependency graph, not a
  stub record)

This exists to answer one real question: given "add a signup link to this
project", which file should actually be edited, and what's already in it?
Without this, every edit would mean regenerating the whole project blindly
and hoping nothing breaks - which is exactly the kind of "looks done but
isn't" trap this whole build has been catching one by one.

Deliberately simple/regex-and-ast based, not a full language server. Good
enough to route edits to the right file and avoid re-generating things that
already work.
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FileSymbols:
    path: str
    file_type: str  # "html" | "css" | "js" | "py" | "other"
    ids: set = field(default_factory=set)
    classes: set = field(default_factory=set)
    css_selectors: set = field(default_factory=set)
    py_functions: set = field(default_factory=set)
    py_classes: set = field(default_factory=set)
    py_imports: set = field(default_factory=set)
    js_functions: set = field(default_factory=set)
    references: set = field(default_factory=set)  # other local files this file points to
    purpose_words: set = field(default_factory=set)  # keywords for search, from filename + content


@dataclass
class ProjectIndex:
    project_dir: Path
    files: dict = field(default_factory=dict)  # path -> FileSymbols

    def dependency_edges(self) -> list[tuple[str, str]]:
        """Real dependency graph: (from_file, to_file) pairs actually found in the code."""
        edges = []
        for path, symbols in self.files.items():
            for ref in symbols.references:
                if ref in self.files:
                    edges.append((path, ref))
        return edges


_ID_RE = re.compile(r'\bid\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
_CLASS_RE = re.compile(r'\bclass\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
_HREF_RE = re.compile(r'\bhref\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
_SRC_RE = re.compile(r'\bsrc\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
_SELECTOR_BLOCK_RE = re.compile(r'([^{}]+)\{[^{}]*\}')
_TAG_TEXT_RE = re.compile(r'<(?:h1|h2|h3|label|button|title|legend)[^>]*>([^<]+)<', re.IGNORECASE)
_JS_GET_BY_ID_RE = re.compile(r'getElementById\(\s*["\']([^"\']+)["\']\s*\)')
_JS_QUERY_SELECTOR_RE = re.compile(r'querySelector(?:All)?\(\s*["\']([^"\']+)["\']\s*\)')
_JS_FUNCTION_RE = re.compile(r'\bfunction\s+(\w+)\s*\(')
_WORD_RE = re.compile(r'[a-zA-Z]{3,}')

# Honest heuristic, not a real classifier: words that commonly signal
# which KIND of file a request is about, independent of that file's own
# symbols. Needed because symbol-overlap alone ties easily (e.g. both an
# HTML class "login-container" and a CSS selector for it share the word
# "login" - the query's own phrasing is what actually disambiguates
# "add a link to the page" (HTML) from "change the styling" (CSS)).
_FILE_TYPE_INTENT_HINTS = {
    "html": {"page", "link", "button", "form", "header", "footer", "nav",
             "heading", "title", "field", "input", "element"},
    "css": {"style", "styling", "color", "colour", "layout", "design",
            "font", "spacing", "padding", "margin", "css"},
    "py": {"backend", "server", "endpoint", "handler", "api", "route",
           "database", "request", "response"},
    "js": {"script", "javascript", "validation", "event", "click",
           "submit", "interactive", "behavior", "behaviour"},
}


def _expand_words(text: str) -> set:
    """
    Real fix for a real gap: plain word extraction misses identifiers like
    'LoginHandler' matching a query for 'login handler', because CSS class
    names split naturally on hyphens ('login-container' -> 'login',
    'container') but camelCase/PascalCase identifiers don't split on their
    own. This adds the camelCase-split sub-words alongside the whole
    identifier, so 'LoginHandler' contributes both 'loginhandler' (exact)
    and 'login' + 'handler' (sub-words) to the searchable keyword pool.
    """
    words = set()
    for token in _WORD_RE.findall(text):
        words.add(token.lower())
        for part in re.findall(r'[A-Z][a-z0-9]*|[a-z0-9]+', token):
            if len(part) >= 3:
                words.add(part.lower())
    return words


def _index_html(content: str) -> tuple[set, set, set]:
    ids = set(_ID_RE.findall(content))
    classes = set()
    for cls_attr in _CLASS_RE.findall(content):
        classes.update(cls_attr.split())
    references = set()
    for href in _HREF_RE.findall(content):
        if not href.startswith(("http://", "https://", "//")):
            references.add(href)
    for src in _SRC_RE.findall(content):
        if not src.startswith(("http://", "https://", "//")):
            references.add(src)
    return ids, classes, references


_CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)


def _index_css(content: str) -> set:
    """
    Real fix for THREE real bugs found in practice, in order of discovery:
    (1) the old regex grabbed only the fragment right before '{' (turning
    'button:hover' into just 'hover'), (2) it silently dropped every
    selector but the last in a comma-separated group ('input, button {'
    kept only 'button'), and (3) a CSS comment sitting right before a rule
    ('/* style.css */\nbody {') got merged INTO the selector text instead
    of being recognized as a comment, producing a garbage selector like
    '/* style.css */ body'. Comments are stripped first now, before any
    selector-block parsing happens.
    """
    content = _CSS_COMMENT_RE.sub("", content)
    selectors = set()
    for block in _SELECTOR_BLOCK_RE.findall(content):
        for part in block.split(","):
            sel = re.sub(r"\s+", " ", part.strip())
            if sel and not sel.startswith("@"):
                selectors.add(sel)
    return selectors


def _index_js(content: str) -> tuple[set, set]:
    """
    Real JS indexing: extract actual DOM references the script makes
    (getElementById/querySelector targets) and function names it defines.
    This is what makes a JS file's real behavior searchable/routable,
    instead of the file contributing nothing (or noise) to the index.
    """
    ids = set(_JS_GET_BY_ID_RE.findall(content))
    js_functions = set(_JS_FUNCTION_RE.findall(content))
    for selector in _JS_QUERY_SELECTOR_RE.findall(content):
        if selector.startswith("#"):
            ids.add(selector[1:])
    return ids, js_functions


def _index_python(content: str) -> tuple[set, set, set]:
    functions, classes, imports = set(), set(), set()
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return functions, classes, imports
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.add(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.add(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return functions, classes, imports


def _guess_file_type(path: str) -> str:
    if path.endswith((".html", ".htm")):
        return "html"
    if path.endswith(".css"):
        return "css"
    if path.endswith(".js"):
        return "js"
    if path.endswith(".py"):
        return "py"
    return "other"


def index_project(project_dir: Path) -> ProjectIndex:
    """
    Real static analysis: walk every file actually on disk in project_dir,
    parse it with the right tool for its type (ast for Python, regex for
    HTML/CSS - good enough for generated single-purpose files), and build
    a real symbol table + dependency graph.
    """
    project_dir = Path(project_dir)
    index = ProjectIndex(project_dir=project_dir)

    for file_path in sorted(project_dir.rglob("*")):
        if not file_path.is_file():
            continue
        rel_path = str(file_path.relative_to(project_dir)).replace("\\", "/")
        file_type = _guess_file_type(rel_path)
        if file_type == "other":
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        symbols = FileSymbols(path=rel_path, file_type=file_type)

        if file_type == "html":
            symbols.ids, symbols.classes, symbols.references = _index_html(content)
        elif file_type == "css":
            symbols.css_selectors = _index_css(content)
        elif file_type == "js":
            symbols.ids, symbols.js_functions = _index_js(content)
        elif file_type == "py":
            symbols.py_functions, symbols.py_classes, symbols.py_imports = _index_python(content)

        # purpose_words: built from REAL extracted symbols + filename +
        # (for HTML) visible text in headings/buttons/labels - NOT the raw
        # file text. Scoring against raw content is noisy: e.g.
        # "addEventListener" contains "add", which would falsely match any
        # query containing the word "add". Symbols are what a file
        # actually IS; raw text is mostly incidental syntax.
        words = _expand_words(rel_path)
        words |= set().union(*(_expand_words(s) for s in symbols.ids)) if symbols.ids else set()
        words |= set().union(*(_expand_words(s) for s in symbols.classes)) if symbols.classes else set()
        words |= set().union(*(_expand_words(s.lstrip(".#")) for s in symbols.css_selectors)) if symbols.css_selectors else set()
        words |= set().union(*(_expand_words(s) for s in symbols.py_functions)) if symbols.py_functions else set()
        words |= set().union(*(_expand_words(s) for s in symbols.py_classes)) if symbols.py_classes else set()
        words |= set().union(*(_expand_words(s) for s in symbols.py_imports)) if symbols.py_imports else set()
        words |= set().union(*(_expand_words(s) for s in symbols.js_functions)) if symbols.js_functions else set()
        if file_type == "html":
            for text_match in _TAG_TEXT_RE.findall(content):
                words |= _expand_words(text_match)
        symbols.purpose_words = words

        index.files[rel_path] = symbols

    return index


def find_relevant_file(index: ProjectIndex, query: str) -> str | None:
    """
    Relevance scoring = real symbol overlap (query words vs. actual
    ids/classes/functions/imports the file defines) PLUS a small, honestly
    labeled heuristic bonus when the query's own phrasing hints at a file
    type ("styling" -> css, "endpoint" -> py). The heuristic exists because
    symbol overlap alone ties easily - an HTML class and its matching CSS
    selector often share the same word, so the query's phrasing is what
    actually disambiguates intent.

    Returns the best-matching file path, or None if nothing matches at all.
    """
    query_words = _expand_words(query)
    if not query_words:
        return None

    best_path, best_score = None, 0
    for path, symbols in index.files.items():
        score = len(query_words & symbols.purpose_words)
        score += len(query_words & _FILE_TYPE_INTENT_HINTS.get(symbols.file_type, set()))
        if score > best_score:
            best_score, best_path = score, path

    return best_path
