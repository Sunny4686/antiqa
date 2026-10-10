// Takes the screenshot the content script asked for and posts it to the owner's own Fyndjakt server.
// Requests go only to that server, never to Blocket or Facebook.

const MIN_GAP_MS = 1200; // Chrome allows about two captures per second; stay well below
let last = 0;

async function settings() {
  return chrome.storage.local.get({ enabled: false, server: "http://127.0.0.1:8000", token: "", sent: 0 });
}

chrome.runtime.onMessage.addListener((msg, sender) => {
  if (msg.type !== "capture" || !sender.tab) return;
  (async () => {
    const s = await settings();
    if (!s.enabled || !s.token) return;
    const now = Date.now();
    if (now - last < MIN_GAP_MS) return;
    last = now;
    const dataUrl = await chrome.tabs.captureVisibleTab(sender.tab.windowId, { format: "jpeg", quality: 85 });
    const blob = await (await fetch(dataUrl)).blob();
    const form = new FormData();
    form.append("image", blob, "screen.jpg");
    form.append("page_url", msg.pageUrl);
    form.append("links", JSON.stringify(msg.links));
    const r = await fetch(`${s.server.replace(/\/$/, "")}/ingest/screenshot`, {
      method: "POST",
      headers: { Authorization: `Bearer ${s.token}` },
      body: form,
    });
    if (r.ok) {
      const sent = s.sent + 1;
      await chrome.storage.local.set({ sent });
      chrome.action.setBadgeText({ text: String(sent) });
      chrome.action.setBadgeBackgroundColor({ color: "#b8460b" });
    } else {
      chrome.action.setBadgeText({ text: "!" });
    }
  })().catch(() => chrome.action.setBadgeText({ text: "!" }));
});
