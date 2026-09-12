#!/usr/bin/env python3
from __future__ import annotations

import html.parser
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_BASE_URL = "https://afpframework.org/"
RETRIES = 8
RETRY_SECONDS = 10
TIMEOUT_SECONDS = 20

# Markers are intentionally specific enough to reject an older cached site that
# merely returns HTTP 200. They are part of the production revision contract.
REQUIRED_PAGES = {
    "/": "A reliability layer for AI workflows",
    "/specification/": "Working Specification",
    "/specification/history/": "Document status vocabulary",
    "/evaluations/": "benchmark scores not yet published",
    "/evaluations/protocol/": "Publication gate",
    "/failure-cases/": "Failure Cases",
    "/zh/": "AI 工作流程的可靠性層",
    "/zh/specification/": "Working Specification",
    "/zh/evaluations/protocol/": "發布門檻",
}

FORBIDDEN_PAGE_MARKERS = {
    "/specification/": ["Jan 1, 0001"],
    "/evaluations/": ["Jan 1, 0001"],
    "/failure-cases/": ["Jan 1, 0001"],
    "/zh/specification/": ["1月 1, 0001", "中文 (简体)", "分钟阅读时长", ">语言<"],
    "/zh/evaluations/protocol/": ["1月 1, 0001", "中文 (简体)", "分钟阅读时长", ">语言<"],
}

REQUIRED_FILES = {
    "/uploads/afp-whitepaper-2025-annotated.pdf": "application/pdf",
    "/uploads/afp-whitepaper-2025-annotated.zh.pdf": "application/pdf",
}


class AssetCollector(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stylesheets: list[str] = []
        self.media: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        rel = (values.get("rel") or "").lower().split()
        if tag == "link" and "stylesheet" in rel and values.get("href"):
            self.stylesheets.append(values["href"] or "")
        if tag in {"img", "source"} and values.get("src"):
            self.media.append(values["src"] or "")


def fetch(url: str) -> tuple[int, bytes, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "AFP-production-acceptance/1.1",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return response.status, response.read(), response.headers.get("Content-Type", "")


def fetch_with_retry(url: str) -> tuple[int, bytes, str]:
    last_error: Exception | None = None
    for attempt in range(1, RETRIES + 1):
        try:
            status, body, content_type = fetch(url)
            if 200 <= status < 300:
                return status, body, content_type
            last_error = RuntimeError(f"HTTP {status}")
        except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
            last_error = exc
        if attempt < RETRIES:
            print(f"Retry {attempt}/{RETRIES - 1}: {url} ({last_error})")
            time.sleep(RETRY_SECONDS)
    raise RuntimeError(f"production request failed after {RETRIES} attempts: {url}: {last_error}")


def absolute_url(base_url: str, raw_url: str) -> str:
    return urllib.parse.urljoin(base_url, raw_url)


def main() -> int:
    base_url = (sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE_URL).rstrip("/") + "/"
    errors: list[str] = []
    homepage_body = b""

    for path, marker in REQUIRED_PAGES.items():
        url = urllib.parse.urljoin(base_url, path.lstrip("/"))
        try:
            status, body, content_type = fetch_with_retry(url)
            text = body.decode("utf-8", errors="replace")
            if "text/html" not in content_type.lower():
                errors.append(f"expected HTML for {url}, got {content_type or 'unknown content type'}")
            if marker not in text:
                errors.append(f"expected deployed-revision marker {marker!r} missing from {url}")
            for forbidden in FORBIDDEN_PAGE_MARKERS.get(path, []):
                if forbidden in text:
                    errors.append(f"forbidden live marker {forbidden!r} present in {url}")
            if path == "/":
                homepage_body = body
            print(f"PASS {status}: {url}")
        except Exception as exc:
            errors.append(str(exc))

    for path, expected_content_type in REQUIRED_FILES.items():
        url = urllib.parse.urljoin(base_url, path.lstrip("/"))
        try:
            status, body, content_type = fetch_with_retry(url)
            if expected_content_type not in content_type.lower():
                errors.append(f"expected {expected_content_type} for {url}, got {content_type or 'unknown'}")
            if not body.startswith(b"%PDF-"):
                errors.append(f"expected PDF signature for {url}")
            if len(body) < 10_000:
                errors.append(f"artifact unexpectedly small: {url} ({len(body)} bytes)")
            print(f"PASS {status}: artifact {url}")
        except Exception as exc:
            errors.append(str(exc))

    if homepage_body:
        parser = AssetCollector()
        parser.feed(homepage_body.decode("utf-8", errors="replace"))
        if not parser.stylesheets:
            errors.append("homepage exposes no stylesheet link")
        else:
            css_url = absolute_url(base_url, parser.stylesheets[0])
            try:
                status, body, content_type = fetch_with_retry(css_url)
                if "text/css" not in content_type.lower():
                    errors.append(f"expected CSS content type for {css_url}, got {content_type or 'unknown'}")
                if not body:
                    errors.append(f"stylesheet is empty: {css_url}")
                print(f"PASS {status}: stylesheet {css_url}")
            except Exception as exc:
                errors.append(str(exc))

        if not parser.media:
            errors.append("homepage exposes no img/source media URL")
        else:
            media_url = absolute_url(base_url, parser.media[0])
            try:
                status, body, content_type = fetch_with_retry(media_url)
                if not content_type.lower().startswith(("image/", "video/", "audio/")):
                    errors.append(f"expected media content type for {media_url}, got {content_type or 'unknown'}")
                if not body:
                    errors.append(f"media asset is empty: {media_url}")
                print(f"PASS {status}: media {media_url}")
            except Exception as exc:
                errors.append(str(exc))

    if errors:
        print("PRODUCTION ACCEPTANCE FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PRODUCTION ACCEPTANCE PASSED")
    print("Verified authoritative protocol revision, zh-Hant UI markers, absence of undefined dates, annotated PDFs, one stylesheet, and one rendered media asset on the canonical production domain.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
