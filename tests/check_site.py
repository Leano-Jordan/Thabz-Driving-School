#!/usr/bin/env python3
"""Dependency-free static quality checks for the Thabz site."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

def read(path):
    file = ROOT / path
    if not file.is_file():
        errors.append(f"Missing required file: {path}")
        return ""
    return file.read_text(encoding="utf-8")

html = read("index.html")
css = read("styles.css")
js = read("script.js")
read("README.md")

def check(condition, message):
    if not condition:
        errors.append(message)

check(bool(re.search(r"<title>\s*[^<]+</title>", html, re.I)), "Missing/empty title")
check(bool(re.search(r'<meta\s+name="description"\s+content="[^"]+"', html, re.I)), "Missing meta description")
check(bool(re.search(r"<main\b[^>]*id=\"main-content\"", html, re.I)), "Missing main landmark / skip target")
check('href="#main-content"' in html, "Missing skip link")
check('aria-label="Main navigation"' in html, "Main navigation is not labelled")
check("prefers-reduced-motion" in css, "Reduced-motion fallback missing")
check(":focus-visible" in css, "Visible keyboard focus missing")
check("wa.me/" in html and "data-event=" in html, "WhatsApp conversion links missing")
check("tel:" in html, "Phone conversion link missing")

public_text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", html, flags=re.I | re.S)
public_text = re.sub(r"<[^>]+>", " ", public_text)
public_text = re.sub(r"&(?:amp|nbsp|quot|apos|lt|gt);", " ", public_text, flags=re.I)
check(not re.search(r"R\s?\d[\d,]*(?:\.\d{2})?", public_text, re.I), "Possible public price found in homepage")

for attr, value in re.findall(r'\b(src|href)="([^"]+)"', html, re.I):
    if value.startswith(("#", "https://", "http://", "tel:", "mailto:", "data:")):
        continue
    path = value.split("?", 1)[0].split("#", 1)[0]
    if path and not (ROOT / path).exists():
        errors.append(f"Broken local {attr} reference: {value}")

check(len(re.findall(r"<h1\b", html, re.I)) == 1, "Expected exactly one h1")
check(bool(re.search(r'<img\b[^>]*\balt="[^"]+"', html, re.I)), "Image missing alt text")
check(bool(re.search(r"@media\s*\([^)]*max-width", css)), "No narrow-screen breakpoint")
check("innerHTML" not in js, "Review potentially unsafe innerHTML usage")

print("Thabz static quality checks")
print(f"Errors: {len(errors)}")
for error in errors:
    print(f"FAIL: {error}")
if errors:
    sys.exit(1)
print("PASS: all static checks passed")
