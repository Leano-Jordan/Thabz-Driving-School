# Thabz Driving School — commercial website

A mobile-first static website for Thabz Driving School, designed around a distinctive editorial identity, clear training pathways and direct WhatsApp enquiries.

## Customer journey
- Start with a clear brand statement and an illustrative driving lesson photo.
- Explore the approach and the learner, driving licence, Code 8/10, Code 14, PDP and lesson options.
- Message or call Thabz to confirm availability, current package inclusions and an accurate quote.
- No package prices are published on the website.

## Business details
- Phone / WhatsApp: 071 575 2579
- WhatsApp international format: +27 71 575 2579
- The supplied price-list details are intentionally not reproduced in this public-facing README or website copy. The owner should confirm any current quote and package inclusions directly with prospective customers.

## Hero photography
- The temporary illustrative hero image is by Ron Lach on Pexels: https://www.pexels.com/photo/man-in-white-and-black-striped-dress-shirt-driving-car-9518029/
- Pexels lists the image as free to use. It depicts a Black adult sitting beside a young learner during a practice drive; it is not a photograph of Thabz or a verified member of the business.
- Replace this stock image with owner-approved photography before claiming it shows the actual instructor or vehicle.

## Site experience
- Pages: `index.html`, `services.html`, `contact.html`, and `404.html`.
- Static HTML, CSS and vanilla JavaScript; no booking backend, database or framework.
- Responsive layouts, accessible mobile navigation, skip link, visible focus styles, native accessible FAQ disclosures and reduced-motion support.
- Motion includes a continuous editorial ticker, scroll reveals, subtle hover feedback, a route motif and scroll progress.
- Main conversion path: WhatsApp and telephone.
- SEO metadata and basic structured business data are included. No unverified address, reviews, pass rates, opening hours, instructor credentials or service guarantees are invented.

## Development workflow
- The single working branch is `main`. All site work and commits happen directly on `main`; do not create working branches or pull requests.
- Run `python3 tests/check_site.py` before committing site changes.
- Detailed working rules are in `AGENTS.md`; quality-gate details are in `docs/QUALITY-GATES.md`.

## Before launch
1. Test the published site on a real phone and in Chrome, Edge and Firefox.
2. Run Lighthouse and field performance checks. Aim for Core Web Vitals in the good range.
3. Confirm the business's actual service area, current contact details, package inclusions and any applicable application/testing fees with the owner.
4. Add genuine testimonials or business-owned photography only after receiving approval.
5. Review repository visibility and older Git history if any previously committed pricing must remain confidential. Removing amounts from current files does not erase previous public commits.

## Deployment
GitHub Pages workflow: `.github/workflows/deploy-pages.yml`.
