(() => {
  "use strict";

  const reducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const header = document.querySelector(".site-header, body > header");
  const nav = header && header.querySelector("nav");
  const menuToggle = header && header.querySelector(".menu-toggle");

  const progress = document.createElement("div");
  progress.className = "scroll-progress";
  progress.setAttribute("aria-hidden", "true");
  document.body.appendChild(progress);

  function updateScrollUI() {
    const scrollTop = window.scrollY || document.documentElement.scrollTop || 0;
    const scrollable = document.documentElement.scrollHeight - window.innerHeight;
    const percentage = scrollable > 0 ? Math.min(1, Math.max(0, scrollTop / scrollable)) : 0;
    progress.style.transform = "scaleX(" + percentage + ")";
    if (header) header.classList.toggle("is-scrolled", scrollTop > 12);
    const floating = document.querySelector(".floating-whatsapp");
    if (floating) floating.classList.toggle("is-visible", scrollTop > 240);
  }
  window.addEventListener("scroll", updateScrollUI, { passive: true });
  window.addEventListener("resize", updateScrollUI, { passive: true });

  if (header && nav && menuToggle) {
    if (!nav.id) nav.id = "primary-navigation";
    menuToggle.setAttribute("aria-controls", nav.id);
    const closeMenu = () => {
      header.classList.remove("is-menu-open");
      menuToggle.setAttribute("aria-expanded", "false");
      menuToggle.setAttribute("aria-label", "Open navigation menu");
    };
    menuToggle.addEventListener("click", () => {
      const open = !header.classList.contains("is-menu-open");
      header.classList.toggle("is-menu-open", open);
      menuToggle.setAttribute("aria-expanded", String(open));
      menuToggle.setAttribute("aria-label", open ? "Close navigation menu" : "Open navigation menu");
    });
    nav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", closeMenu);
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeMenu();
        menuToggle.focus();
      }
    });
    document.addEventListener("click", (event) => {
      if (header.classList.contains("is-menu-open") && !header.contains(event.target)) closeMenu();
    });
  }

  const chat = document.createElement("a");
  chat.className = "floating-whatsapp";
  chat.href = "https://wa.me/27715752579?text=Hi%20Thabz%2C%20I%27d%20like%20to%20enquire%20about%20driving%20options.";
  chat.setAttribute("aria-label", "Message Thabz Driving School on WhatsApp");
  chat.innerHTML = '<span class="chat-dot" aria-hidden="true"></span><span>Message Thabz</span><span aria-hidden="true">↗</span>';
  chat.dataset.event = "WHATSAPP_CLICK";
  document.body.appendChild(chat);

  document.querySelectorAll("[data-event]").forEach((element) => {
    element.addEventListener("click", () => {
      const eventName = element.dataset.event;
      if (typeof window.gtag === "function") window.gtag("event", eventName);
      if (typeof window.plausible === "function") window.plausible(eventName);
      window.dispatchEvent(new CustomEvent("roscore:event", { detail: { name: eventName, href: element.href || null } }));
    });
  });

  if (!reducedMotion && "IntersectionObserver" in window) {
    const revealTargets = document.querySelectorAll(
      ".hero-copy, .hero-visual, .approach-intro, .approach-step, .section-heading, .training-card, .package-card, .extras-panel, .faq-item, .contact-inner, .service-detail-card, .inner-hero-copy, .inner-hero-art, .contact-page-copy, .contact-direct-card, .message-guide-grid article, .service-close, .contact-bottom-cta"
    );
    document.body.classList.add("motion-ready");
    revealTargets.forEach((element, index) => {
      element.setAttribute("data-reveal", "");
      element.style.setProperty("--reveal-delay", (index % 3) * 70 + "ms");
    });
    const observer = new IntersectionObserver((entries, instance) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          instance.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -48px 0px", threshold: 0.08 });
    revealTargets.forEach((element) => observer.observe(element));
  }

  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener("click", (event) => {
      const targetId = link.getAttribute("href");
      if (!targetId || targetId === "#") return;
      const target = document.querySelector(targetId);
      if (target) {
        event.preventDefault();
        target.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "start" });
        if (window.history && window.history.replaceState) window.history.replaceState(null, "", targetId);
      }
    });
  });

  updateScrollUI();
})();