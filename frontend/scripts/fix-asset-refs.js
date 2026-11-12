/* Final consistency pass: rewrite every built HTML file so its main JS/CSS
   references exactly match asset-manifest.json from the CURRENT build.
   Heals any stale/mixed-phase prerendered HTML. Never fails the build. */
const fs = require('fs');
const path = require('path');

const BUILD = process.env.SEO_BUILD_DIR || path.join(__dirname, '..', 'build');

try {
  const manifest = JSON.parse(fs.readFileSync(path.join(BUILD, 'asset-manifest.json'), 'utf8'));
  const mainJs = manifest.files && manifest.files['main.js'];
  const mainCss = manifest.files && manifest.files['main.css'];
  if (!mainJs) {
    console.log('[fix-asset-refs] No main.js in asset-manifest — skipping.');
    process.exit(0);
  }

  const walk = (dir) => {
    let out = [];
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, e.name);
      if (e.isDirectory()) {
        if (e.name !== 'static') out = out.concat(walk(p));
      } else if (e.name.endsWith('.html')) {
        out.push(p);
      }
    }
    return out;
  };

  let fixed = 0;
  for (const file of walk(BUILD)) {
    const orig = fs.readFileSync(file, 'utf8');
    let html = orig.replace(/\/static\/js\/main\.[0-9a-f]+\.js/g, mainJs);
    if (mainCss) html = html.replace(/\/static\/css\/main\.[0-9a-f]+\.css/g, mainCss);
    if (html !== orig) {
      fs.writeFileSync(file, html);
      fixed++;
    }
  }
  console.log(`[fix-asset-refs] Ensured ${mainJs} / ${mainCss || '-'} in all HTML (${fixed} files rewritten).`);
} catch (e) {
  console.warn('[fix-asset-refs] Skipped (non-fatal):', e.message);
}
