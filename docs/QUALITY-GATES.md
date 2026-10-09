# Thabz Website Quality Gates

Run from repository root: python3 tests/check_site.py

The dependency-free check validates metadata, landmarks, skip navigation, reduced motion, focus visibility, conversion links, public-price privacy, local asset references, and basic responsive/accessibility signals.

Static checks are not a browser audit. Before launch test:
- 320px, 375px, 768px, 1024px, and desktop widths.
- Keyboard-only navigation and a screen-reader smoke test.
- Chrome, Firefox, Safari/iOS, and Edge where available.
- WhatsApp and telephone links on a real phone.
- Production URL, HTTPS, canonical/OG URL, and GitHub Pages path behaviour.