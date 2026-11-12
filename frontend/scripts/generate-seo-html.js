/* Chromium-free SEO prerender: writes real page content into static HTML for every route.
   Runs at build time in cloud builds where react-snap/Chromium is unavailable.
   Must NEVER fail the build — exits 0 on any error. */
const fs = require('fs');
const path = require('path');
const https = require('https');

const BUILD_DIR = process.env.SEO_BUILD_DIR || path.join(__dirname, '..', 'build');
const API_BASE = (process.env.REACT_APP_BACKEND_URL || 'https://adityaretail.com').replace(/\/$/, '');
const SITE = 'https://adityaretail.com';

const esc = (s) => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const slugify = (s) => String(s || '').toLowerCase()
  .replace(/[^a-z0-9\s-]/g, '').replace(/[\s_]+/g, '-').replace(/-+/g, '-').replace(/^-+|-+$/g, '');

function fetchJson(url) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, { timeout: 30000 }, (res) => {
      let data = '';
      res.on('data', (c) => (data += c));
      res.on('end', () => { try { resolve(JSON.parse(data)); } catch (e) { reject(e); } });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
  });
}

function productSlug(p) {
  if (p.slug) return p.slug;
  const name = p.name || '';
  const brand = p.brand || '';
  const prefix = brand && !name.toLowerCase().startsWith(brand.toLowerCase()) ? brand + '-' : '';
  let raw = slugify(prefix + name);
  if (raw.length > 60) raw = raw.slice(0, 60).replace(/-[^-]*$/, '');
  return raw.replace(/^-+|-+$/g, '');
}

function productPath(p) {
  const cat = slugify(p.category) || 'product';
  const slug = productSlug(p);
  if (!slug) return null;
  const brand = slugify(p.brand);
  return brand ? `/${cat}/${brand}/${slug}` : `/${cat}/${slug}`;
}

