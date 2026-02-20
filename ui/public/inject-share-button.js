(function () {
  function ensureButton() {
    if (document.getElementById("vataShareBtn")) return;

    const btn = document.createElement("button");
    btn.id = "vataShareBtn";
    btn.textContent = "Share this verification";
    btn.style.position = "fixed";
    btn.style.right = "16px";
    btn.style.bottom = "16px";
    btn.style.zIndex = "99999";
    btn.style.padding = "10px 14px";
    btn.style.borderRadius = "12px";
    btn.style.border = "1px solid rgba(255,255,255,0.25)";
    btn.style.background = "#111";
    btn.style.color = "#fff";
    btn.style.cursor = "pointer";
    btn.style.fontFamily = "system-ui, -apple-system, Segoe UI, Roboto, sans-serif";
    btn.style.boxShadow = "0 8px 30px rgba(0,0,0,0.35)";

    btn.onclick = async () => {
      try {
        const batchDir = window.__VATA_BATCHDIR__ || window.vataInferBatchDir();
        if (!batchDir) throw new Error("BatchDir not found. Click 'Use latest' or paste BatchDir, then run Verify.");

        // Best-effort parse from page text (your UI prints these already)
        const t = document.body.innerText;

        const arbVerifier = (t.match(/ARB_VERIFIER\s*([0-9a-fx]{42})/i) || [])[1] || "";
        const opVerifier  = (t.match(/OP_VERIFIER\s*([0-9a-fx]{42})/i) || [])[1] || "";

        const arbPass = /=== VERIFY \(ARB\) ===[\s\S]*?PASS/i.test(t) && /=== VERIFY \(OP\) ===/i.test(t) ? true : (/=== VERIFY \(ARB\) ===[\s\S]*?PASS/i.test(t));
        const opPass  = /=== VERIFY \(OP\) ===[\s\S]*?PASS/i.test(t);

        const arbCmdMatch = t.match(/=== VERIFY \(ARB\) ===[\s\S]*?RUN:\s*(.+)\r?\n/i);
        const opCmdMatch  = t.match(/=== VERIFY \(OP\) ===[\s\S]*?RUN:\s*(.+)\r?\n/i);
        const arbCommand = arbCmdMatch ? arbCmdMatch[1].trim() : "";
        const opCommand  = opCmdMatch ? opCmdMatch[1].trim() : "";

        const publicSignalMatch = t.match(/PUBLIC\s*=\s*(.+public\.json)/i);
        const publicSignal = publicSignalMatch ? publicSignalMatch[1].trim() : "";

        const payload = {
          batchDir,
          arbVerifier,
          opVerifier,
          arbRpc: "https://sepolia-rollup.arbitrum.io/rpc",
          opRpc: "https://sepolia.optimism.io",
          arbResult: arbPass,
          opResult: opPass,
          arbCommand,
          opCommand,
          publicSignal
        };

        const out = await window.vataShareReceipt(payload);
        alert(out.copied
          ? "Receipt copied to clipboard ✅ (and saved to VERIFICATION_RECEIPT.md)"
          : "Receipt generated ✅ (saved to VERIFICATION_RECEIPT.md)");
      } catch (e) {
        alert("Share failed: " + (e?.message || e));
      }
    };

    document.body.appendChild(btn);
  }

  ensureButton();
  setInterval(ensureButton, 1200);
})();
