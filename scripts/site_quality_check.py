#!/usr/bin/env python3
from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

SITE_HOST = "afpframework.org"


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.urls: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag in {"a", "link"} and values.get("href"):
            self.urls.append((tag, values["href"] or ""))
        if tag in {"img", "script", "source"} and values.get("src"):
            self.urls.append((tag, values["src"] or ""))


def local_target(public: Path, raw_url: str) -> Path | None:
    if not raw_url or raw_url.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None

    parsed = urlparse(raw_url)
    if parsed.scheme in {"http", "https"} and parsed.netloc not in {SITE_HOST, f"www.{SITE_HOST}"}:
        return None
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return None

    path = unquote(parsed.path)
    if not path or path == "/":
        return public / "index.html"

    relative = path.lstrip("/")
    target = public / relative
    if path.endswith("/"):
        return target / "index.html"
    if target.suffix:
        return target
    return target / "index.html"


def check_page_links(public: Path, page_rel: str, errors: list[str]) -> None:
    page = public / page_rel
    if not page.exists():
        errors.append(f"required page missing: {page_rel}")
        return

    parser = LinkCollector()
    parser.feed(page.read_text(encoding="utf-8", errors="replace"))
    for tag, raw_url in parser.urls:
        target = local_target(public, raw_url)
        if target is not None and not target.exists():
            errors.append(f"broken local {tag} reference in {page_rel}: {raw_url}")


def check_marker(public: Path, page_rel: str, marker: str, errors: list[str]) -> None:
    page = public / page_rel
    if not page.exists():
        return
    text = page.read_text(encoding="utf-8", errors="replace")
    if marker not in text:
        errors.append(f"required content marker missing in {page_rel}: {marker}")


def main() -> int:
    public = Path(sys.argv[1] if len(sys.argv) > 1 else "public").resolve()
    errors: list[str] = []

    required = [
        "index.html", "zh/index.html",
        "specification/index.html", "zh/specification/index.html",
        "specification/history/index.html", "zh/specification/history/index.html",
        "evaluations/index.html", "zh/evaluations/index.html",
        "evaluations/protocol/index.html", "zh/evaluations/protocol/index.html",
        "failure-cases/index.html", "zh/failure-cases/index.html",
        "publication/afp-whitepaper/index.html", "zh/publication/afp-whitepaper/index.html",
        "privacy/index.html", "zh/privacy/index.html",
        "uploads/afp-whitepaper.pdf", "uploads/afp-whitepaper.zh.pdf",
        "robots.txt", "sitemap.xml", "pagefind/pagefind.js",
    ]
    for rel in required:
        if not (public / rel).exists():
            errors.append(f"required output missing: {rel}")

    forbidden = [
        "event/example/index.html", "teaching/js/index.html", "teaching/python/index.html",
        "project/pandas/index.html", "project/pytorch/index.html", "project/scikit/index.html",
        "zh/author/庄辉恺/index.html",
    ]
    for rel in forbidden:
        if (public / rel).exists():
            errors.append(f"starter/stale output should not be public: {rel}")

    bad_markers = {
        "your-form-link": "placeholder form URL",
        "GetResearchDev": "starter-template social handle",
    }
    for html in public.rglob("*.html"):
        text = html.read_text(encoding="utf-8", errors="replace")
        for marker, label in bad_markers.items():
            if marker in text:
                errors.append(f"{label} remains in {html.relative_to(public)}")

    governed_pages = [
        "index.html", "zh/index.html",
        "specification/index.html", "zh/specification/index.html",
        "specification/history/index.html", "zh/specification/history/index.html",
        "evaluations/index.html", "zh/evaluations/index.html",
        "evaluations/protocol/index.html", "zh/evaluations/protocol/index.html",
        "failure-cases/index.html", "zh/failure-cases/index.html",
        "privacy/index.html", "zh/privacy/index.html",
    ]
    for page_rel in governed_pages:
        check_page_links(public, page_rel, errors)

    check_marker(public, "specification/index.html", "Working Specification", errors)
    check_marker(public, "specification/index.html", "Version:", errors)
    check_marker(public, "zh/specification/index.html", "Working Specification", errors)
    check_marker(public, "specification/history/index.html", "Document status vocabulary", errors)
    check_marker(public, "zh/specification/history/index.html", "文件狀態用語", errors)

    css_files = list((public / "css").glob("*.css")) if (public / "css").exists() else []
    if not css_files:
        errors.append("no compiled main CSS found under public/css")

    image_files = list((public / "media").glob("*")) if (public / "media").exists() else []
    if not any(path.is_file() for path in image_files):
        errors.append("no generated media asset found under public/media")

    if errors:
        print("SITE QUALITY CHECK FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    html_count = sum(1 for _ in public.rglob("*.html"))
    print(f"SITE QUALITY CHECK PASSED: {html_count} HTML files")
    print("Verified required routes, specification governance, CSS, media, PDFs, Pagefind, local links, and absence of known stale outputs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
