import React from 'react';
import { Helmet } from 'react-helmet-async';

const SEO = ({
  title = 'Aditya Retail - Premium Home Appliances | Bosch, Siemens & Hindware',
  description = 'Shop premium home appliances from Bosch, Siemens, and Hindware. Expert installation, best prices, and authentic products. Ovens, Chimneys, Gas Hobs, Induction Cooktops, and more.',
  keywords = 'home appliances, kitchen appliances, Bosch appliances, Siemens appliances, Hindware products, built-in ovens, kitchen chimneys, induction cooktop, gas hobs, washing machines, dishwashers',
  image = 'https://adityaretail.com/logo.png',
  url = window.location.href,
  type = 'website'
}) => {
  return (
    <Helmet>
      {/* Basic Meta Tags */}
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />
      
      {/* Open Graph Tags (Facebook, LinkedIn) */}
      <meta property="og:type" content={type} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={image} />
      <meta property="og:url" content={url} />
      <meta property="og:site_name" content="Aditya Retail" />
      
      {/* Twitter Card Tags */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={image} />
      
      {/* Canonical URL */}
      <link rel="canonical" href={url} />
    </Helmet>
  );
};

// Product SEO Component
export const ProductSEO = ({ product }) => {
  if (!product) return null;
  
  const productImage = product.images?.[0] || '/default-product.jpg';
  const productPrice = product.price || 0;
  const inStock = (product.stock_quantity || 0) > 0;
  
  return (
    <>
      <SEO
        title={`${product.name} | ${product.brand} | Aditya Retail`}
        description={product.description || `Buy ${product.name} from ${product.brand}. ${product.key_features?.[0] || 'Premium quality appliance.'}`}
        keywords={`${product.name}, ${product.brand}, ${product.category}, buy ${product.model_number}`}
        image={productImage}
        type="product"
      />
      
      {/* Product Structured Data (Schema.org) */}
      <Helmet>
        <script type="application/ld+json">
          {JSON.stringify({
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": product.name,
            "image": productImage,
            "description": product.description,
            "brand": {
              "@type": "Brand",
              "name": product.brand
            },
            "sku": product.model_number || product.id,
            "offers": {
              "@type": "Offer",
              "url": window.location.href,
              "priceCurrency": "INR",
              "price": productPrice,
              "availability": inStock ? "https://schema.org/InStock" : "https://schema.org/OutOfStock",
              "seller": {
                "@type": "Organization",
                "name": "Aditya Retail"
              }
            }
          })}
        </script>
      </Helmet>
    </>
  );
};

// Category SEO Component
export const CategorySEO = ({ categoryName, productCount }) => {
  return (
    <SEO
      title={`${categoryName} | Premium Home Appliances | Aditya Retail`}
      description={`Shop ${productCount} ${categoryName} products from top brands like Bosch, Siemens, and Hindware. Best prices, expert installation, and authentic products.`}
      keywords={`${categoryName}, buy ${categoryName}, ${categoryName} online, best ${categoryName}`}
    />
  );
};

export default SEO;
