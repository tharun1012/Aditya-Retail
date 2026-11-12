const fs = require('fs');
const path = require('path');

const PRERENDERED_DIR = path.join(__dirname, 'prerendered');
const BUILD_DIR = path.join(__dirname, 'build');

function getFreshAssetTags(freshHtml) {
  const scriptMatch = freshHtml.match(/<script[^>]*src="\/static\/js\/[^"]+"[^>]*><\/script>/);
  const cssMatch = freshHtml.match(/<link[^>]*href="\/static\/css\/[^"]+"[^>]*rel="stylesheet"[^>]*>|<link[^>]*rel="stylesheet"[^>]*href="\/static\/css\/[^"]+"[^>]*>/);
  return {
    script: scriptMatch ? scriptMatch[0] : null,
    css: cssMatch ? cssMatch[0] : null,
  };
}

function patchHtml(snapshotHtml, freshAssets) {
  let patched = snapshotHtml;
  patched = patched.replace(
    /<script[^>]*src="\/static\/js\/[^"]+"[^>]*><\/script>/,
    freshAssets.script || ''
  );
  patched = patched.replace(
    /<link[^>]*href="\/static\/css\/[^"]+"[^>]*rel="stylesheet"[^>]*>|<link[^>]*rel="stylesheet"[^>]*href="\/static\/css\/[^"]+"[^>]*>/,
    freshAssets.css || ''
  );
  return patched;
}

function walkAndPatch(prerenderedPath, buildPath, freshAssets) {
  const stats = fs.statSync(prerenderedPath);
  if (stats.isDirectory()) {
    if (!fs.existsSync(buildPath)) fs.mkdirSync(buildPath, { recursive: true });
    for (const entry of fs.readdirSync(prerenderedPath)) {
      walkAndPatch(path.join(prerenderedPath, entry), path.join(buildPath, entry), freshAssets);
    }
  } else if (prerenderedPath.endsWith('.html')) {
    const snapshotHtml = fs.readFileSync(prerenderedPath, 'utf8');
    const patched = patchHtml(snapshotHtml, freshAssets);
    fs.writeFileSync(buildPath, patched, 'utf8');
    console.log(`[apply-prerendered] Patched and wrote: ${buildPath}`);
  } else {
    fs.copyFileSync(prerenderedPath, buildPath);
  }
}

if (!fs.existsSync(PRERENDERED_DIR)) {
  console.log('[apply-prerendered] No prerendered folder found, skipping.');
  process.exit(0);
}

if (!fs.existsSync(BUILD_DIR)) {
  console.log('[apply-prerendered] No build folder found, skipping.');
  process.exit(0);
}

const freshIndexPath = path.join(BUILD_DIR, 'index.html');
if (!fs.existsSync(freshIndexPath)) {
  console.log('[apply-prerendered] No fresh build/index.html found, skipping.');
  process.exit(0);
}

const freshHtml = fs.readFileSync(freshIndexPath, 'utf8');
const freshAssets = getFreshAssetTags(freshHtml);

if (!freshAssets.script) {
  console.log('[apply-prerendered] WARNING: could not find script tag in fresh build, aborting to avoid breaking the site.');
  process.exit(0);
}

console.log('[apply-prerendered] Fresh JS asset:', freshAssets.script);
console.log('[apply-prerendered] Fresh CSS asset:', freshAssets.css);
console.log('[apply-prerendered] Applying prerendered HTML with corrected asset references...');

walkAndPatch(PRERENDERED_DIR, BUILD_DIR, freshAssets);

console.log('[apply-prerendered] Done.');
