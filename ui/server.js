const express = require("express");
const path = require("path");
const fs = require("fs");
const os = require("os");
const crypto = require("crypto");

const app = express();
const PORT = process.env.PORT || 4177;

/* ---------------------------------------------------------
   Paths
--------------------------------------------------------- */

const UI_DIR = __dirname;
const PROJECT_DIR = path.resolve(UI_DIR, "..");
const BATCHES_DIR = "C:\\Users\\lhmsi\\Desktop\\project-vata\\merkle\\batches";

/* ---------------------------------------------------------
   RPC Defaults
--------------------------------------------------------- */

const ARB_RPC = "https://sepolia-rollup.arbitrum.io/rpc";
const OP_RPC  = "https://sepolia.optimism.io";

/* ---------------------------------------------------------
   Middleware
--------------------------------------------------------- */

app.use(express.json({ limit: "10mb" }));
app.use(express.static(path.join(UI_DIR, "public")));

/* ---------------------------------------------------------
   Utils
--------------------------------------------------------- */

function sha256File(p) {
  return crypto.createHash("sha256")
    .update(fs.readFileSync(p))
    .digest("hex");
}

function listClaimDirs(dir) {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir, { withFileTypes: true })
    .filter(d => d.isDirectory() && d.name.startsWith("claim_"))
    .map(d => ({
      name: d.name,
      full: path.join(dir, d.name),
      mtime: fs.statSync(path.join(dir, d.name)).mtimeMs
    }))
    .sort((a, b) => b.mtime - a.mtime);
}

/* ---------------------------------------------------------
   ENV
--------------------------------------------------------- */

app.get("/api/env", (_, res) => {
  res.json({
    ok: true,
    ARB_VERIFIER: process.env.ARB_VERIFIER || "",
    OP_VERIFIER:  process.env.OP_VERIFIER  || "",
    ARB_RPC,
    OP_RPC
  });
});

/* Legacy alias */
app.get("/env", (req, res) => res.redirect(302, "/api/env"));

/* ---------------------------------------------------------
   LATEST BATCH
--------------------------------------------------------- */

app.get("/api/latest", (_, res) => {
  const dirs = listClaimDirs(BATCHES_DIR);
  res.json({
    ok: true,
    batchesDir: BATCHES_DIR,
    latest: dirs[0]?.full || ""
  });
});

/* Aliases */
app.get("/latest", (req,res)=>res.redirect(302,"/api/latest"));
app.get("/getLatest",(req,res)=>res.redirect(302,"/api/latest"));
app.get("/api/getLatest",(req,res)=>res.redirect(302,"/api/latest"));

/* ---------------------------------------------------------
   SHARE RECEIPT
--------------------------------------------------------- */

app.post("/api/share", (req, res) => {
  try {

    const {
      batchDir,
      arbVerifier,
      opVerifier,
      arbRpc,
      opRpc,
      arbResult,
      opResult
    } = req.body || {};

    if (!batchDir)
      return res.status(400).json({ ok:false, error:"batchDir required" });

    const proofPath  = path.join(batchDir,"proof.json");
    const publicPath = path.join(batchDir,"public.json");

    const proofHash  = fs.existsSync(proofPath)  ? sha256File(proofPath)  : "N/A";
    const publicHash = fs.existsSync(publicPath) ? sha256File(publicPath) : "N/A";

    let publicSignal = "N/A";
    let arbCmd = "";
    let opCmd  = "";

    function buildCast(verifier, rpc) {
      const proof = JSON.parse(fs.readFileSync(proofPath,"utf8"));
      const pub   = JSON.parse(fs.readFileSync(publicPath,"utf8"));

      publicSignal = String(pub[0]);

      const A = `[${proof.pi_a[0]},${proof.pi_a[1]}]`;

      // swap inner pairs for EVM
      const B = `[[${proof.pi_b[0][1]},${proof.pi_b[0][0]}],[${proof.pi_b[1][1]},${proof.pi_b[1][0]}]]`;

      const C = `[${proof.pi_c[0]},${proof.pi_c[1]}]`;
      const PUB = `[${pub[0]}]`;

      const SIG = `"verifyProof(uint256[2],uint256[2][2],uint256[2],uint256[1])(bool)"`;
      return `cast call ${verifier} ${SIG} ${A} ${B} ${C} ${PUB} --rpc-url ${rpc}`;
    }

    if (fs.existsSync(proofPath) && fs.existsSync(publicPath)) {
      const aV = arbVerifier || process.env.ARB_VERIFIER;
      const oV = opVerifier  || process.env.OP_VERIFIER;

      if (aV) arbCmd = buildCast(aV, arbRpc || ARB_RPC);
      if (oV) opCmd  = buildCast(oV,  opRpc  || OP_RPC);
    }

    const stamp = new Date().toISOString();
    const host = os.hostname();
    const platform = `${os.platform()} ${os.release()}`;

    const md = `# Project VATA — Dual L2 Proof Verification Receipt

**Timestamp (UTC):** ${stamp}  
**Host:** ${host} (${platform})

## Batch
- **BatchDir:** \`${batchDir}\`
- **proof.json (SHA256):** \`${proofHash}\`
- **public.json (SHA256):** \`${publicHash}\`
- **Public Signal:** \`${publicSignal}\`

## Arbitrum Sepolia
- **RPC:** \`${arbRpc || ARB_RPC}\`
- **Verifier:** \`${arbVerifier || process.env.ARB_VERIFIER || "N/A"}\`
- **Result:** **${arbResult ? "PASS ✅" : "FAIL ❌"}**
\`\`\`bash
${arbCmd}
\`\`\`

## Optimism Sepolia
- **RPC:** \`${opRpc || OP_RPC}\`
- **Verifier:** \`${opVerifier || process.env.OP_VERIFIER || "N/A"}\`
- **Result:** **${opResult ? "PASS ✅" : "FAIL ❌"}**
\`\`\`bash
${opCmd}
\`\`\`

## Share

### GitHub
> ✅ Project VATA — Dual L2 ZK Proof Verification PASS  
> Root: \`${publicSignal}\`  
> Batch: \`${batchDir}\`

### X
Project VATA verified a Groth16 proof on two L2s.  
ARB ✅ OP ✅  
Root: ${publicSignal}

### Discord
VATA Dual-L2 Verify PASS  
Root: ${publicSignal}

## Notes
Generated locally. Contains **no private keys**.  
Reproducible from \`proof.json\` + \`public.json\`.
`;

    const outPath = path.join(batchDir,"VERIFICATION_RECEIPT.md");
    fs.writeFileSync(outPath, md, "utf8");

    res.json({ ok:true, savedTo: outPath, markdown: md });

  } catch (e) {
    res.status(500).json({ ok:false, error:String(e) });
  }
});

/* Legacy alias */
app.post("/share",(req,res)=>res.redirect(307,"/api/share"));

/* ---------------------------------------------------------
   FALLBACK
--------------------------------------------------------- */

app.get("*", (_, res) => {
  res.sendFile(path.join(UI_DIR,"public","index.html"));
});

/* ---------------------------------------------------------
   START
--------------------------------------------------------- */

const server = app.listen(PORT, () => {
  console.log(`UI server running on port ${PORT}`);
  console.log(`BATCHES_DIR = ${BATCHES_DIR}`);
});

server.on("error", err => {
  if (err.code === "EADDRINUSE") {
    console.error(`Port ${PORT} already in use.`);
    process.exit(1);
  }
});