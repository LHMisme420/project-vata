async function vataShareReceipt(payload) {
  const r = await fetch("/share", { // legacy alias supported
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const j = await r.json();
  if (!j.ok) throw new Error(j.error || "share failed");
  if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(j.markdown);
  return j;
}
window.vataShareReceipt = vataShareReceipt;
