import assert from "node:assert/strict";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { test } from "node:test";

function files(dir: URL): URL[] {
  return readdirSync(dir).flatMap((name) => {
    const url = new URL(name, dir);
    return statSync(url).isDirectory() ? files(new URL(`${name}/`, dir)) : /\.tsx?$/.test(name) ? [url] : [];
  });
}
const src = new URL("../src/", import.meta.url);
const UI = files(src).filter((f) => !/\/(lib|content)\//.test(f.pathname) || /science-copy/.test(f.pathname));

/** Brief section 11, Honesty: no biological unit on model output, and no "verified" on a result in the interface text. */
test("no bare mV on model output in interface sources", () => {
  for (const file of UI) {
    if (/science-copy/.test(file.pathname)) continue;
    const text = readFileSync(file, "utf8");
    assert.doesNotMatch(text, /["'>\s]mV["'<\s.,)]/, `${file.pathname.split("/src/")[1]} shows a bare mV`);
  }
});

test("interface text says integrity-checked, not verified, apart from internal names", () => {
  for (const file of UI) {
    if (/science-copy/.test(file.pathname)) continue; // holds the list of retired words
    const text = readFileSync(file, "utf8");
    // Visible strings: quoted or JSX text that begins with or contains the word as a capitalised label.
    const hits = text.match(/(>|["'`])[^"'`<>\n]*\b[Vv]erified\b[^"'`<>\n]*/g) ?? [];
    const visible = hits.filter((h) => !/_verified|verified\.|\(verified|const verified|verified\)|verified =|Verified\s*:\s*(true|false)/.test(h) && !/'verified/.test(h) && !/RETIRED|term:/.test(h));
    assert.deepEqual(visible, [], `${file.pathname.split("/src/")[1]}: ${visible.join(" | ")}`);
  }
});
