"use strict";

const viewport = document.getElementById("site-viewport");
const menuLinks = [...viewport.querySelectorAll("nav a")];

function showSection() {
  const hash = window.location.hash || "#home";
  const target = document.getElementById(hash.slice(1));
  for (const link of menuLinks) {
    if (link.getAttribute("href") === hash) {
      link.setAttribute("aria-current", "location");
    } else {
      link.removeAttribute("aria-current");
    }
  }

  // Scroll the shared viewport explicitly inside standalone SVG documents.
  if (hash === "#home") {
    viewport.scrollTop = 0;
  } else if (target) {
    const offset = target.getBoundingClientRect().top - viewport.getBoundingClientRect().top;
    viewport.scrollTop += offset;
  }
}

window.addEventListener("hashchange", showSection);
showSection();
