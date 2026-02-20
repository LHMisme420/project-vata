const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const os = require("os");

function sha256File(filePath) {
  const buf = fs.readFileSync(filePath);
  return crypto.createHash("sha256").update(buf).digest("hex");
}

module.exports = function registerShareRoute(app) {
  app.post("/api/share", (req, res) => {
    try {
      const {
        batchDir,
        arbVerifier,
        opVerifier,
        arbRpc,
        opRpc,
        arbResult,
        opResult,
        arbCommand,
        opCommand,
        publicSignal
      } = req.body || {};

      if (!batchDir) return res.status(400).json({ ok: false, error: "batchDir is required" });

      const proofPath = path.join(batchDir, "proof.json");
      const publicPath = path.join(batchDir, "public.json");

      const proofHash = fs.existsSync(proofPath) ? sha256File(proofPath) : null;
      const publicHash = fs.existsSync(publicPath) ? sha256File(publicPath) : null;

      const stamp = new Date().toISOString();
      const host = os.hostname();
      const platform = `${os.platform()} ${os.release()}`;

      const md = `# Project VATA — Dual L2 Proof Verification Receipt

**Timestamp (UTC):** ${stamp}  
**Host:** ${host} (${platform})  

## Batch
- **BatchDir:** \`${batchDir}\`
- **proof.json (SHA256):** \`${proofHash ?? "N/A"}\`
- **public.json (SHA256):** \`${publicHash ?? "N/A"}\`
- **Public Signal:** \`${publicSignal ?? "N/A"}\`

## Networks
### Arbitrum Sepolia
- **RPC:** \`${arbRpc ?? "N/A"}\`
- **Verifier:** \`${arbVerifier ?? "N/A"}\`
- **Result:** **${arbResult ? "PASS ✅" : "FAIL ❌"}**
- **Repro command:**
\`\`\`bash
${arbCommand ?? "N/A"}
\`\`\`

### Optimism Sepolia
- **RPC:** \`${opRpc ?? "N/A"}\`
- **Verifier:** \`${opVerifier ?? "N/A"}\`
- **Result:** **${opResult ? "PASS ✅" : "FAIL ❌"}**
- **Repro command:**
\`\`\`bash
${opCommand ?? "N/A"}
\`\`\`

## Notes
Generated locally. Contains **no private keys**. Reproducible using batch artifacts (\`proof.json\`, \`public.json\`) and verifier contracts above.
`;

      const outPath = path.join(batchDir, "VERIFICATION_RECEIPT.md");
      try { fs.writeFileSync(outPath, md, "utf8"); } catch (_) {}

      return res.json({ ok: true, markdown: md, savedTo: outPath });
    } catch (e) {
      return res.status(500).json({ ok: false, error: String(e?.message || e) });
    }
  });
}
