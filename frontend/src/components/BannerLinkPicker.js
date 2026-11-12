import React, { useEffect, useState } from 'react';
import { BACKEND_URL } from '../config/api';

const CATEGORIES = [
  ['washing-machine', 'Washing Machine'], ['refrigerator', 'Refrigerator'], ['gas-hob', 'Gas Hob'],
  ['induction-hob', 'Induction Hob'], ['dishwasher', 'Dishwasher'], ['sink', 'Sink'],
  ['chimney', 'Chimney'], ['oven', 'Oven'], ['mixer-grinder', 'Mixer Grinder'],
  ['air-fryer', 'Air Fryer'], ['coffee-machine', 'Coffee Machine'], ['detergent', 'Detergent'],
];
const BRANDS = ['Bosch', 'Siemens', 'Electrolux', 'Haier', 'Hindware'];
const PAGES = [['/contact', 'Contact Us'], ['/about', 'About Us'], ['/blog', 'Blog'], ['/faq', 'FAQ']];

const BannerLinkPicker = ({ formData, setFormData }) => {
  const [type, setType] = useState(formData.link_type || 'custom');
  const [cat, setCat] = useState('');
  const [brand, setBrand] = useState('');
  const [q, setQ] = useState('');
  const [products, setProducts] = useState(null);

  useEffect(() => {
    if (type !== 'product' || products) return;
    fetch(`${BACKEND_URL}/api/products`)
      .then((r) => r.json())
      .then((d) => setProducts(Array.isArray(d) ? d : d.products || []))
      .catch(() => setProducts([]));
  }, [type, products]);

  const apply = (t, value, url) =>
    setFormData((prev) => ({ ...prev, link_type: t, link_value: value, link_url: url }));

  const cls = 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600 text-sm';
  const matches = (products || [])
    .filter((p) => p.id && (p.name || '').toLowerCase().includes(q.toLowerCase()))
    .slice(0, 30);

  return (
    <div className="space-y-2">
      <select value={type} className={cls} onChange={(e) => { setType(e.target.value); apply(e.target.value, '', ''); }}>
        <option value="category">Category</option>
        <option value="brand">Brand (within a category)</option>
        <option value="product">Product</option>
        <option value="offer">Page / offer</option>
        <option value="custom">Custom URL</option>
      </select>

      {(type === 'category' || type === 'brand') && (
        <select value={cat} className={cls} onChange={(e) => {
          setCat(e.target.value);
          if (type === 'category') apply('category', e.target.value, e.target.value ? `/category/${e.target.value}` : '');
          else if (brand) apply('brand', `${brand}|${e.target.value}`, `/category/${e.target.value}?brand=${encodeURIComponent(brand)}`);
        }}>
          <option value="">-- Category --</option>
          {CATEGORIES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
      )}

      {type === 'brand' && (
        <select value={brand} className={cls} onChange={(e) => {
          setBrand(e.target.value);
          if (cat && e.target.value) apply('brand', `${e.target.value}|${cat}`, `/category/${cat}?brand=${encodeURIComponent(e.target.value)}`);
        }}>
          <option value="">-- Brand --</option>
          {BRANDS.map((b) => <option key={b} value={b}>{b}</option>)}
        </select>
      )}

      {type === 'product' && (
        <>
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search product name…" className={cls} />
          <select className={cls} value="" onChange={(e) => e.target.value && apply('product', e.target.value, `/product/${e.target.value}`)}>
            <option value="">{products ? `-- ${matches.length} matches --` : 'Loading…'}</option>
            {matches.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </>
      )}

      {type === 'offer' && (
        <select className={cls} value={formData.link_url || ''} onChange={(e) => apply('offer', e.target.value, e.target.value)}>
          <option value="">-- Page --</option>
          {PAGES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
      )}
    </div>
  );
};

export default BannerLinkPicker;
