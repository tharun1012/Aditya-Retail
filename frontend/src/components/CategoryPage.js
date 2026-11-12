import React, { useState, useEffect, useMemo } from 'react';
import { BACKEND_URL } from '../config/api';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { 
  SlidersHorizontal, Grid, List, ChevronDown, X, ArrowLeft, 
  Filter, Package, TrendingUp, Star
} from 'lucide-react';
import ProductCard from './ProductCard';
import SEOHead, { SEOConfigs, SEOOverrideText } from './SEOHead';
import Breadcrumbs, { generateBreadcrumbs } from './Breadcrumbs';
import { generateItemListSchema, generateFAQSchema } from './SEOSchemas';
import WhyBuyStrip from './WhyBuyStrip';
import BrandCategoryContent from './BrandCategoryContent';


const CategoryPage = ({ onViewProduct, onAddToCart, onAISalesChat, overrideCategoryName, overrideBrandParam }) => {
  const { categoryName: routeCategoryName } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const categoryName = overrideCategoryName || routeCategoryName;
  const searchQuery = searchParams.get('search') || '';
  const brandParam = overrideBrandParam || searchParams.get('brand') || '';
  const maxPriceParam = searchParams.get('maxPrice');
  const isHaierWashingMachine = categoryName === 'washing-machine' && brandParam === 'Haier';
  const [activeBrandContent, setActiveBrandContent] = useState(null);

  // Fetch (or trigger generation of) brand+category content from the backend
  useEffect(() => {
    if (!brandParam) {
      setActiveBrandContent(null);
      return;
    }
    let cancelled = false;
    const fetchBrandContent = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/brand-category-content/${categoryName}/${encodeURIComponent(brandParam)}`);
        const data = await res.json();
        if (!cancelled && data.status === 'success') {
          setActiveBrandContent(data.content);
        }
      } catch (e) {
        console.error('Error fetching brand category content:', e);
      }
    };
    fetchBrandContent();
    return () => { cancelled = true; };
  }, [categoryName, brandParam]);
  
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('grid'); // grid or list
  
  // Filters state
const [filters, setFilters] = useState({
    priceRange: { min: 0, max: maxPriceParam ? parseInt(maxPriceParam, 10) : 500000 },
    brands: brandParam ? [brandParam] : [],
    capacities: [],
    energyRatings: [],
    sizes: [],
    sortBy: 'popularity',
    inStock: false
  });
  
  const [showFilters, setShowFilters] = useState(true);
  const [availableBrands, setAvailableBrands] = useState([]);
  const [availableCapacities, setAvailableCapacities] = useState([]);
  const [availableEnergyRatings, setAvailableEnergyRatings] = useState([]);
  const [availableSizes, setAvailableSizes] = useState([]);
  const [priceRange, setPriceRange] = useState({ min: 0, max: 500000 });
  const [smartFilters, setSmartFilters] = useState([]);
  const [selectedSmartFilters, setSelectedSmartFilters] = useState({});

  useEffect(() => {
    fetchCategoryProducts();
    fetchSmartFilters();
  }, [categoryName, searchQuery]);

  // Apply brand filter from URL param when it changes
  useEffect(() => {
    if (brandParam) {
      setFilters(prev => ({ ...prev, brands: [brandParam] }));
    }
  }, [brandParam]);

  // Apply maxPrice filter from URL param when it changes
  useEffect(() => {
    if (maxPriceParam) {
      const parsed = parseInt(maxPriceParam, 10);
      if (!isNaN(parsed)) {
        setFilters(prev => ({ ...prev, priceRange: { ...prev.priceRange, max: parsed } }));
      }
    }
  }, [maxPriceParam]);
  useEffect(() => {
    applyFilters();
  }, [products, filters, selectedSmartFilters]);

  const fetchSmartFilters = async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 20000);
      const response = await fetch(`${BACKEND_URL}/api/smart-filters/${categoryName}`, { signal: controller.signal });
      clearTimeout(timeoutId);
      const data = await response.json();
      
      if (data.status === 'success' && data.smart_filters) {
        setSmartFilters(data.smart_filters);
        
        // Initialize selected smart filters
        const initialFilters = {};
        data.smart_filters.forEach(filter => {
          initialFilters[filter.filter_name] = [];
        });
        setSelectedSmartFilters(initialFilters);
      }
    } catch (error) {
      // Smart filters are optional — don't block the page
      console.log('Smart filters unavailable, continuing without them');
    }
  };

  const fetchCategoryProducts = async () => {
    try {
      setLoading(true);
      
      // If category is 'all', fetch all products, otherwise fetch by category
      let url = categoryName === 'all' 
        ? `${BACKEND_URL}/api/products?limit=200`
        : `${BACKEND_URL}/api/categories/${categoryName}/products`;
      
      // Add search query if present
      if (searchQuery) {
        url += `${url.includes('?') ? '&' : '?'}search=${encodeURIComponent(searchQuery)}`;
      }
      
      const response = await fetch(url);
      const data = await response.json();
      
      let categoryProducts = [];
      if (data.status === 'success' && data.products) {
        categoryProducts = data.products;
      } else if (Array.isArray(data)) {
        categoryProducts = data;
      } else if (data.products) {
        categoryProducts = data.products;
      }
      
      // Apply client-side search filter if needed
      if (searchQuery && categoryProducts.length > 0) {
        const query = searchQuery.toLowerCase();
        categoryProducts = categoryProducts.filter(p => 
          (p.name && p.name.toLowerCase().includes(query)) ||
          (p.brand && p.brand.toLowerCase().includes(query)) ||
          (p.description && p.description.toLowerCase().includes(query)) ||
          (p.category && p.category.toLowerCase().includes(query))
        );
      }
      
      setProducts(categoryProducts);
        
      // Extract unique brands
      const brands = [...new Set(categoryProducts.map(p => p.brand).filter(Boolean))];
      setAvailableBrands(brands);
      
      // Extract unique capacities from specifications
      const capacities = new Set();
      categoryProducts.forEach(p => {
        if (Array.isArray(p.specifications)) {
          // Look for capacity in specifications
          const capacitySpec = p.specifications.find(s => 
            s.name?.toLowerCase().includes('capacity') || 
            s.name?.toLowerCase().includes('load')
          );
          if (capacitySpec?.value) {
            capacities.add(capacitySpec.value);
          }
        }
      });
      setAvailableCapacities([...capacities]);
      
      // Extract unique energy ratings
      const ratings = new Set();
      categoryProducts.forEach(p => {
        if (Array.isArray(p.specifications)) {
          const ratingSpec = p.specifications.find(s => 
            s.name?.toLowerCase().includes('energy') || 
            s.name?.toLowerCase().includes('rating')
          );
          if (ratingSpec?.value) {
            ratings.add(ratingSpec.value);
          }
        }
      });
      setAvailableEnergyRatings([...ratings]);
      
      // Extract unique sizes/dimensions
      const sizes = new Set();
      categoryProducts.forEach(p => {
        if (Array.isArray(p.specifications)) {
          const sizeSpec = p.specifications.find(s => 
            s.name?.toLowerCase().includes('size') || 
            s.name?.toLowerCase().includes('dimension') ||
            s.name?.toLowerCase().includes('width')
          );
          if (sizeSpec?.value) {
            sizes.add(sizeSpec.value);
          }
        }
      });
      setAvailableSizes([...sizes]);
      
      // Set price range
      const prices = categoryProducts.map(p => p.price || 0);
      if (prices.length > 0) {
        setPriceRange({
          min: Math.min(...prices),
          max: Math.max(...prices)
        });
        
        // Set default filter range
        setFilters(prev => ({
          ...prev,
          priceRange: {
            min: Math.min(...prices),
            max: Math.max(...prices)
          }
        }));
      }
    } catch (error) {
      console.error('Error fetching category products:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...products];
    
    // Price filter
    filtered = filtered.filter(p => 
      (p.price || 0) >= filters.priceRange.min && 
      (p.price || 0) <= filters.priceRange.max
    );
    
    // Brand filter
    if (filters.brands.length > 0) {
      filtered = filtered.filter(p => filters.brands.includes(p.brand));
    }
    
    // Capacity filter
    if (filters.capacities.length > 0) {
      filtered = filtered.filter(p => {
        if (!Array.isArray(p.specifications)) return false;
        const capacitySpec = p.specifications.find(s => 
          s.name?.toLowerCase().includes('capacity') || 
          s.name?.toLowerCase().includes('load')
        );
        return capacitySpec && filters.capacities.includes(capacitySpec.value);
      });
    }
    
    // Energy Rating filter
    if (filters.energyRatings.length > 0) {
      filtered = filtered.filter(p => {
        if (!Array.isArray(p.specifications)) return false;
        const ratingSpec = p.specifications.find(s => 
          s.name?.toLowerCase().includes('energy') || 
          s.name?.toLowerCase().includes('rating')
        );
        return ratingSpec && filters.energyRatings.includes(ratingSpec.value);
      });
    }
    
    // Size filter
    if (filters.sizes.length > 0) {
      filtered = filtered.filter(p => {
        if (!Array.isArray(p.specifications)) return false;
        const sizeSpec = p.specifications.find(s => 
          s.name?.toLowerCase().includes('size') || 
          s.name?.toLowerCase().includes('dimension') ||
          s.name?.toLowerCase().includes('width')
        );
        return sizeSpec && filters.sizes.includes(sizeSpec.value);
      });
    }
    
    // Smart filters (AI-generated)
    for (const [filterName, selectedOptions] of Object.entries(selectedSmartFilters)) {
      if (selectedOptions.length > 0) {
        filtered = filtered.filter(p => {
          // Create a searchable text from product data
          let searchText = `${p.name || ''} `;
          
          if (Array.isArray(p.specifications)) {
            p.specifications.forEach(spec => {
              searchText += `${spec.name || ''} ${spec.value || ''} `;
            });
          }
          
          if (p.features) {
            searchText += p.features.join(' ');
          }
          
          searchText = searchText.toLowerCase();
          
          // Check if any selected option matches
          return selectedOptions.some(option => 
            searchText.includes(option.toLowerCase())
          );
        });
      }
    }
    
    // Stock filter
    if (filters.inStock) {
      filtered = filtered.filter(p => 
        (p.stock || p.stock_quantity || p.current_stock || 0) > 0
      );
    }
    
    // Sorting
    switch (filters.sortBy) {
      case 'price-low':
        filtered.sort((a, b) => (a.price || 0) - (b.price || 0));
        break;
      case 'price-high':
        filtered.sort((a, b) => (b.price || 0) - (a.price || 0));
        break;
      case 'name':
        filtered.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
        break;
      case 'rating':
        filtered.sort((a, b) => (b.rating || 0) - (a.rating || 0));
        break;
      default: // popularity
        filtered.sort((a, b) => (b.featured ? 1 : 0) - (a.featured ? 1 : 0));
    }
    
    setFilteredProducts(filtered);
  };

  const toggleBrandFilter = (brand) => {
    setFilters(prev => ({
      ...prev,
      brands: prev.brands.includes(brand)
        ? prev.brands.filter(b => b !== brand)
        : [...prev.brands, brand]
    }));
  };

  const toggleCapacityFilter = (capacity) => {
    setFilters(prev => ({
      ...prev,
      capacities: prev.capacities.includes(capacity)
        ? prev.capacities.filter(c => c !== capacity)
        : [...prev.capacities, capacity]
    }));
  };

  const toggleEnergyRatingFilter = (rating) => {
    setFilters(prev => ({
      ...prev,
      energyRatings: prev.energyRatings.includes(rating)
        ? prev.energyRatings.filter(r => r !== rating)
        : [...prev.energyRatings, rating]
    }));
  };

  const toggleSizeFilter = (size) => {
    setFilters(prev => ({
      ...prev,
      sizes: prev.sizes.includes(size)
        ? prev.sizes.filter(s => s !== size)
        : [...prev.sizes, size]
    }));
  };

  const toggleSmartFilter = (filterName, option) => {
    setSelectedSmartFilters(prev => {
      const currentOptions = prev[filterName] || [];
      const newOptions = currentOptions.includes(option)
        ? currentOptions.filter(o => o !== option)
        : [...currentOptions, option];
      
      return {
        ...prev,
        [filterName]: newOptions
      };
    });
  };

  const clearFilters = () => {
    setFilters({
      priceRange: { min: priceRange.min, max: priceRange.max },
      brands: [],
      capacities: [],
      energyRatings: [],
      sizes: [],
      sortBy: 'popularity',
      inStock: false
    });
    
    // Clear smart filters
    const clearedSmartFilters = {};
    smartFilters.forEach(filter => {
      clearedSmartFilters[filter.filter_name] = [];
    });
    setSelectedSmartFilters(clearedSmartFilters);
  };

  const formatCategoryName = (name) => {
    return name.split('-').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };
const [showFullBrandContent, setShowFullBrandContent] = useState(false);

  const haierWashingMachineFAQs = [
    { question: 'How is Haier different from Bosch or Siemens washing machines in terms of price and features?', answer: 'Haier washing machines are generally positioned as a value-for-money option, offering solid core wash performance at a more affordable price point compared to premium brands like Bosch and Siemens, which focus more on advanced features and build quality at a higher price.' },
    { question: 'Is after-sales service easily available for Haier washing machines in India?', answer: 'Yes, Haier has an established service network across India. Aditya Retail also provides dedicated support through our service ticket system for any post-purchase assistance.' },
    { question: 'What is the warranty on Haier washing machines?', answer: "Haier washing machines come with the original manufacturer's warranty, with select models offering extended warranty on the motor. Exact warranty terms vary by model and are listed on each product page." },
    { question: 'Do you offer installation for Haier washing machines?', answer: 'Basic installation guidance is included with every purchase. Professional installation services are available at an additional cost for select models.' },
    { question: 'Which Haier washing machine models are best for a family of 4-5 members?', answer: 'For a family of 4-5 members, an 8-9 kg capacity front load or top load Haier washing machine is generally recommended for adequate load capacity without excessive water and electricity usage.' }
  ];

  // Plain-text version of the intro + Why Buy + Types + How to Choose content,
  // used only to compute the first-150-words preview
  const haierBrandContentPlainText = `Shop the complete range of Haier washing machines at Aditya Retail, featuring energy-efficient front load, top load, and semi-automatic models built for Indian households. As an authorised dealer, we offer 100% genuine products, manufacturer warranty, doorstep delivery, and expert installation support across Bengaluru. Browse our full Washing Machine range to compare across brands. Authorised Dealer — every Haier washing machine sold is 100% genuine with full manufacturer warranty. Best Price Guarantee — competitive pricing with regular offers and cashback on select models. Doorstep Delivery — safe, insured delivery within 3-7 business days. Installation Support — basic installation guidance included; professional installation available for select models. After-Sales Service — dedicated service tickets and support team for any issues post-purchase. AI Shopping Assistant — compare Haier models, check specifications, and get personalised recommendations 24/7 via our AI Sales Agent. Haier offers washing machines across multiple formats to suit different household needs and budgets. Front load Haier washing machines are designed for higher wash quality, lower water consumption, and gentler fabric care.`;

  const haierBrandContentPreview = (() => {
    const words = haierBrandContentPlainText.trim().split(/\s+/);
    if (words.length <= 150) return haierBrandContentPlainText;
    return words.slice(0, 150).join(' ') + '…';
  })();
  // Generate category-specific FAQ items (must be before early return for hooks rules)
  const categoryFAQs = useMemo(() => {
    const name = formatCategoryName(categoryName);
    return [
      { question: `What brands of ${name} are available at Aditya Retail?`, answer: `We carry premium ${name} from top brands including Bosch, Siemens, and more. All products are 100% genuine with manufacturer warranty.` },
      { question: `Do you offer free delivery for ${name}?`, answer: `Yes, we offer free delivery on most ${name}. Standard delivery takes 3-7 business days depending on your location.` },
      { question: `What is the warranty on ${name}?`, answer: `All ${name} come with the original manufacturer's warranty, typically ranging from 1 to 5 years depending on the product and brand.` },
      { question: `Can I get installation for ${name}?`, answer: `Basic installation guidance is included. Professional installation services are available at an additional cost for select products.` },
      { question: `How do I choose the right ${name}?`, answer: `Our AI Sales Agent is available 24/7 to help you compare models, check specifications, and find the perfect ${name} for your needs. Click the chat button to get started.` }
    ];
  }, [categoryName]);

  // Build schemas for category page
  const categorySchemas = useMemo(() => {
    const schemas = [];
    const name = formatCategoryName(categoryName);
    if (filteredProducts.length > 0) {
      schemas.push(generateItemListSchema(filteredProducts, name));
    }
    const faqSchema = generateFAQSchema(categoryFAQs);
    if (faqSchema) schemas.push(faqSchema);
    return schemas;
  }, [filteredProducts, categoryName, categoryFAQs]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-64 mb-8"></div>
            <div className="grid grid-cols-4 gap-6">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="h-96 bg-gray-200 rounded-lg"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* SEO Meta Tags + ItemList + FAQ Schemas */}
     <SEOHead
   {...SEOConfigs.category(formatCategoryName(categoryName))}
  {...(brandParam ? { canonical: `/${categoryName}/${brandParam.toLowerCase()}` } : {})}
  {...(activeBrandContent ? { title: activeBrandContent.metaTitle, description: activeBrandContent.metaDescription } : {})}
   schemas={categorySchemas}
