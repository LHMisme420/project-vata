const express = require("express");
const path = require("path");
const { spawn } = require("child_process");

const app = express();
app.use(express.json({ limit: "1mb" }));

app.use("/", express.static(path.join(__dirname, "public")));

const REPO_ROOT = path.resolve(__dirname, "..");

function runPwsh(args, { cwd = REPO_ROOT } = {}) {
  return new Promise((resolve) => {
    const candidates = ["pwsh", "powershell"];
    let idx = 0;

    function trySpawn() {
      const exe = candidates[idx++];
      const ps = spawn(exe, args, { cwd, windowsHide: true });

      let out = "";
      let err = "";

      ps.stdout.on("data", (d) => (out += d.toString()));
      ps.stderr.on("data", (d) => (err += d.toString()));

      ps.on("error", (e) => {
        if (idx < candidates.length) return trySpawn();
        resolve({ code: 1, stdout: out, stderr: err + "\n" + e.toString() });
      });

      ps.on("close", (code) => resolve({ code, stdout: out, stderr: err }));
    }

    trySpawn();
  });
}

app.get("/api/env", (_req, res) => {
  res.json({
    ARB_VERIFIER: process.env.ARB_VERIFIER || "",
    OP_VERIFIER: process.env.OP_VERIFIER || ""
  });
});

app.get("/api/latest-batch", async (_req, res) => {
  const cmd = `
    $root = Join-Path (Resolve-Path ".").Path "merkle\\batches"
    if (-not (Test-Path $root)) { throw "Missing merkle\\batches folder at: $root" }
    $b = (Get-ChildItem -LiteralPath $root -Directory -Filter "claim_*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
    $b
  `;
  const r = await runPwsh(["-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd]);
  if (r.code !== 0) return res.status(500).json({ ok: false, error: r.stderr || r.stdout });
  res.json({ ok: true, batchDir: r.stdout.trim() });
});

app.post("/api/verify", async (req, res) => {
  const { net, batchDir } = req.body || {};
  if (!batchDir || typeof batchDir !== "string") {
    return res.status(400).json({ ok: false, error: "batchDir required" });
  }

  let scriptRel, scriptArgs;
  if (net === "arb") {
    scriptRel = "scripts\\l2_verify_proof.ps1";
    scriptArgs = ["-Net", "arb", "-BatchDir", batchDir];
  } else if (net === "op") {
    scriptRel = "scripts\\l2_verify_proof.ps1";
    scriptArgs = ["-Net", "op", "-BatchDir", batchDir];
  } else {
    scriptRel = "scripts\\l2_verify_all.ps1";
    scriptArgs = ["-BatchDir", batchDir];
  }

  const scriptAbs = path.join(REPO_ROOT, scriptRel);
  const args = ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", scriptAbs, ...scriptArgs];

  const r = await runPwsh(args);
  const combined = [
    `# Running: ${scriptRel} ${scriptArgs.join(" ")}`,
    "",
    r.stdout.trim(),
    r.stderr.trim() ? "\n# STDERR\n" + r.stderr.trim() : ""
  ].join("\n");

  res.json({ ok: r.code === 0, code: r.code, output: combined });
});

const PORT = process.env.PORT || 4177;
app.listen(PORT, () => console.log(`VATA UI running on http://127.0.0.1:${PORT}`));