import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, it } from "node:test";
import { spawnSync } from "node:child_process";

const ROOT = process.cwd();
const HTML_PATH = join(ROOT, "growth_model.html");
const APP_PATH = join(ROOT, "src", "app.js");

describe("frontend structure", () => {
  it("loads frontend logic from module script instead of inline block", () => {
    const html = readFileSync(HTML_PATH, "utf8");

    assert.match(html, /<script\s+src="\.\/*model\/growth_model\.data\.js"><\/script>/);
    assert.match(html, /<script\s+type="module"\s+src="\.\/*src\/app\.js"><\/script>/);

    const scriptTagCount = (html.match(/<script/g) || []).length;
    assert.equal(scriptTagCount, 2);
    assert.doesNotMatch(html, /<script>\s*const data = window\.GROWTH_MODEL_DATA;/);
  });

  it("keeps extracted app module syntactically valid", () => {
    const result = spawnSync("node", ["--check", APP_PATH], {
      cwd: ROOT,
      encoding: "utf8",
    });

    assert.equal(result.status, 0, `node --check failed: ${result.stderr}`);
  });
});