/>
      
      {/* Breadcrumbs */}
      <Breadcrumbs
        items={
          brandParam
            ? [
                { label: formatCategoryName(categoryName), url: `/${categoryName}` },
                { label: brandParam, url: null }
              ]
            : generateBreadcrumbs.category(formatCategoryName(categoryName))
        }
      />
      
      {/* Header */}
      <div className="bg-white border-b border-gray-200 py-6">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
                <SEOOverrideText field="h1_tag" fallback={activeBrandContent?.h1 || (brandParam ? `${brandParam} ${formatCategoryName(categoryName)} - Buy Online at Best Price` : formatCategoryName(categoryName))} />
              </h1>
              <p className="text-gray-600">
                {filteredProducts.length} products found
              </p>
            </div>
            
            {/* View Mode & Sort */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded ${viewMode === 'grid' ? 'bg-white shadow' : ''}`}
                >
                  <Grid className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded ${viewMode === 'list' ? 'bg-white shadow' : ''}`}
                >
                  <List className="h-4 w-4" />
                </button>
              </div>
              
              <select
                value={filters.sortBy}
                onChange={(e) => setFilters({...filters, sortBy: e.target.value})}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="popularity">Most Popular</option>
                <option value="price-low">Price: Low to High</option>
                <option value="price-high">Price: High to Low</option>
                <option value="name">Name: A to Z</option>
                <option value="rating">Highest Rated</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex gap-8">
          {/* Filters Sidebar */}
          <div className={`${showFilters ? 'w-64' : 'w-0'} transition-all duration-300 overflow-hidden`}>
            <div className="bg-white rounded-lg shadow-sm p-6 sticky top-4">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold text-gray-900 flex items-center">
                  <Filter className="h-5 w-5 mr-2" />
                  Filters
                </h3>
                <button
                  onClick={clearFilters}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Clear All
                </button>
              </div>

              {/* Price Range */}
              <div className="mb-6">
                <h4 className="font-semibold text-gray-900 mb-3">Price Range</h4>
                <div className="space-y-3">
                  <input
                    type="range"
                    min={priceRange.min}
                    max={priceRange.max}
                    value={filters.priceRange.max}
                    onChange={(e) => setFilters({
                      ...filters,
                      priceRange: { ...filters.priceRange, max: parseInt(e.target.value) }
                    })}
                    className="w-full"
                  />
                  <div className="flex items-center justify-between text-sm text-gray-600">
                    <span>₹{filters.priceRange.min.toLocaleString()}</span>
                    <span>₹{filters.priceRange.max.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {/* Brands */}
              <div className="mb-6">
                <h4 className="font-semibold text-gray-900 mb-3">Brands</h4>
                <div className="space-y-2">
                  {availableBrands.map(brand => (
                    <label key={brand} className="flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={filters.brands.includes(brand)}
                        onChange={() => toggleBrandFilter(brand)}
                        className="mr-2 rounded"
                      />
                      <span className="text-sm text-gray-700">{brand}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* AI-Powered Smart Filters */}
              {smartFilters.map((smartFilter, index) => (
                <div key={index} className="mb-6">
                  <div className="flex items-center mb-3">
                    <h4 className="font-semibold text-gray-900">{smartFilter.filter_name}</h4>
                    <span className="ml-2 text-xs bg-gradient-to-r from-purple-500 to-pink-500 text-white px-2 py-0.5 rounded-full">
                      AI
                    </span>
                  </div>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {smartFilter.filter_options.map((option, optionIndex) => (
                      <label key={optionIndex} className="flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={(selectedSmartFilters[smartFilter.filter_name] || []).includes(option)}
                          onChange={() => toggleSmartFilter(smartFilter.filter_name, option)}
                          className="mr-2 rounded"
                        />
                        <span className="text-sm text-gray-700">{option}</span>
                      </label>
                    ))}
                  </div>
                </div>
              ))}

              {/* Capacity */}
              {availableCapacities.length > 0 && (
                <div className="mb-6">
                  <h4 className="font-semibold text-gray-900 mb-3">Capacity</h4>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {availableCapacities.map(capacity => (
                      <label key={capacity} className="flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={filters.capacities.includes(capacity)}
                          onChange={() => toggleCapacityFilter(capacity)}
                          className="mr-2 rounded"
                        />
                        <span className="text-sm text-gray-700">{capacity}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {/* Energy Rating */}
              {availableEnergyRatings.length > 0 && (
                <div className="mb-6">
                  <h4 className="font-semibold text-gray-900 mb-3">Energy Rating</h4>
                  <div className="space-y-2">
                    {availableEnergyRatings.map(rating => (
                      <label key={rating} className="flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={filters.energyRatings.includes(rating)}
                          onChange={() => toggleEnergyRatingFilter(rating)}
                          className="mr-2 rounded"
                        />
                        <span className="text-sm text-gray-700">{rating}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {/* Size/Dimension */}
              {availableSizes.length > 0 && (
                <div className="mb-6">
                  <h4 className="font-semibold text-gray-900 mb-3">Size/Dimension</h4>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {availableSizes.map(size => (
                      <label key={size} className="flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={filters.sizes.includes(size)}
                          onChange={() => toggleSizeFilter(size)}
                          className="mr-2 rounded"
                        />
                        <span className="text-sm text-gray-700">{size}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {/* Stock Availability */}
              <div className="mb-6">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={filters.inStock}
                    onChange={(e) => setFilters({...filters, inStock: e.target.checked})}
                    className="mr-2 rounded"
                  />
                  <span className="text-sm text-gray-700">In Stock Only</span>
                </label>
              </div>
            </div>
          </div>

          {/* Products Grid */}
          <div className="flex-1">
            {/* Filter Toggle for Mobile */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="lg:hidden mb-4 flex items-center px-4 py-2 bg-white border border-gray-300 rounded-lg"
            >
              <SlidersHorizontal className="h-4 w-4 mr-2" />
              {showFilters ? 'Hide Filters' : 'Show Filters'}
            </button>

            {filteredProducts.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm p-12 text-center">
                <Package className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  No products found
                </h3>
                <p className="text-gray-600 mb-4">
                  Try adjusting your filters to see more results
                </p>
                <button
                  onClick={clearFilters}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Clear Filters
                </button>
              </div>
            ) : (
              <div className={`grid ${
                viewMode === 'grid' 
                  ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4' 
                  : 'grid-cols-1'
              } gap-6`}>
                {filteredProducts.map(product => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    onViewProduct={onViewProduct}
                    onAddToCart={onAddToCart}
                    onAISalesChat={onAISalesChat}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
     <BrandCategoryContent content={activeBrandContent} />

      {/* Category FAQ Section - boosts SEO with FAQ schema (hidden when a brand-specific FAQ already exists) */}
      {!activeBrandContent && (
      <div className="max-w-7xl mx-auto px-4 py-12" data-testid="category-faq-section">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          Frequently Asked Questions about {formatCategoryName(categoryName)}
        </h2>
        <div className="space-y-3">
          {categoryFAQs.map((faq, idx) => (
            <details key={idx} className="bg-white rounded-lg shadow-sm group" data-testid={`category-faq-${idx}`}>
              <summary className="px-6 py-4 cursor-pointer font-semibold text-gray-900 hover:bg-gray-50 transition-colors list-none flex items-center justify-between">
                {faq.question}
                <ChevronDown className="w-5 h-5 text-gray-500 group-open:rotate-180 transition-transform flex-shrink-0 ml-2" />
              </summary>
              <div className="px-6 pb-4 text-gray-700 border-t border-gray-100">
                <p className="pt-3">{faq.answer}</p>
              </div>
            </details>
          ))}
        </div>
      </div>
      )}
    </div>
  );
};

export default CategoryPage;