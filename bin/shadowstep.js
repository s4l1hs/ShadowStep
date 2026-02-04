#!/usr/bin/env node

const { spawnSync } = require("child_process");

const args = process.argv.slice(2);
const candidates = [];

if (process.env.SHADOWSTEP_PYTHON) {
  candidates.push(process.env.SHADOWSTEP_PYTHON);
}

candidates.push("python3", "python", "py");

function runPython(cmd) {
  const baseArgs = cmd === "py" ? ["-3", "-m", "shadowstep"] : ["-m", "shadowstep"];
  const result = spawnSync(cmd, [...baseArgs, ...args], { stdio: "inherit" });

  if (result.error && result.error.code === "ENOENT") {
    return false;
  }

  if (typeof result.status === "number") {
    process.exit(result.status);
  }

  return true;
}

for (const cmd of candidates) {
  const handled = runPython(cmd);
  if (handled) {
    process.exit(1);
  }
}

console.error("[shadowstep] Python bulunamadı. Python 3 kurun veya SHADOWSTEP_PYTHON değişkenini ayarlayın.");
process.exit(1);
