import React, { useState, useMemo, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Filter, SlidersHorizontal, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import ProductCard from './ProductCard';
import BoschStyleProductDetail from './BoschStyleProductDetail';
import { useProducts, useBrands } from '../hooks/useProducts';

const ProductGrid = ({ 
  title = "Products", 
  selectedCategory, 
  onAddToCart, 
  onViewProduct, 
  onAISalesChat,
  showFilters = true 
}) => {
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState(0);
  const [sortBy, setSortBy] = useState('name');
  const [priceRange, setPriceRange] = useState([0, 500000]);
  const [selectedBrands, setSelectedBrands] = useState([]);
  const [selectedSizes, setSelectedSizes] = useState([]);
  const [selectedSeries, setSelectedSeries] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilterPanel, setShowFilterPanel] = useState(false);
  const [selectedProductForDetail, setSelectedProductForDetail] = useState(null);
  const [isProductDetailOpen, setIsProductDetailOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  
  // Detect mobile viewport
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);
  
  const productsPerPage = 8;

  // Use real API data with initial filters
  const initialFilters = useMemo(() => ({
    category: selectedCategory,
    min_price: priceRange[0], 
    max_price: priceRange[1]
  }), [selectedCategory, priceRange]);
  
  const { products: allProducts, loading, error, updateFilters } = useProducts(initialFilters);
  const { brands } = useBrands();

  // Update filters when category or price range changes
  useEffect(() => {
    const newFilters = { 
      category: selectedCategory,
      min_price: priceRange[0],
      max_price: priceRange[1]
    };
    
    // Only update if filters have actually changed
    updateFilters(newFilters);
  }, [selectedCategory, priceRange, updateFilters]);

  // Filter and sort products client-side for additional filtering
  const filteredProducts = useMemo(() => {
    let products = [...allProducts];
    
    // Apply search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      products = products.filter(product => 
        product.name.toLowerCase().includes(query) ||
        product.brand.toLowerCase().includes(query) ||
        product.modelNumber?.toLowerCase().includes(query) ||
        product.category.toLowerCase().includes(query) ||
        product.description?.toLowerCase().includes(query)
      );
    }
    
    // Apply brand filter
    if (selectedBrands.length > 0) {
      products = products.filter(product => 
        selectedBrands.includes(product.brand)
      );
    }
    
    // Apply size filter (extract width from specifications or sub_category)
    if (selectedSizes.length > 0) {
      products = products.filter(product => {
        const width = product.specifications?.Width || product.subCategory || '';
        return selectedSizes.some(size => width.includes(size));
      });
    }
    
    // Apply series filter
    if (selectedSeries.length > 0) {
      products = products.filter(product => {
        const series = product.specifications?.Series || '';
        return selectedSeries.some(s => series.includes(s));
      });
    }
    
    // Sort products
    products.sort((a, b) => {
      switch (sortBy) {
        case 'price-low':
          return a.price - b.price;
        case 'price-high':
          return b.price - a.price;
        case 'name':
          return a.name.localeCompare(b.name);
        case 'rating':
          return (b.rating || 0) - (a.rating || 0);
        case 'newest':
          return new Date(b.createdAt || 0) - new Date(a.createdAt || 0);
        default:
          return 0;
      }
    });
    
    return products;
  }, [allProducts, selectedBrands, selectedSizes, selectedSeries, searchQuery, sortBy]);

  const totalPages = Math.ceil(filteredProducts.length / productsPerPage);
  const currentProducts = filteredProducts.slice(
    currentPage * productsPerPage,
    (currentPage + 1) * productsPerPage
  );

  const toggleBrand = (brand) => {
    setSelectedBrands(prev => 
      prev.includes(brand) 
        ? prev.filter(b => b !== brand)
        : [...prev, brand]
    );
  };

  const nextPage = () => {
    setCurrentPage(prev => Math.min(prev + 1, totalPages - 1));
  };

  const prevPage = () => {
    setCurrentPage(prev => Math.max(prev - 1, 0));
  };

  return (
    <div className="bg-white py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Search Bar */}
        <div className="mb-6">
          <input
            type="text"
            placeholder="Search by product name, model, brand, or category..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Section Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              {selectedCategory ? `${selectedCategory} Products` : title}
            </h2>
            <p className="text-gray-600">
              {filteredProducts.length} products found
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Sort Dropdown */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="name">Sort by Name</option>
              <option value="price-low">Price: Low to High</option>
              <option value="price-high">Price: High to Low</option>
              <option value="rating">Highest Rated</option>
              <option value="newest">Newest First</option>
            </select>
            
            {showFilters && (
              <button
                onClick={() => setShowFilterPanel(!showFilterPanel)}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                <SlidersHorizontal className="w-5 h-5" />
                <span>Filters</span>
              </button>
            )}
          </div>
        </div>

        <div className="flex gap-8">
          {/* Filter Panel */}
          {showFilters && showFilterPanel && (
            <div className="w-80 bg-gray-50 rounded-lg p-6">
              <div className="flex items-center space-x-2 mb-4">
                <Filter className="w-5 h-5 text-gray-600" />
                <h3 className="font-semibold text-gray-800">Filters</h3>
              </div>
              
              {/* Price Range */}
              <div className="mb-6">
                <h4 className="font-medium text-gray-700 mb-3">Price Range</h4>
                <div className="space-y-2">
                  <input
                    type="range"
                    min="0"
                    max="200000"
                    value={priceRange[1]}
                    onChange={(e) => setPriceRange([priceRange[0], parseInt(e.target.value)])}
                    className="w-full"
                  />
                  <div className="flex justify-between text-sm text-gray-600">
                    <span>₹{priceRange[0].toLocaleString()}</span>
                    <span>₹{priceRange[1].toLocaleString()}</span>
                  </div>
                </div>
              </div>
              
              {/* Brand Filter */}
              <div className="mb-6">
                <h4 className="font-medium text-gray-700 mb-3">Brands</h4>
                <div className="space-y-2">
                  {brands.map(brand => (
                    <label key={brand} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={selectedBrands.includes(brand)}
                        onChange={() => toggleBrand(brand)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-gray-700">{brand}</span>
                    </label>
                  ))}
                </div>
              </div>
              
              {/* Size/Width Filter */}
              <div className="mb-6">
                <h4 className="font-medium text-gray-700 mb-3">Size/Width</h4>
                <div className="space-y-2">
                  {['60 cm', '75 cm', '90 cm', '80 cm', '30 cm'].map(size => (
                    <label key={size} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={selectedSizes.includes(size)}
                        onChange={() => setSelectedSizes(prev => 
                          prev.includes(size) 
                            ? prev.filter(s => s !== size)
                            : [...prev, size]
                        )}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-gray-700">{size}</span>
                    </label>
                  ))}
                </div>
              </div>
              
              {/* Series Filter */}
              <div className="mb-6">
                <h4 className="font-medium text-gray-700 mb-3">Series</h4>
                <div className="space-y-2">
                  {['iQ700', 'iQ500', 'iQ300', 'Series 8', 'Series 6', 'Series 4', 'Series 2'].map(series => (
                    <label key={series} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={selectedSeries.includes(series)}
                        onChange={() => setSelectedSeries(prev => 
                          prev.includes(series) 
                            ? prev.filter(s => s !== series)
                            : [...prev, series]
                        )}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-gray-700">{series}</span>
                    </label>
                  ))}
                </div>
              </div>
              
              {/* Clear Filters */}
              <button
                onClick={() => {
                  setPriceRange([0, 500000]);
                  setSelectedBrands([]);
                  setSelectedSizes([]);
                  setSelectedSeries([]);
                  setSearchQuery('');
                }}
                className="w-full py-2 px-4 bg-gray-200 hover:bg-gray-300 rounded-lg text-gray-700 transition-colors"
              >
                Clear All Filters
              </button>
            </div>
          )}

          {/* Product Grid */}
          <div className="flex-1">
            {currentProducts.length > 0 ? (
              <>
                <div 
                  id="mobile-product-grid"
                  className="product-grid grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6"
                >
                  {currentProducts.map(product => (
                    <ProductCard
                      key={product.id}
                      product={product}
                      onAddToCart={onAddToCart}
                      onViewProduct={(product) => {
                        setSelectedProductForDetail(product);
                        setIsProductDetailOpen(true);
                        onViewProduct && onViewProduct(product);
                      }}
                      onAISalesChat={onAISalesChat}
                    />
                  ))}
                </div>

                {/* View All Button */}
                {totalPages > 1 && (
                  <div className="flex justify-center mt-10">
                    <button
                      onClick={() => {
                        if (selectedCategory) {
                          const slug = selectedCategory.toLowerCase().replace(/\s+/g, '-');
                          navigate(`/${slug}`);
                        } else {
                          navigate('/category/all');
                        }
                      }}
                      className="inline-flex items-center gap-2 px-8 py-3 bg-amber-700 hover:bg-amber-800 text-white rounded-full font-semibold text-sm transition-all shadow-md hover:shadow-lg"
                      data-testid="view-all-products-btn"
                    >
                      View All {selectedCategory || 'Products'}
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-12">
                <div className="text-gray-400 mb-4">
                  <Filter className="w-16 h-16 mx-auto" />
                </div>
                <h3 className="text-xl font-semibold text-gray-600 mb-2">No products found</h3>
                <p className="text-gray-500">Try adjusting your filters or search criteria</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Bosch-Style Product Detail View */}
      <BoschStyleProductDetail
        product={selectedProductForDetail}
        isOpen={isProductDetailOpen}
        onClose={() => {
          setIsProductDetailOpen(false);
          setSelectedProductForDetail(null);
        }}
        onAddToCart={onAddToCart}
        onAIChat={onAISalesChat}
      />
    </div>
  );
};

export default ProductGrid;