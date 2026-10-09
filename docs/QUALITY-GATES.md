# Thabz Website Quality Gates

Run from the repository root:

```sh
python3 tests/check_site.py
```

The dependency-free checks cover all public HTML pages, not just the homepage. They validate document metadata, landmarks, skip navigation, unique IDs, internal file/anchor references, image alt text, external-link safety, reduced-motion and focus support, mobile navigation, responsive image markup, JSON-LD syntax, WhatsApp/telephone conversion paths, and price confidentiality.

Static checks are not a browser audit. Before launch:
- Check 320px, 360px, 375px, 390px, 768px, 1024px and wide desktop widths.
- Test keyboard-only navigation, reduced-motion mode and a screen-reader smoke test.
- Test Chrome, Firefox, Safari/iOS and Edge where available.
- Test WhatsApp and telephone links on an actual phone.
- Confirm GitHub Pages deployment and the public URL.
- Run Lighthouse and check Core Web Vitals on mobile and desktop. Target LCP ≤ 2.5s, INP ≤ 200ms and CLS ≤ 0.1 at the 75th percentile.
- Confirm no package prices or unapproved business claims appear in public HTML, repo docs or images.


CI runs on pushes to the single working branch, `main`, plus manual dispatch. This repository does not use feature branches or pull-request-based work for routine changes.
