const fs = require('fs');
const path = require('path');
const https = require('https');

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'https://adityaretail.com';

function fetchJSON(path) {
  return new Promise((resolve, reject) => {
    https.get(`${API_BASE}${path}`, (res) => {
      let data = '';
      res.on('data', (c) => { data += c; });
      res.on('end', () => {
        try { resolve(JSON.parse(data)); } catch (e) { reject(e); }
      });
    }).on('error', reject);
  });
}

const slugify = (s) => s.toLowerCase().trim().replace(/\s+/g, '-');

// Mirrors frontend/src/components/ProductCard.js getProductUrl() exactly,
// so prerendered routes match the real links customers/crawlers click.
function getProductUrl(product) {
  const categorySlug = product.category
    ? product.category.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
    : 'product';

  let productSlug = product.slug;
  if (!productSlug && product.name) {
    const nameHasBrand = product.brand &&
      product.name.toLowerCase().startsWith(product.brand.toLowerCase());
    const rawSlug = `${(!nameHasBrand && product.brand) ? product.brand + '-' : ''}${product.name}`
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim();
    productSlug = rawSlug.length > 60
      ? rawSlug.slice(0, 60).replace(/-[^-]*$/, '')
      : rawSlug;
    productSlug = productSlug.replace(/^-+|-+$/g, '');
  }

  const brandSlug = product.brand
    ? product.brand.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
    : null;

  if (productSlug && brandSlug) return `/${categorySlug}/${brandSlug}/${productSlug}`;
  if (productSlug) return `/${categorySlug}/${productSlug}`;

  const modelNumber = product.model_number || product.modelNumber;
  const looksLikeRealModelNumber =
    modelNumber &&
    modelNumber.toLowerCase() !== (product.brand || '').toLowerCase() &&
    /[0-9]/.test(modelNumber);

  if (looksLikeRealModelNumber) return `/${categorySlug}/${modelNumber.toLowerCase()}`;

  return `/product/${(product.id || product._id || '').toLowerCase()}`;
}

async function main() {
  const catRes = await fetchJSON('/api/categories/');
  const categories = catRes.categories || [];

  const prodRes = await fetchJSON('/api/products?limit=1000');
  const products = prodRes.products || [];

  // Only real, admin-defined category names are valid routes.
  const validCategoryNames = new Set(
    categories.filter((c) => c.is_active !== false && c.name).map((c) => c.name)
  );

  const brandsByCategory = {};
  const subCategoriesByCategory = {};
  products.forEach((p) => {
    const cat = p.category;
    const brand = p.brand;
    const subCat = p.sub_category;
    // Skip products whose "category" field is actually a mis-entered product name/slug,
    // not a real category — these caused broken prerender pages and Chromium crashes.
    if (cat && validCategoryNames.has(cat) && brand && brand !== 'TestBrand' && brand !== 'Test') {
      if (!brandsByCategory[cat]) brandsByCategory[cat] = new Set();
      brandsByCategory[cat].add(brand);
    }
    if (cat && validCategoryNames.has(cat) && subCat) {
      if (!subCategoriesByCategory[cat]) subCategoriesByCategory[cat] = new Set();
      subCategoriesByCategory[cat].add(subCat);
    }
  });

  const staticRoutes = ['/', '/blog', '/contact-us'];

  const categoryRoutes = [...validCategoryNames].map((name) => `/${slugify(name)}`);

  const brandRoutes = [];
  Object.keys(brandsByCategory).forEach((catKey) => {
    const catSlug = slugify(catKey);
    brandsByCategory[catKey].forEach((brand) => {
      brandRoutes.push(`/${catSlug}/${slugify(brand)}`);
    });
  });

  const subCategoryRoutes = [];
  Object.keys(subCategoriesByCategory).forEach((catKey) => {
    const catSlug = slugify(catKey);
    subCategoriesByCategory[catKey].forEach((subCat) => {
      subCategoryRoutes.push(`/${catSlug}/${slugify(subCat)}`);
    });
  });

  const productRoutes = products
    .filter((p) => p && (p.id || p._id))
    .map((p) => getProductUrl(p));

  const allRoutes = [...new Set([...staticRoutes, ...categoryRoutes, ...brandRoutes, ...subCategoryRoutes])];

  const pkgPath = path.join(__dirname, '..', 'package.json');
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
  pkg.reactSnap = pkg.reactSnap || {};
  pkg.reactSnap.include = allRoutes;
  pkg.reactSnap.puppeteerExecutablePath = pkg.reactSnap.puppeteerExecutablePath || '/usr/bin/chromium';
  pkg.reactSnap.puppeteerArgs = pkg.reactSnap.puppeteerArgs || ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'];
  pkg.reactSnap.concurrency = pkg.reactSnap.concurrency || 1;
  pkg.reactSnap.skipThirdPartyRequests = true;
  fs.writeFileSync(pkgPath, JSON.stringify(pkg, null, 2) + '\n');

  console.log(`Wrote ${allRoutes.length} routes to reactSnap.include`);
  console.log(`  static: ${staticRoutes.length}, categories: ${categoryRoutes.length}, brand pages: ${brandRoutes.length}, subcategory pages: ${subCategoryRoutes.length}`);
  console.log(`  skipped ${products.length} products' categories, keeping only ${validCategoryNames.size} real category names`);
}

main().catch((e) => {
  console.error('Route generation failed (non-fatal, prerender will be skipped):', e.message);
  process.exit(0);
});