function headSwap(html, { title, description, canonical }) {
  let out = html.replace(/<title>[\s\S]*?<\/title>/, `<title>${esc(title)}</title>`);
  out = out.replace(/(<meta name="description" content=")[^"]*(")/, `$1${esc(description)}$2`);
  const extra = `<link rel="canonical" href="${esc(canonical)}"/><meta property="og:title" content="${esc(title)}"/><meta property="og:description" content="${esc(description)}"/><meta property="og:url" content="${esc(canonical)}"/><meta property="og:type" content="website"/>`;
  return out.replace('</head>', extra + '</head>');
}

function rootSwap(html, inner) {
  return html.replace(/<div id="root"><\/div>/, `<div id="root">${inner}</div>`);
}

function navHtml(categories) {
  const links = categories.map((c) => `<a href="/${slugify(c)}">${esc(c)}</a>`).join(' ');
  return `<header><a href="/">Aditya Retail — Premium Home Appliances</a><nav>${links} <a href="/blog">Blog</a> <a href="/contact">Contact Us</a></nav></header>`;
}

function writeRoute(route, html) {
  const dir = path.join(BUILD_DIR, ...route.split('/').filter(Boolean));
  const file = path.join(dir, 'index.html');
  if (process.env.SEO_SKIP_EXISTING && fs.existsSync(file)) return false;
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(file, html);
  return true;
}

async function main() {
  const template = fs.readFileSync(path.join(BUILD_DIR, 'index.html'), 'utf8');

  const prodResp = await fetchJson(`${API_BASE}/api/products?limit=2000`);
  const products = (prodResp.products || prodResp || []).filter((p) => p && p.name && p.is_listed !== false);
  const catResp = await fetchJson(`${API_BASE}/api/categories`).catch(() => ({ categories: [] }));
  const rawCats = catResp.categories || [];
  // keep only categories that look like real category names (short, and used by >2 products)
  const counts = {};
  products.forEach((p) => { if (p.category) counts[p.category] = (counts[p.category] || 0) + 1; });
  const categories = [...new Set(rawCats.filter((c) => c && c.length <= 30 && (counts[c] || 0) >= 2))];
  const nav = navHtml(categories);
  const footer = `<footer><p>Aditya Retail — Authorised Bosch &amp; Siemens brand store. Best prices, doorstep delivery, genuine products.</p></footer>`;

  let written = 0;


  // Home page handled by ReactSnap / React build
console.log('[seo-html] Skipping homepage override');



  // Category pages
  for (const cat of categories) {
    const catProducts = products.filter((p) => p.category === cat);
    const inner = `<div>${nav}<main><h1>${esc(cat)} — Buy Online at Best Price</h1><p>${catProducts.length} ${esc(cat)} products from Bosch, Siemens &amp; more at Aditya Retail. Genuine products with doorstep delivery.</p><ul>${catProducts.map((p) => { const u = productPath(p); return u ? `<li><a href="${u}">${esc(p.short_title || p.name)}${p.price ? ` — ₹${p.price}` : ''}</a></li>` : ''; }).join('')}</ul></main>${footer}</div>`;
    writeRoute(`/${slugify(cat)}`, rootSwap(headSwap(template, {
      title: `${cat} - Buy Online at Best Price | Aditya Retail`,
      description: `Buy ${cat} online at Aditya Retail. ${catProducts.length} products from Bosch, Siemens & top brands. Best prices, genuine products, doorstep delivery.`,
      canonical: `${SITE}/${slugify(cat)}`
    }), inner));
    written++;

    // Brand pages within category
    const brands = [...new Set(catProducts.map((p) => p.brand).filter(Boolean))];
    for (const brand of brands) {
      const bp = catProducts.filter((p) => p.brand === brand);
      if (!bp.length) continue;
      const inner2 = `<div>${nav}<main><h1>${esc(brand)} ${esc(cat)}s — Buy Online at Best Price</h1><p>${bp.length} ${esc(brand)} ${esc(cat)} products at Aditya Retail, authorised ${esc(brand)} brand store.</p><ul>${bp.map((p) => { const u = productPath(p); return u ? `<li><a href="${u}">${esc(p.short_title || p.name)}${p.price ? ` — ₹${p.price}` : ''}</a></li>` : ''; }).join('')}</ul></main>${footer}</div>`;
      writeRoute(`/${slugify(cat)}/${slugify(brand)}`, rootSwap(headSwap(template, {
        title: `${brand} ${cat} - Best Price in India | Aditya Retail`,
        description: `Shop ${brand} ${cat} at Aditya Retail — authorised ${brand} store. ${bp.length} models with best prices and doorstep delivery.`,
        canonical: `${SITE}/${slugify(cat)}/${slugify(brand)}`
      }), inner2));
      written++;
    }
  }

  // Product pages
  for (const p of products) {
    const route = productPath(p);
    if (!route) continue;
    const title = p.short_title || p.name;
    const img = (Array.isArray(p.images) && p.images[0]) || p.image || p.image_url || '';
    const desc = (p.description || `Buy ${p.name} from ${p.brand || 'top brands'} at best price with doorstep delivery.`).replace(/\s+/g, ' ').slice(0, 300);
    const jsonld = JSON.stringify([
      {
        '@context': 'https://schema.org', '@type': 'Product',
        name: title, image: img ? [img] : undefined, description: desc,
        brand: p.brand ? { '@type': 'Brand', name: p.brand } : undefined,
        sku: p.model_number || undefined,
        offers: {
          '@type': 'Offer', url: SITE + route, priceCurrency: 'INR',
          price: p.price || undefined,
          availability: (p.stock_quantity === 0 || p.in_stock === false) ? 'https://schema.org/OutOfStock' : 'https://schema.org/InStock',
          seller: { '@type': 'Organization', name: 'Aditya Retail' }
        }
      },
      {
        '@context': 'https://schema.org', '@type': 'BreadcrumbList',
        itemListElement: [
          { '@type': 'ListItem', position: 1, name: 'Home', item: SITE + '/' },
          { '@type': 'ListItem', position: 2, name: p.category, item: `${SITE}/${slugify(p.category)}` },
          ...(p.brand ? [{ '@type': 'ListItem', position: 3, name: p.brand, item: `${SITE}/${slugify(p.category)}/${slugify(p.brand)}` }] : []),
          { '@type': 'ListItem', position: p.brand ? 4 : 3, name: title, item: SITE + route }
        ]
      }
    ]);
    const specs = p.specifications && typeof p.specifications === 'object'
      ? Object.entries(p.specifications).slice(0, 12).map(([k, v]) => `<li>${esc(k)}: ${esc(typeof v === 'object' ? JSON.stringify(v) : v)}</li>`).join('')
      : '';
    const features = Array.isArray(p.features) ? p.features.slice(0, 8).map((f) => `<li>${esc(typeof f === 'object' ? (f.name || f.title || JSON.stringify(f)) : f)}</li>`).join('') : '';
    const inner = `<div>${nav}<main><nav><a href="/">Home</a> &gt; <a href="/${slugify(p.category)}">${esc(p.category)}</a>${p.brand ? ` &gt; <a href="/${slugify(p.category)}/${slugify(p.brand)}">${esc(p.brand)}</a>` : ''} &gt; ${esc(title)}</nav><h1>${esc(title)}</h1>${img ? `<img src="${esc(img)}" alt="${esc(title)}" width="400"/>` : ''}<p>Brand: ${esc(p.brand || '')}${p.model_number ? ` | Model: ${esc(p.model_number)}` : ''} | Category: ${esc(p.category || '')}</p>${p.price ? `<p>Price: ₹${esc(p.price)}${p.originalPrice && p.originalPrice > p.price ? ` (MRP ₹${esc(p.originalPrice)})` : ''}</p>` : ''}<p>${esc(desc)}</p>${features ? `<h2>Key Features</h2><ul>${features}</ul>` : ''}${specs ? `<h2>Specifications</h2><ul>${specs}</ul>` : ''}</main>${footer}</div>`;
    let html = rootSwap(headSwap(template, {
      title: `${title} - Best Price | Aditya Retail`,
      description: `${title} at ₹${p.price || 'best price'}. ${desc.slice(0, 150)}`,
      canonical: SITE + route
    }), inner);
    html = html.replace('</head>', `<script type="application/ld+json">${jsonld}</script></head>`);
    writeRoute(route, html);
    written++;
  }

  console.log(`[seo-html] Wrote real-content HTML for ${written} routes (${products.length} products, ${categories.length} categories) using ${API_BASE}`);
}

main().catch((e) => {
  console.warn('[seo-html] Generation failed (non-fatal, SPA build still valid):', e.message);
  process.exit(0);
});
