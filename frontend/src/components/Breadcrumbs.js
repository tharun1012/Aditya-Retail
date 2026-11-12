import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';
import { generateBreadcrumbSchema } from './SEOSchemas';

const Breadcrumbs = ({ items = [] }) => {
  const breadcrumbSchema = generateBreadcrumbSchema(items);

  return (
    <>
      {/* Breadcrumb Schema JSON-LD */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }}
      />

      {/* Breadcrumb UI */}
      <nav aria-label="Breadcrumb" className="py-3 px-4 bg-gray-50 border-b border-gray-200" data-testid="breadcrumb-nav">
        <ol className="flex items-center space-x-2 text-sm max-w-7xl mx-auto flex-wrap">
          {/* Home */}
          <li>
            <Link 
              to="/" 
              className="flex items-center text-gray-600 hover:text-blue-600 transition-colors"
              aria-label="Home"
              data-testid="breadcrumb-home"
            >
              <Home className="w-4 h-4" />
            </Link>
          </li>

          {/* Breadcrumb Items */}
          {items.map((item, index) => (
            <React.Fragment key={index}>
              <li>
                <ChevronRight className="w-4 h-4 text-gray-400" />
              </li>
              <li>
                {item.url && index < items.length - 1 ? (
                  <Link 
                    to={item.url}
                    className="text-gray-600 hover:text-blue-600 transition-colors"
                    data-testid={`breadcrumb-link-${index}`}
                  >
                    {item.label}
                  </Link>
                ) : (
                  <span className="text-gray-900 font-medium" aria-current="page" data-testid={`breadcrumb-current-${index}`}>
                    {item.label}
                  </span>
                )}
              </li>
            </React.Fragment>
          ))}
        </ol>
      </nav>
    </>
  );
};

// Helper: generate breadcrumb items for common routes
// Structure: Home > Category > Brand > Product
export const generateBreadcrumbs = {
  category: (categoryName) => [
    { label: categoryName, url: null }
  ],
  
  // Full: Home > Category > Brand > Short Product Title
  product: (product, categoryName) => {
    const catSlug = categoryName.toLowerCase().replace(/ /g, '-');
    const brand = product.brand;
    const crumbs = [
      { label: categoryName, url: `/${catSlug}` }
    ];
    // Add brand level if brand exists
    if (brand) {
      crumbs.push({ label: brand, url: `/${catSlug}/${brand.toLowerCase().replace(/\s+/g, '-')}` });
    }
    crumbs.push({ label: product.short_title || product.name, url: null });
    return crumbs;
  },
  
  // Brand-filtered category: Home > Category > Brand Category
  brandCategory: (categoryName, brandName) => [
    { label: categoryName, url: `/${categoryName.toLowerCase().replace(/ /g, '-')}` },
    { label: `${brandName} ${categoryName}`, url: null }
  ],

  checkout: () => [
    { label: 'Cart', url: '/cart' },
    { label: 'Checkout', url: null }
  ],
  
  account: (pageName) => [
    { label: 'My Account', url: '/account' },
    { label: pageName, url: null }
  ],

  blog: () => [
    { label: 'Blog', url: null }
  ],

  blogPost: (title) => [
    { label: 'Blog', url: '/blog' },
    { label: title, url: null }
  ],

  faq: () => [
    { label: 'FAQ', url: null }
  ],

  contact: () => [
    { label: 'Contact Us', url: null }
  ],

  about: () => [
    { label: 'About Us', url: null }
  ]
};

export default Breadcrumbs;
