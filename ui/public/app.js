const out = document.getElementById("out");
const batchDirEl = document.getElementById("batchDir");
const arbEnv = document.getElementById("arbEnv");
const opEnv = document.getElementById("opEnv");

function log(msg) { out.textContent = msg; }

async function getJSON(url, opts) {
  const r = await fetch(url, opts);
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.error || `HTTP ${r.status}`);
  return j;
}

document.getElementById("btnEnv").onclick = async () => {
  try {
    log("Loading env...");
    const j = await getJSON("/api/env");
    arbEnv.textContent = j.ARB_VERIFIER || "(unset)";
    opEnv.textContent = j.OP_VERIFIER || "(unset)";
    log("Env loaded.");
  } catch (e) {
    log(String(e));
  }
};

document.getElementById("btnLatest").onclick = async () => {
  try {
    log("Finding latest batch...");
    const j = await getJSON("/api/latest-batch");
    batchDirEl.value = j.batchDir;
    log(`Latest batch set:\n${j.batchDir}`);
  } catch (e) {
    log(String(e));
  }
};

async function verify(net) {
  const batchDir = batchDirEl.value.trim();
  if (!batchDir) return log("Paste a BatchDir or click “Use latest claim_*” first.");

  try {
    log(`Running verification (${net})...`);
    const j = await getJSON("/api/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ net, batchDir })
    });
    log(j.output || "(no output)");
  } catch (e) {
    log(`ERROR: ${String(e)}`);
  }
}

document.getElementById("btnAll").onclick = () => verify("all");
document.getElementById("btnArb").onclick = () => verify("arb");
document.getElementById("btnOp").onclick = () => verify("op");