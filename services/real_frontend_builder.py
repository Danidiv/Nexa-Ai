"""
Real Frontend Builder — Phase 3 of the Lovable roadmap, actually wired.

Unlike completion_frontend_plan.py (which only stores whatever fields you
pass it), this module does the real work:

    prompt -> model call -> generated HTML/CSS/JS -> written to disk

This is intentionally small and unglamorous. It does ONE real thing well,
instead of many fake things with impressive names.
"""
from __future__ import annotations

import re
from pathlib import Path


SYSTEM_PROMPT = (
    "You are a frontend code generator. Given a short description of a UI, "
    "output a SINGLE self-contained HTML file that implements it. "
    "Requirements:\n"
    "- Inline ALL CSS in a <style> tag and ALL JS in a <script> tag, both "
    "inside this same file.\n"
    "- Do NOT include <link rel=\"stylesheet\" href=\"...\"> for any external "
    "CSS file. Do NOT include <script src=\"...\"></script> pointing at any "
    "external JS file. This file must not reference any other file at all.\n"
    "- No external dependencies, no CDN links, no explanations.\n"
    "- Output ONLY the raw HTML, starting with <!DOCTYPE html>.\n"
    "- Do not wrap the output in markdown code fences."
)

# Matches a full <link ...> tag, and a full <script ...>...</script> element.
_LINK_TAG_RE = re.compile(r'<link\b[^>]*>', re.IGNORECASE)
_SCRIPT_TAG_RE = re.compile(r'<script\b[^>]*>\s*</script>', re.IGNORECASE)
_HREF_RE = re.compile(r'\bhref\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
_SRC_RE = re.compile(r'\bsrc\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)


def find_dangling_references(html: str) -> list[str]:
    """
    Real check (not a stub): scan generated HTML for <link href=...> or
    <script src=...> tags pointing at local files, since we explicitly told
    the model to inline everything and not reference separate files.
    Returns a list of the offending reference strings found (empty = clean).
    External CDN URLs (http/https) are not flagged here - the "no CDN"
    instruction is enforced by the prompt, this check is specifically for
    the self-contained-file promise being broken.
    """
    problems = []
    for tag in _LINK_TAG_RE.findall(html):
        m = _HREF_RE.search(tag)
        if m and not m.group(1).startswith(("http://", "https://", "//")):
            problems.append(m.group(1))
    for tag in _SCRIPT_TAG_RE.findall(html):
        m = _SRC_RE.search(tag)
        if m and not m.group(1).startswith(("http://", "https://", "//")):
            problems.append(m.group(1))
    return problems


def _strip_markdown_fences(text: str) -> str:
    """Model outputs sometimes wrap code in ```html ... ``` even when told not to."""
    text = text.strip()
    fence_match = re.match(r"^```[a-zA-Z]*\n(.*)\n```$", text, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()
    return text


def generate_frontend_html(gateway, description: str) -> tuple[str, list[str]]:
    """
    Call the model gateway to generate a real HTML page for the given
    description. Returns (html, dangling_references) where
    dangling_references is a non-empty list if the model broke the
    self-contained-file promise (e.g. left in a <link href="styles.css">
    to a file that will never exist).

    `gateway` is any object implementing ModelGateway.chat(messages) -> str
    (e.g. core.models.lm_studio.LMStudioGateway).
    """
    if not description or not description.strip():
        raise ValueError("description is required")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": description.strip()},
    ]
    # Cap output length so a slow/local model can't run unbounded, but give
    # enough room for a "thinking" model's reasoning tokens PLUS the real
    # HTML content (reasoning alone can easily use 500-1500 tokens).
    raw = gateway.chat(messages, temperature=0.2, max_tokens=4000)
    html = _strip_markdown_fences(raw)

    if "<html" not in html.lower():
        raise ValueError(
            "Model did not return HTML. Got:\n" + html[:300]
        )

    dangling = find_dangling_references(html)
    return html, dangling


def remove_dangling_references(html: str) -> str:
    """
    Real repair, not just detection: strip out <link href="local.css"> and
    <script src="local.js"></script> tags that point at files which will
    never exist, since the model was supposed to (and usually did) inline
    the real CSS/JS elsewhere in the same file already.
    CDN links (http/https) are left untouched.
    """
    def _strip_if_local(tag_match: re.Match, href_or_src_re: re.Pattern) -> str:
        full_tag = tag_match.group(0)
        m = href_or_src_re.search(full_tag)
        if m and not m.group(1).startswith(("http://", "https://", "//")):
            return ""
        return full_tag

    cleaned = _LINK_TAG_RE.sub(lambda m: _strip_if_local(m, _HREF_RE), html)
    cleaned = _SCRIPT_TAG_RE.sub(lambda m: _strip_if_local(m, _SRC_RE), cleaned)
    return cleaned


_ID_ATTR_RE = re.compile(r'\bid\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
_CLASS_ATTR_RE = re.compile(r'\bclass\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
_TAG_RE = re.compile(r'<([a-zA-Z][a-zA-Z0-9]*)\b', re.IGNORECASE)

_GET_ELEMENT_BY_ID_RE = re.compile(r'getElementById\(\s*["\']([^"\']+)["\']\s*\)')
_GET_ELEMENTS_BY_CLASS_RE = re.compile(r'getElementsByClassName\(\s*["\']([^"\']+)["\']\s*\)')
_GET_ELEMENTS_BY_TAG_RE = re.compile(r'getElementsByTagName\(\s*["\']([^"\']+)["\']\s*\)')
_QUERY_SELECTOR_RE = re.compile(r'querySelector(?:All)?\(\s*["\']([^"\']+)["\']\s*\)')

_HTML_TAGS_ALWAYS_PRESENT = {
    "html", "head", "body", "meta", "title", "style", "script", "link",
    "br", "hr",
}


def _extract_html_inventory(html: str) -> dict:
    """
    Real, lightweight scan of what elements actually exist in the markup:
    every id="...", every class="...", every tag name used. Used to check
    whether the JS is looking for something that isn't there.
    Deliberately simple (regex, not a real DOM parser) - good enough to
    catch obvious mismatches like the 'form' bug, not meant to be a full
    HTML validator.
    """
    ids = set(_ID_ATTR_RE.findall(html))
    classes = set()
    for cls_attr in _CLASS_ATTR_RE.findall(html):
        classes.update(cls_attr.split())
    tags = {t.lower() for t in _TAG_RE.findall(html)} | _HTML_TAGS_ALWAYS_PRESENT
    return {"ids": ids, "classes": classes, "tags": tags}


def _selector_target_exists(selector: str, inventory: dict) -> bool | None:
    """
    Check a single simple CSS selector ('#id', '.class', 'tagname') against
    the inventory. Returns True/False for simple selectors we understand,
    or None if the selector is too complex to safely judge (e.g. combinators
    like 'div.container > input') - callers should skip None results rather
    than treat them as a problem, to avoid false positives.
    """
    selector = selector.strip()
    if not selector or any(ch in selector for ch in " >+~[:,"):
        return None  # too complex to safely evaluate with a regex-based scan
    if selector.startswith("#"):
        return selector[1:] in inventory["ids"]
    if selector.startswith("."):
        return selector[1:] in inventory["classes"]
    if selector.isalnum():
        return selector.lower() in inventory["tags"]
    return None


def find_dom_reference_problems(html: str) -> list[str]:
    """
    Real check: scan <script> content for JS that looks up DOM elements
    (getElementById, querySelector, etc.) and flag any lookup whose target
    doesn't actually exist anywhere in the HTML. This is what would have
    caught the real bug: document.querySelector('form') when there was no
    <form> tag in the page at all.

    This does NOT auto-repair anything - guessing what missing HTML should
    look like is too risky to do silently. It only reports problems so a
    human (or a future repair step) can decide what to do.
    """
    problems = []
    inventory = _extract_html_inventory(html)

    for target_id in _GET_ELEMENT_BY_ID_RE.findall(html):
        if target_id not in inventory["ids"]:
            problems.append(f"getElementById('{target_id}') - no element with id=\"{target_id}\" exists")

    for target_class in _GET_ELEMENTS_BY_CLASS_RE.findall(html):
        if target_class not in inventory["classes"]:
            problems.append(f"getElementsByClassName('{target_class}') - no element with that class exists")

    for target_tag in _GET_ELEMENTS_BY_TAG_RE.findall(html):
        if target_tag.lower() not in inventory["tags"]:
            problems.append(f"getElementsByTagName('{target_tag}') - no <{target_tag}> element exists")

    for selector in _QUERY_SELECTOR_RE.findall(html):
        exists = _selector_target_exists(selector, inventory)
        if exists is False:
            problems.append(f"querySelector('{selector}') - no matching element exists in the HTML")

    return problems


def write_frontend_project(task_id: str, html: str, workspace_dir: str = "workspace") -> Path:
    """
    Write the generated HTML to workspace/<task_id>/index.html and return
    the path. This is a real file on disk, not a stored/hashed record.
    """
    if not task_id or not task_id.strip():
        raise ValueError("task_id is required")

    project_dir = Path(workspace_dir).resolve() / task_id.strip()
    project_dir.mkdir(parents=True, exist_ok=True)

    index_path = project_dir / "index.html"
    index_path.write_text(html, encoding="utf-8")
    return index_path


def build_frontend(gateway, task_id: str, description: str, workspace_dir: str = "workspace"):
    """
    The full real chain: description -> model -> HTML -> (auto-repaired if
    needed) -> file on disk.

    Returns (path: Path, dangling_references: list[str], dom_problems: list[str]).

    - dangling_references: <link>/<script src> tags pointing at files that
      would never exist. These ARE auto-repaired (safe to strip).
    - dom_problems: JS looking up HTML elements (by id/class/tag/selector)
      that don't actually exist in the page. These are NOT auto-repaired
      (too risky to guess the fix) - just reported so you know the page
      may be broken even though it "ran" without an error.
    """
    html, dangling = generate_frontend_html(gateway, description)
    if dangling:
        html = remove_dangling_references(html)
    dom_problems = find_dom_reference_problems(html)
    path = write_frontend_project(task_id, html, workspace_dir=workspace_dir)
    return path, dangling, dom_problems
