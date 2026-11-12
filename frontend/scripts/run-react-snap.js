/* Runs react-snap prerendering in batches, restarting Chrome fresh each batch.
   This avoids crashes from long-running Chromium sessions in low-/dev/shm containers.
   Prerendering is an SEO optimization — it must NEVER fail the production build. */
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const pkgPath = path.join(__dirname, '..', 'package.json');
const BATCH_SIZE = 10;

function findBundledChromium() {
  try {
    const base = path.join(__dirname, '..', 'node_modules', 'puppeteer', '.local-chromium');
    if (!fs.existsSync(base)) return null;
    const versionDirs = fs.readdirSync(base);
    for (const dir of versionDirs) {
      const candidate = path.join(base, dir, 'chrome-linux', 'chrome');
      if (fs.existsSync(candidate)) return candidate;
    }
  } catch (e) { /* ignore */ }
  return null;
}

const candidates = [
  process.env.PUPPETEER_EXECUTABLE_PATH,
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
  '/usr/bin/google-chrome',
  '/usr/bin/google-chrome-stable',
  findBundledChromium()
].filter(Boolean);

let chrome = candidates.find((p) => {
  try { return fs.existsSync(p); } catch (e) { return false; }
});

// No Chromium on the build machine — download puppeteer's bundled Chromium (~120MB)
if (!chrome) {
  console.log('[postbuild] No Chromium found — attempting puppeteer Chromium download...');
  try {
    const env = Object.assign({}, process.env);
    delete env.PUPPETEER_SKIP_CHROMIUM_DOWNLOAD;
    delete env.PUPPETEER_SKIP_DOWNLOAD;
    delete env.PUPPETEER_EXECUTABLE_PATH;
    execSync('node node_modules/puppeteer/install.js', {
      stdio: 'inherit', cwd: path.join(__dirname, '..'), env, timeout: 300000
    });
    chrome = findBundledChromium();
    if (chrome) console.log('[postbuild] Chromium downloaded:', chrome);
  } catch (e) {
    console.warn('[postbuild] Chromium download failed:', e.message);
  }
}

if (!chrome) {
  console.log('[postbuild] No Chrome/Chromium — using static SEO HTML generator instead of react-snap.');
  try {
    execSync('node scripts/generate-seo-html.js', { stdio: 'inherit', cwd: path.join(__dirname, '..') });
  } catch (e) {
    console.warn('[postbuild] SEO HTML generation failed (non-fatal):', e.message);
  }
  try {
    execSync('node scripts/fix-asset-refs.js', { stdio: 'inherit', cwd: path.join(__dirname, '..') });
  } catch (e) {
    console.warn('[postbuild] fix-asset-refs failed (non-fatal):', e.message);
  }
  process.exit(0);
}

function readPkg() {
  return JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
}
function writePkg(pkg) {
  fs.writeFileSync(pkgPath, JSON.stringify(pkg, null, 2) + '\n');
}

const originalPkg = readPkg();
const allRoutes = (originalPkg.reactSnap && originalPkg.reactSnap.include) || ['/'];
const baseReactSnap = originalPkg.reactSnap || {};

const batches = [];
for (let i = 0; i < allRoutes.length; i += BATCH_SIZE) {
  batches.push(allRoutes.slice(i, i + BATCH_SIZE));
}

console.log(`[postbuild] Running react-snap in ${batches.length} batches of up to ${BATCH_SIZE} routes each, using ${chrome}`);

const buildDir = path.join(__dirname, '..', 'build');
const pristineIndexPath = path.join(__dirname, '..', '.pristine-index.html');
const homeIndexBackupPath = path.join(__dirname, '..', '.home-index.html');
const indexPath = path.join(buildDir, 'index.html');
const html200Path = path.join(buildDir, '200.html');

// Preserve the original, un-prerendered index.html BEFORE any batch runs.
// Each batch must start from this pristine shell, not from whatever the
// previous batch left in index.html — otherwise React hydrates the WRONG
// page's markup against the new route (hydration mismatch, crashes the crawl).
fs.copyFileSync(indexPath, pristineIndexPath);

let successCount = 0;
let failCount = 0;

