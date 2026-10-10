const $ = (id) => document.getElementById(id);

chrome.storage.local.get({ enabled: false, server: "http://127.0.0.1:8000", token: "", sent: 0, lastError: "" }, (s) => {
  $("err").textContent = s.lastError ? `Senaste fel: ${s.lastError}` : "";
  $("enabled").checked = s.enabled;
  $("server").value = s.server;
  $("token").value = s.token;
  $("sent").textContent = s.sent;
});

$("save").onclick = async () => {
  const server = $("server").value.trim();
  if ($("enabled").checked) {
    // Chrome only lets an extension screenshot a tab with this permission; asked once, on this click.
    const ok = await chrome.permissions.request({ origins: ["<all_urls>"] });
    if (!ok) {
      $("err").textContent = "Utan behörigheten kan tillägget inte läsa av skärmen.";
      return;
    }
  }
  if (server.startsWith("https://")) {
    // A remote server (e.g. behind Cloudflare) needs the owner's consent to that host.
    await chrome.permissions.request({ origins: [new URL(server).origin + "/*"] });
  }
  await chrome.storage.local.set({ enabled: $("enabled").checked, server, token: $("token").value.trim() });
  window.close();
};

$("reset").onclick = async () => {
  await chrome.storage.local.set({ sent: 0 });
  chrome.action.setBadgeText({ text: "" });
  $("sent").textContent = "0";
};
