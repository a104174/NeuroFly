import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync, existsSync } from "node:fs";
import { inflateSync } from "node:zlib";
import { createHash } from "node:crypto";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { BrandLogo } from "../src/components/site/BrandLogo";
import { AppHeader } from "../src/components/AppHeader";
import { SiteHeader, SiteFooter } from "../src/components/site/SiteChrome";

/** Standard PNG scanline reconstruction; checks actual pixels without an image dependency. */
function rgba(bytes: Buffer) {
  assert.equal(bytes.subarray(1, 4).toString(), "PNG");
  const width = bytes.readUInt32BE(16), height = bytes.readUInt32BE(20);
  assert.equal(bytes[24], 8); assert.equal(bytes[25], 6); assert.equal(bytes[28], 0);
  const chunks: Buffer[] = [];
  for (let offset = 8; offset < bytes.length;) {
    const length = bytes.readUInt32BE(offset), kind = bytes.toString("ascii", offset + 4, offset + 8);
    if (kind === "IDAT") chunks.push(bytes.subarray(offset + 8, offset + 8 + length));
    offset += length + 12;
  }
  const raw = inflateSync(Buffer.concat(chunks)), stride = width * 4, pixels = Buffer.alloc(stride * height);
  let offset = 0;
  for (let y = 0; y < height; y++) {
    const filter = raw[offset++]; assert(filter <= 4);
    for (let x = 0; x < stride; x++) {
      const left = x >= 4 ? pixels[y * stride + x - 4] : 0, up = y ? pixels[(y - 1) * stride + x] : 0, corner = y && x >= 4 ? pixels[(y - 1) * stride + x - 4] : 0;
      const estimate = left + up - corner, a = Math.abs(estimate - left), b = Math.abs(estimate - up), c = Math.abs(estimate - corner);
      const paeth = a <= b && a <= c ? left : b <= c ? up : corner;
      const predictor = [0, left, up, Math.floor((left + up) / 2), paeth][filter];
      pixels[y * stride + x] = (raw[offset++] + predictor) & 255;
    }
  }
  return { width, height, pixels };
}
const asset = new URL("../public/assets/brand/neurofly-logo-white.png", import.meta.url);

test("canonical artwork is white with genuine transparency, negative spaces and antialiased edges", () => {
  const data = readFileSync(asset), { width, height, pixels } = rgba(data);
  assert.equal(width, 512); assert.equal(height, 280); assert(data.length < 30_000);
  let clear = 0, opaque = 0, edge = 0;
  for (let i = 0; i < pixels.length; i += 4) {
    const alpha = pixels[i + 3];
    if (!alpha) clear++; else { assert.deepEqual([...pixels.subarray(i, i + 3)], [255, 255, 255]); if (alpha === 255) opaque++; else edge++; }
  }
  assert(clear > width * height / 2); assert(opaque > 1000); assert(edge > 100);
  for (const [x, y] of [[0, 0], [511, 0], [0, 279], [511, 279]]) assert.equal(pixels[(y * width + x) * 4 + 3], 0);
  let separatedRows = 0;
  for (let y = 0; y < height; y++) {
    let runs = 0, previous = false;
    for (let x = 0; x < width; x++) { const ink = pixels[(y * width + x) * 4 + 3] > 200; if (ink && !previous) runs++; previous = ink; }
    if (runs >= 3) separatedRows++;
  }
  assert(separatedRows > height / 10, "Internal negative spaces must separate the emblem's strokes");
});

test("shared logo renders the canonical asset in public header, footer and internal research navigation", () => {
  for (const component of [BrandLogo, AppHeader, SiteHeader, SiteFooter]) {
    const html = renderToStaticMarkup(createElement(component));
    assert.match(html, /src="\/assets\/brand\/neurofly-logo-white.png"/);
    assert.doesNotMatch(html, /src="[^\"]*neurofly-logo.png"|brand-mark|nf-brand-dot/);
  }
  const lab = readFileSync(new URL("../src/app/visual-lab/arena/page.tsx", import.meta.url), "utf8");
  assert.match(lab, /<BrandLogo \/>/);
  for (const route of ["scenarios", "experiments", "morphology", "visual-lab/fly", "visual-lab/arena/research"]) {
    assert.match(readFileSync(new URL(`../src/app/${route}/page.tsx`, import.meta.url), "utf8"), /AppHeader/);
  }
});

test("logo has no white backing or simulation side effects", () => {
  const css = readFileSync(new URL("../src/app/globals.css", import.meta.url), "utf8");
  const block = css.match(/\.neurofly-logo\s*\{([^}]+)\}/)?.[1]; assert(block);
  assert.doesNotMatch(block, /background|border-radius|filter/);
  const source = readFileSync(new URL("../src/components/site/BrandLogo.tsx", import.meta.url), "utf8");
  assert.doesNotMatch(source, /useEffect|fetch\(|requestAnimationFrame|from.*(?:three|lib\/)/);
});

test("PNG browser and Apple icons preserve transparent corners and ICO contains valid alpha frames", () => {
  assert(!existsSync(new URL("../src/app/icon.svg", import.meta.url)));
  for (const file of ["icon.png", "apple-icon.png"]) {
    const icon = rgba(readFileSync(new URL(`../src/app/${file}`, import.meta.url)));
    assert.equal(icon.width, icon.height); assert.equal(icon.pixels[3], 0);
    assert(icon.pixels.some((v, i) => i % 4 === 3 && v === 255));
  }
  const ico = readFileSync(new URL("../src/app/favicon.ico", import.meta.url));
  assert.equal(ico.readUInt16LE(2), 1); assert.equal(ico.readUInt16LE(4), 4);
  for (let i = 0; i < 4; i++) {
    const entry = 6 + 16 * i, size = ico.readUInt32LE(entry + 8), offset = ico.readUInt32LE(entry + 12);
    const frame = rgba(ico.subarray(offset, offset + size)); assert.equal(frame.pixels[3], 0);
  }
});

test("published provenance authenticates derived bytes without depending on excluded source files", () => {
  const manifest = JSON.parse(readFileSync(new URL("../public/assets/brand/neurofly-logo-source.json", import.meta.url), "utf8"));
  assert.equal(manifest.source.sha256, "3d60e4f3d41cd2266fc70108aa5bad3582e170317e65e508646d450d9fa9d676");
  for (const item of manifest.assets) {
    const bytes = readFileSync(new URL(`../../${item.path}`, import.meta.url));
    assert.equal(bytes.length, item.bytes); assert.equal(createHash("sha256").update(bytes).digest("hex"), item.sha256);
  }
});