for (let b = 0; b < batches.length; b++) {
  const batch = batches[b];

  // react-snap refuses to run if 200.html already exists from a previous batch.
  if (fs.existsSync(html200Path)) {
    fs.unlinkSync(html200Path);
  }

  // Always start this batch from the pristine, un-rendered shell — prevents
  // hydration-mismatch crashes caused by a previous batch's rendered index.html.
  fs.copyFileSync(pristineIndexPath, indexPath);

  const pkg = readPkg();
  pkg.reactSnap = Object.assign({}, baseReactSnap, {
    include: batch,
    exclude: ['/404.html'],
    crawl: false,
    puppeteerExecutablePath: chrome,
    puppeteerArgs: baseReactSnap.puppeteerArgs || ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
    concurrency: 1,
    skipThirdPartyRequests: false
  });
  writePkg(pkg);

  try {
    console.log(`[postbuild] Batch ${b + 1}/${batches.length} (${batch.length} routes)...`);
    execSync('npx react-snap', { stdio: 'inherit', cwd: path.join(__dirname, '..') });
    successCount += batch.length;

    // If this batch rendered '/', its resulting index.html IS the correct
    // prerendered homepage — save it so we can restore it at the very end
    // (later batches will otherwise overwrite index.html with pristine again).
    if (batch.includes('/') && fs.existsSync(indexPath)) {
      fs.copyFileSync(indexPath, homeIndexBackupPath);
    }
  } catch (e) {
    console.warn(`[postbuild] Batch ${b + 1} failed (non-fatal, continuing to next batch): ${e.message}`);
    failCount += batch.length;
  }
}

// Restore the correctly prerendered homepage (if we captured one), else fall
// back to the pristine shell for index.html.
try {
  if (fs.existsSync(homeIndexBackupPath)) {
    fs.copyFileSync(homeIndexBackupPath, indexPath);
    fs.unlinkSync(homeIndexBackupPath);
    console.log('[postbuild] Restored prerendered homepage as index.html.');
  } else {
    fs.copyFileSync(pristineIndexPath, indexPath);
    console.log('[postbuild] No prerendered homepage captured — index.html left as pristine shell.');
  }
} catch (e) {
  console.warn('[postbuild] Could not finalize index.html:', e.message);
}

// Restore a valid 200.html SPA fallback from the pristine (un-prerendered) shell,
// so routes outside our prerender list still work correctly for real users.
try {
  fs.copyFileSync(pristineIndexPath, html200Path);
  fs.unlinkSync(pristineIndexPath);
  console.log('[postbuild] Restored 200.html SPA fallback from pristine shell.');
} catch (e) {
  console.warn('[postbuild] Could not restore 200.html fallback:', e.message);
}

// restore full include list in package.json for consistency/debugging
const finalPkg = readPkg();
finalPkg.reactSnap = Object.assign({}, baseReactSnap, {
  include: allRoutes,
  puppeteerExecutablePath: chrome
});
writePkg(finalPkg);

console.log(`[postbuild] Prerender complete. Batches attempted: ${batches.length}, routes succeeded (best-effort): ~${successCount}, routes in failed batches: ~${failCount}`);

// Fill ALL remaining routes (especially every product page) with real-content
// static HTML. If react-snap fully failed, regenerate everything including home.
try {
  const env = Object.assign({}, process.env);
  if (successCount > 0) env.SEO_SKIP_EXISTING = '1';
  console.log(`[postbuild] Running SEO HTML generator for remaining routes (skipExisting=${successCount > 0})...`);
  execSync('node scripts/generate-seo-html.js', { stdio: 'inherit', cwd: path.join(__dirname, '..'), env });
} catch (e) {
  console.warn('[postbuild] SEO HTML generator failed (non-fatal):', e.message);
}

// FINAL consistency pass: every HTML file must reference the bundles that
// actually exist in THIS build (guards against stale prerendered HTML from
// any earlier build/environment shipping alongside fresh assets).
try {
  execSync('node scripts/fix-asset-refs.js', { stdio: 'inherit', cwd: path.join(__dirname, '..') });
} catch (e) {
  console.warn('[postbuild] fix-asset-refs failed (non-fatal):', e.message);
}

process.exit(0);
