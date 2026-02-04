#!/usr/bin/env node

const { spawnSync } = require("child_process");
const path = require("path");

const pkg = require(path.join(__dirname, "..", "package.json"));
const version = pkg.version || "";
const packageSpec = version ? `shadowstep==${version}` : "shadowstep";
const candidates = [];

if (process.env.SHADOWSTEP_PYTHON) {
  candidates.push(process.env.SHADOWSTEP_PYTHON);
}

candidates.push("python3", "python", "py");

function installWith(cmd, spec) {
  const baseArgs = cmd === "py" ? ["-3", "-m", "pip", "install", spec] : ["-m", "pip", "install", spec];
  const result = spawnSync(cmd, baseArgs, { stdio: "inherit" });

  if (result.error && result.error.code === "ENOENT") {
    return false;
  }

  if (typeof result.status === "number" && result.status === 0) {
    return true;
  }

  return false;
}

let installed = false;

for (const cmd of candidates) {
  installed = installWith(cmd, packageSpec);
  if (installed) {
    break;
  }
}

if (!installed && packageSpec !== "shadowstep") {
  for (const cmd of candidates) {
    installed = installWith(cmd, "shadowstep");
    if (installed) {
      break;
    }
  }
}

if (!installed) {
  console.warn("[shadowstep] Python pip kurulumu başarısız. Lütfen manuel olarak: python -m pip install shadowstep");
}
