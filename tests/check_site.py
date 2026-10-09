#!/usr/bin/env python3
"""Dependency-free multi-page static quality checks for the Thabz site."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "services.html", "contact.html", "404.html")
REQUIRED_FILES = (*PAGES, "styles.css", "script.js", "README.md", "favicon.svg")
errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


class PageAudit(HTMLParser):
    """Collect relevant markup without external test dependencies."""

    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.ids = []
        self.h1_count = 0
        self.main_landmarks = 0
        self.focusable_main = False
        self.skip_links = 0
        self.labelled_navs = 0
        self.images = []
        self.references = []
        self.metas = {}
        self.visible_text = []
        self.json_scripts = []
        self._inside_ignored = None
        self._inside_json = False
        self._json_buffer = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "h1":
            self.h1_count += 1
        if tag == "main" and attrs.get("id") == "main-content":
            self.main_landmarks += 1
            self.focusable_main = attrs.get("tabindex") == "-1"
        if tag == "a" and attrs.get("href") == "#main-content":
            self.skip_links += 1
        if tag == "nav" and attrs.get("aria-label"):
            self.labelled_navs += 1
        if tag == "img":
            self.images.append(attrs)
        for attribute in ("href", "src"):
            value = attrs.get(attribute)
            if value:
                self.references.append((tag, attribute, value))
        if attrs.get("srcset"):
            for candidate in attrs["srcset"].split(","):
                url = candidate.strip().split(" ")[0]
                if url:
                    self.references.append((tag, "srcset", url))
        for attribute in attrs:
            if attribute.lower().startswith("on"):
                errors.append(f"{self.source}: inline event handler {attribute} found")
        if tag == "a" and attrs.get("target") == "_blank":
            rel = set(attrs.get("rel", "").lower().split())
            if not {"noopener", "noreferrer"}.issubset(rel):
                errors.append(f"{self.source}: target=_blank link lacks rel=noopener noreferrer")
        if tag == "meta":
            key = attrs.get("name") or attrs.get("property")
            if key and attrs.get("content"):
                self.metas[key.lower()] = attrs["content"].strip()
        if tag == "script" and attrs.get("type", "").lower() == "application/ld+json":
            self._inside_json = True
            self._json_buffer = []
        elif tag in ("script", "style"):
            self._inside_ignored = tag

    def handle_endtag(self, tag):
        if tag == self._inside_ignored:
            self._inside_ignored = None
        if tag == "script" and self._inside_json:
            self.json_scripts.append("".join(self._json_buffer))
            self._inside_json = False
            self._json_buffer = []

    def handle_data(self, data):
        if self._inside_json:
            self._json_buffer.append(data)
        elif self._inside_ignored is None:
            self.visible_text.append(data)


def read_file(relative_path):
    path = ROOT / relative_path
    if not path.is_file():
        errors.append(f"Missing required file: {relative_path}")
        return ""
    return path.read_text(encoding="utf-8")


sources = {path: read_file(path) for path in REQUIRED_FILES}
sources["README.md"] = read_file("README.md")
sources["AGENTS.md"] = read_file("AGENTS.md")
sources["docs/QUALITY-GATES.md"] = read_file("docs/QUALITY-GATES.md")
sources[".github/workflows/site-quality.yml"] = read_file(".github/workflows/site-quality.yml")
sources["data/business.json"] = read_file("data/business.json")
sources["THABZ_WEBSITE_SPEC.md"] = read_file("THABZ_WEBSITE_SPEC.md")
sources["ROSCORE_PROJECT_MANIFEST.md"] = read_file("ROSCORE_PROJECT_MANIFEST.md")

audits = {}
for page in PAGES:
    source = sources.get(page, "")
    if not source:
        continue
    audit = PageAudit(page)
    try:
        audit.feed(source)
        audit.close()
    except Exception as exc:
        errors.append(f"{page}: HTML parser error: {exc}")
    audits[page] = audit

    check(bool(re.search(r"<html\b[^>]*\blang=[\"'][^\"']+[\"']", source, re.I)),
          f"{page}: missing document language")
    check(bool(re.search(r"<title>\s*[^<]+\s*</title>", source, re.I)),
          f"{page}: missing/empty title")
    check(bool(audit.metas.get("viewport")), f"{page}: missing viewport metadata")
    check(bool(audit.metas.get("description")), f"{page}: missing meta description")
    check(bool(audit.metas.get("theme-color")), f"{page}: missing theme-color metadata")
    check(audit.main_landmarks == 1, f"{page}: expected one main#main-content landmark")
    check(audit.focusable_main, f"{page}: skip-link target should be programmatically focusable")
    check(audit.skip_links >= 1, f"{page}: missing skip link to main content")
    check("page-top" in audit.ids, f"{page}: missing top-of-page anchor")
    check(bool(re.search(r'class="footer-top-link" href="#page-top"', source)),
          f"{page}: footer back-to-top link does not reach the page top")
    check(audit.labelled_navs >= 1, f"{page}: missing labelled navigation")
    check(audit.h1_count == 1, f"{page}: expected exactly one h1")
    check(len(audit.ids) == len(set(audit.ids)),
          f"{page}: duplicate id attribute(s) found")
    check("favicon.svg" in source, f"{page}: missing custom favicon")
    check("styles.css" in source, f"{page}: missing stylesheet")
    check("script.js" in source, f"{page}: missing shared interaction script")
    check(bool(audit.metas.get("og:title")), f"{page}: missing Open Graph title")
    check(bool(audit.metas.get("og:description")),
          f"{page}: missing Open Graph description")
    check(audit.metas.get("twitter:card") == "summary_large_image",
          f"{page}: missing large-image social card metadata")
    for image in audit.images:
        check(bool(image.get("alt", "").strip()),
              f"{page}: image missing meaningful alt text")
    for script_text in audit.json_scripts:
        try:
            json.loads(script_text)
        except json.JSONDecodeError as exc:
            errors.append(f"{page}: invalid JSON-LD: {exc}")

# Validate local files and fragment targets across every page.
for page, audit in audits.items():
    for tag, attribute, value in audit.references:
        if value.startswith("//"):
            continue
        if value.startswith("#"):
            if len(value) > 1:
                check(value[1:] in audit.ids, f"{page}: missing same-page anchor {value}")
            continue
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc:
            if parsed.scheme.lower() == "javascript":
                errors.append(f"{page}: javascript: URL found")
            continue
        path = parsed.path
        fragment = parsed.fragment
        if not path:
            if fragment:
                check(fragment in audit.ids, f"{page}: missing same-page anchor #{fragment}")
            continue
        target_path = (ROOT / path).resolve()
        try:
            target_path.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"{page}: local reference escapes repository: {value}")
            continue
        check(target_path.is_file(), f"{page}: broken local {attribute} reference: {value}")
        if fragment and path in audits:
            check(fragment in audits[path].ids,
                  f"{page}: broken cross-page anchor: {value}")

# Public pricing must stay private in all public page text and the current README.
price_pattern = re.compile(r"\bR\s?\d[\d, ]*(?:\.\d{2})?\b", re.I)
for page, audit in audits.items():
    visible_text = " ".join(audit.visible_text)
    check(not price_pattern.search(visible_text),
          f"{page}: possible public price figure found")
check(not price_pattern.search(sources.get("README.md", "")),
      "README.md: possible public price figure found")
for public_doc in ("data/business.json", "THABZ_WEBSITE_SPEC.md", "ROSCORE_PROJECT_MANIFEST.md"):
    check(not price_pattern.search(sources.get(public_doc, "")),
          f"{public_doc}: possible public price or internal budget figure found")
try:
    json.loads(sources.get("data/business.json", ""))
except json.JSONDecodeError as exc:
    errors.append(f"data/business.json: invalid JSON: {exc}")

index = sources.get("index.html", "")
css = sources.get("styles.css", "")
js = sources.get("script.js", "")
readme = sources.get("README.md", "")
agents = sources.get("AGENTS.md", "").lower()
gates = sources.get("docs/QUALITY-GATES.md", "")

check("wa.me/" in index and "data-event=" in index,
      "Homepage missing WhatsApp conversion links/events")
check("data-current-year" in index and "new Date().getFullYear()" in js,
      "Footer copyright year is not updated automatically")
check("tel:" in index, "Homepage missing telephone conversion link")
check("prefers-reduced-motion" in css, "Reduced-motion fallback missing")
check("#d8f66a" not in css.lower() and "#d8f66a" not in sources.get("favicon.svg", "").lower(),
      "Legacy neon-lime accent remains outside the harmonised sage palette")
check(":focus-visible" in css, "Visible keyboard focus missing")
check(re.search(r"@media\s*\([^)]*max-width", css) is not None,
      "No narrow-screen breakpoint")
check("innerHTML" not in js, "Review potentially unsafe innerHTML usage")
check("IntersectionObserver" in js, "Scroll reveal does not use IntersectionObserver")
check("aria-expanded" in js and "aria-expanded" in index,
      "Mobile navigation is missing an accessible expanded state")
check("has-mobile-menu" in js and ".site-header:not(.has-mobile-menu) nav" in css,
      "mobile navigation must remain available without JavaScript")
check('targetId === "#main-content"' in js and "target.focus({ preventScroll: true })" in js,
      "Skip navigation does not programmatically focus main content")
check("floatingSuppressed = floatingVisibleTargets.size > 0" in js,
      "Floating WhatsApp CTA can obscure the contact area or footer")
check('fetchpriority="high"' in index and "srcset=" in index and "sizes=" in index,
      "Hero image is missing priority/responsive source attributes")
check("images.pexels.com" in index and "Pexels" in readme,
      "Hero stock image source/credit is not documented")
check("the only working branch" in agents and "do not create feature branches" in agents,
      "AGENTS.md is missing the main-only branch rule")
check("python3 tests/check_site.py" in readme or "python3 tests/check_site.py" in gates,
      "No documented command for running quality checks")
workflow = sources.get(".github/workflows/site-quality.yml", "")
check('branches: ["main"]' in workflow and "pull_request:" not in workflow,
      "Site quality workflow should run on main only")

print("Thabz multi-page static quality checks")
print(f"Pages audited: {len(audits)}")
print(f"Errors: {len(errors)}")
for error in errors:
    print(f"FAIL: {error}")
if errors:
    sys.exit(1)
print("PASS: all static checks passed")
