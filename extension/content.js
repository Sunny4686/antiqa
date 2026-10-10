// Runs on Blocket and Marketplace pages the owner opens himself. It never scrolls, clicks or loads anything:
// when the owner has scrolled to a new part of the page and stopped, it asks the extension to take one
// screenshot of what is already on screen, together with where the visible listing links are.

const SETTLE_MS = 700; // wait until scrolling has stopped
const MIN_MOVE = 0.5; // at least half a screen since the last capture
let lastY = null;
let timer = null;

function visibleLinks() {
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  const out = [];
  for (const a of document.querySelectorAll("a[href]")) {
    const r = a.getBoundingClientRect();
    if (r.width < 40 || r.height < 40 || r.bottom < 0 || r.top > vh || r.right < 0 || r.left > vw) continue;
    out.push({
      href: a.href,
      x0: Math.max(r.left / vw, 0),
      y0: Math.max(r.top / vh, 0),
      x1: Math.min(r.right / vw, 1),
      y1: Math.min(r.bottom / vh, 1),
    });
    if (out.length >= 400) break;
  }
  return out;
}

function maybeCapture() {
  const y = window.scrollY;
  if (lastY !== null && Math.abs(y - lastY) < window.innerHeight * MIN_MOVE) return;
  lastY = y;
  chrome.runtime.sendMessage({ type: "capture", pageUrl: location.href, links: visibleLinks() });
}

chrome.storage.local.get({ enabled: false }, ({ enabled }) => {
  if (!enabled) return;
  window.addEventListener(
    "scroll",
    () => {
      clearTimeout(timer);
      timer = setTimeout(maybeCapture, SETTLE_MS);
    },
    { passive: true }
  );
  setTimeout(maybeCapture, 1500); // the first screen after the page has loaded
});
