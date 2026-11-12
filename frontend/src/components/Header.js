import FestiveCountdown from './FestiveCountdown';
import FestiveDecor from './FestiveDecor';
import { isFestive, greeting } from '../utils/festive';
import { useActiveTheme } from '../context/ActiveThemeContext';
import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, ShoppingCart, User, Menu, X, MessageCircle, LogOut, Facebook, Instagram, Linkedin, Twitter, Youtube, Package, Heart, LayoutDashboard, ChevronDown, Phone } from 'lucide-react';
import { categories } from '../data/mockData';
import { BACKEND_URL } from '../config/api';
import WhyBuyStrip from './WhyBuyStrip';
import Login from './Login';
import Register from './Register';
import InstallAppButton from './InstallAppButton';
import { useAuth } from '../contexts/AuthContext';
import NotificationBell from './NotificationBell';

// TODO: replace with your real WhatsApp business number (country code + number, no + or spaces)
const WHATSAPP_NUMBER = '919844577440';

const Header = ({ cartCount, cartTotal, onCategorySelect, onAIChat }) => {
  const { theme: activeTheme } = useActiveTheme();
  const festive = isFestive(activeTheme);
  const navBg = festive ? 'festive-nav' : 'bg-amber-700';
  const navigate = useNavigate();
  const { user, logout, isAuthenticated } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [isRegisterOpen, setIsRegisterOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSearchCategory, setSelectedSearchCategory] = useState('');
  const [categoryBrands, setCategoryBrands] = useState({});
  const [hoveredCategory, setHoveredCategory] = useState(null);
  const [allProducts, setAllProducts] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [navCategories, setNavCategories] = useState(() => {
    try {
      const extras = JSON.parse(localStorage.getItem('navExtrasCache') || '[]');
      return extras.length > 0 ? [...categories, ...extras] : categories;
    } catch (e) { return categories; }
  });
  const [categoriesReady, setCategoriesReady] = useState(false);
  const [showMobileSearch, setShowMobileSearch] = useState(false);
  // Merge admin-managed categories (e.g. newly added ones like TV) into the nav
  // Nav is only rendered once this resolves (success, error, or timeout) so it
  // appears once in its final form instead of growing after first paint.
  useEffect(() => {
    const settle = (finalCategories) => {
      if (finalCategories) setNavCategories(finalCategories);
      setCategoriesReady(true);
    };

    const fetchManagedCategories = async () => {
      try {
        let res;
        for (let i = 0; i < 3; i++) {
          try {
            res = await fetch(`${BACKEND_URL}/api/categories/`, { cache: 'no-store' });
            if (res.ok) break;
          } catch (err) { if (i === 2) throw err; }
          await new Promise(r => setTimeout(r, 800 * (i + 1)));
        }
        const data = await res.json();
        const managed = data.categories || [];
        const norm = (n) => n.toLowerCase().trim().replace(/s$/, '');
        const staticNames = new Set(categories.map(c => norm(c.name)));
        const seen = new Set();
        const extras = managed
          .filter(c => {
            if (!c.name || staticNames.has(norm(c.name)) || seen.has(norm(c.name))) return false;
            seen.add(norm(c.name));
            return true;
          })
          .map(c => ({
            id: `dyn-${c.id || c.name}`,
            name: c.name,
            subcategories: (c.sub_categories || []).filter(s => s.is_active !== false).map(s => s.name)
          }));
        try { localStorage.setItem('navExtrasCache', JSON.stringify(extras)); } catch (e) {}
        settle(extras.length > 0 ? [...categories, ...extras] : categories);
      } catch (e) {
        console.error('Error fetching managed categories:', e);
        settle(null);
      }
    };

    fetchManagedCategories();
    // Safety timeout: if the API is slow/down, show static categories after 1s
    // rather than leaving the nav in a placeholder state indefinitely.
    const timeoutId = setTimeout(() => settle(null), 2500);
    return () => clearTimeout(timeoutId);
  }, []);

  // Fetch brands per category once on mount (also caches full product list for search suggestions)
  useEffect(() => {
    const fetchBrands = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/products?limit=300`);
        const data = await response.json();
        const products = data.products || data || [];
        setAllProducts(products);
        const brandsMap = {};
        products.forEach(p => {
          const cat = p.category;
          const brand = p.brand;
          if (cat && brand && brand !== 'TestBrand' && brand !== 'Test') {
            if (!brandsMap[cat]) brandsMap[cat] = new Set();
            brandsMap[cat].add(brand);
          }
        });
        // Convert sets to sorted arrays
        const result = {};
        Object.keys(brandsMap).forEach(cat => {
          result[cat] = [...brandsMap[cat]].sort();
        });
        setCategoryBrands(result);
      } catch (e) {
        console.error('Error fetching brands:', e);
      }
    };
    fetchBrands();
  }, []);

  // Reserve space at the bottom of the viewport on mobile so page content
  // isn't hidden behind the new fixed mobile bottom bar. Desktop is untouched.
  useEffect(() => {
    const updateBodyPadding = () => {
      document.body.style.paddingBottom = window.innerWidth < 768 ? '48px' : '0px';
    };
    updateBodyPadding();
    window.addEventListener('resize', updateBodyPadding);
    return () => {
      window.removeEventListener('resize', updateBodyPadding);
      document.body.style.paddingBottom = '0px';
    };
  }, []);

  const handleLogin = (userData) => {
    // This is handled by the Login component via AuthContext now
    setIsLoginOpen(false);
  };

  const handleLogout = () => {
    logout();
    // Clear all user type data
    localStorage.removeItem('userType');
    localStorage.removeItem('storeToken');
    localStorage.removeItem('storeUser');
    localStorage.removeItem('storeData');
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
    navigate('/');
  };

  const switchToRegister = () => {
    setIsLoginOpen(false);
    setIsRegisterOpen(true);
  };

  const switchToLogin = () => {
    setIsRegisterOpen(false);
    setIsLoginOpen(true);
  };

  // Parse natural language like "washing machine under 30000" into structured filters
  const parseSmartSearch = (query) => {
    const lower = query.toLowerCase();
    let maxPrice = null;
    const priceMatch = lower.match(/(?:under|below|less than|within)\s*(?:rs\.?|₹)?\s*(\d+(?:,\d+)?)\s*(k)?/);
    if (priceMatch) {
      let num = parseInt(priceMatch[1].replace(/,/g, ''), 10);
      if (priceMatch[2]) num *= 1000;
      maxPrice = num;
    }
    const matchedCategory = navCategories.find(c => lower.includes(c.name.toLowerCase()));
    const allBrands = new Set();
    Object.values(categoryBrands).forEach(arr => arr.forEach(b => allBrands.add(b)));
    const matchedBrand = [...allBrands].find(b => lower.includes(b.toLowerCase()));
    return { maxPrice, category: matchedCategory?.name || null, brand: matchedBrand || null };
  };

  // Handle search functionality — now understands category, brand, and price constraints
  const handleSearch = () => {
    if (!searchQuery.trim()) return;
    const { maxPrice, category, brand } = parseSmartSearch(searchQuery);
    const resolvedCategory = category || selectedSearchCategory;
    const catSlug = resolvedCategory
      ? resolvedCategory.toLowerCase().replace(/\s+/g, '-')
      : 'all';
    const params = new URLSearchParams();
    if (!category) {
      params.set('search', searchQuery.trim());
    }
    if (brand) params.set('brand', brand);
    if (maxPrice) params.set('maxPrice', String(maxPrice));
    setShowSuggestions(false);
    setShowMobileSearch(false);
    navigate(`/${catSlug}${params.toString() ? '?' + params.toString() : ''}`);
  };

  // Handle search on Enter key
  const handleSearchKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // Live suggestions as the user types
  const searchSuggestions = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (q.length < 2) return [];
    return allProducts
      .filter(p =>
        (p.name && p.name.toLowerCase().includes(q)) ||
        (p.brand && p.brand.toLowerCase().includes(q)) ||
        (p.category && p.category.toLowerCase().includes(q))
      )
      .slice(0, 6);
  }, [searchQuery, allProducts]);

  // Build a product URL matching the same slug pattern used on product cards
const getSuggestionUrl = (product) => {
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
  }

  const brandSlug = product.brand
    ? product.brand.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
    : null;

  if (productSlug && brandSlug) {
    return `/${categorySlug}/${brandSlug}/${productSlug}`;
  }
  if (productSlug) {
    return `/${categorySlug}/${productSlug}`;
  }

  const modelNumber = product.model_number || product.modelNumber;
  if (modelNumber) {
    return `/${categorySlug}/${modelNumber.toLowerCase()}`;
  }

  return `/product/${(product.id || product._id || '').toLowerCase()}`;
};

  const handleSuggestionClick = (product) => {
    setSearchQuery('');
    setShowSuggestions(false);
    setShowMobileSearch(false);
    navigate(getSuggestionUrl(product));
  };

  // Handle category click from menu - navigate to category page
  const handleCategoryClick = (categoryName) => {
    setIsMobileMenuOpen(false);
    setHoveredCategory(null);
    if (categoryName === null) {
      navigate('/');
    } else {
      const slug = categoryName.toLowerCase().replace(/\s+/g, '-');
      navigate(`/${slug}`);
    }
  };

  // Handle brand click — navigate to category page filtered by brand
  const handleBrandClick = (categoryName, brandName) => {
    setIsMobileMenuOpen(false);
    setHoveredCategory(null);
    const catSlug = categoryName.toLowerCase().replace(/\s+/g, '-');
    navigate(`/${catSlug}/${brandName.toLowerCase().replace(/\s+/g, '-')}`);
  };

  // Get brands for a given category name (case-insensitive match)
  const getBrandsForCategory = (categoryName) => {
    // Direct match
    if (categoryBrands[categoryName]) return categoryBrands[categoryName];
    // Case-insensitive search
    const key = Object.keys(categoryBrands).find(
      k => k.toLowerCase() === categoryName.toLowerCase()
    );
    return key ? categoryBrands[key] : [];
  };

  // Handle Contact Us click
  const handleContactClick = () => {
    setIsMobileMenuOpen(false);
    navigate('/contact');
  };

  return (
    <>
      <header className="w-full bg-white shadow-sm fixed top-0 left-0 right-0 z-40">
      <FestiveDecor theme={activeTheme} />
        {/* Top Header - Trust Badges & Social Media */}
        <div className={`${(festive && activeTheme.background_color) || 'bg-gray-50'} border-b`}>
        <div className="max-w-7xl mx-auto px-3 py-1.5 md:px-4 md:py-2">
          <div className="flex justify-between items-center text-xs text-gray-600">
            <div className="flex items-center space-x-4">
              {festive && <span className="font-semibold text-gray-800 truncate max-w-[70vw]">{greeting(activeTheme)}</span>}
              {festive && <FestiveCountdown endsAt={activeTheme.ends_at} />}
              <span className={festive ? 'hidden md:inline' : ''}>Assured Safe Delivery</span>
              <span className="hidden md:inline">Payment Secure System</span>
              <span className="hidden lg:inline">Only Best Brands</span>
            </div>

            {/* Social Media Icons */}
            <div className="flex items-center space-x-3">
              <span className="hidden md:inline mr-2">Follow Us:</span>
              <a
                href="https://www.facebook.com/adityaretailonline1"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-amber-700 transition-colors"
                aria-label="Facebook"
              >
                <Facebook size={16} />
              </a>
              <a
                href="https://www.instagram.com/adityaretailonline/"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-amber-700 transition-colors"
                aria-label="Instagram"
              >
                <Instagram size={16} />
              </a>
              <a
                href="https://www.linkedin.com/company/adityaretailonline/"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-amber-700 transition-colors"
                aria-label="LinkedIn"
              >
                <Linkedin size={16} />
              </a>
              <a
                href="https://x.com/adityaretailon1"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-amber-700 transition-colors"
                aria-label="X (Twitter)"
              >
                <Twitter size={16} />
              </a>
              <a
                href="https://www.youtube.com/@adityaretailonline"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-amber-700 transition-colors"
                aria-label="YouTube"
              >
                <Youtube size={16} />
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Main Header */}
      <div className="max-w-7xl mx-auto px-3 py-1 md:py-4">
        <div className="flex items-center justify-between flex-nowrap h-12 md:h-14">
          {/* Mobile Menu Button — far left on mobile (single hamburger, doubles as close icon) */}
          <button
            className="md:hidden flex-shrink-0"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Open menu"
            data-testid="mobile-menu-btn"
          >
            {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>

          {/* Logo */}
          <div
  className="flex flex-1 items-center justify-center self-center cursor-pointer"
  onClick={() => navigate('/')}
>
  <img
    src="/aditya-logo.png"
    alt="Aditya Retail"
    className="site-logo block h-5 md:h-12 w-auto max-w-[125px] md:max-w-[140px] object-contain relative -top-[1px] md:top-0"
  />
</div>

          {/* Search Bar — desktop only */}
          <div className="hidden md:block flex-1 max-w-2xl mx-8 relative">
            <div className={`flex rounded-lg border-2 transition-colors ${
              isSearchFocused ? 'border-amber-700' : 'border-gray-200'
            }`}>
              <input
                type="text"
                placeholder="Search for Products"
                className="flex-1 px-4 py-3 rounded-l-lg focus:outline-none"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={handleSearchKeyPress}
                onFocus={() => { setIsSearchFocused(true); setShowSuggestions(true); }}
                onBlur={() => setTimeout(() => { setIsSearchFocused(false); setShowSuggestions(false); }, 150)}
                data-testid="search-input"
              />
              <select
                className="px-4 py-3 border-l border-gray-200 bg-gray-50 text-gray-600 focus:outline-none"
                value={selectedSearchCategory}
                onChange={(e) => setSelectedSearchCategory(e.target.value)}
                data-testid="search-category-select"
              >
                <option value="">All Categories</option>
                {navCategories.map(category => (
                  <option key={category.id} value={category.name}>{category.name}</option>
                ))}
              </select>
              <button
                onClick={handleSearch}
                className="px-6 bg-amber-700 text-white rounded-r-lg hover:bg-amber-800 transition-colors"
                data-testid="search-button"
              >
                <Search className="w-5 h-5" />
              </button>
            </div>

            {/* Live suggestions dropdown */}
            {showSuggestions && searchSuggestions.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white rounded-lg shadow-xl border border-gray-100 z-50 overflow-hidden">
                {searchSuggestions.map((product, idx) => (
                  <button
                    key={product.id || idx}
                    onMouseDown={(e) => { e.preventDefault(); handleSuggestionClick(product); }}
                    className="w-full text-left px-4 py-3 hover:bg-amber-50 transition-colors flex items-center justify-between border-b border-gray-50 last:border-0"
                  >
                    <div>
                      <div className="text-sm font-medium text-gray-900">{product.name}</div>
                      <div className="text-xs text-gray-500">{product.brand} · {product.category}</div>
                    </div>
                    {product.price && (
                      <div className="text-sm font-semibold text-amber-700 whitespace-nowrap ml-3">₹{product.price.toLocaleString()}</div>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Mobile icon cluster — search / bell / cart, all inline with logo & hamburger */}
          <div className="flex md:hidden items-center gap-2 ml-auto">
            <button
              onClick={() => setShowMobileSearch(prev => !prev)}
              aria-label="Search"
              className="text-gray-700"
              data-testid="mobile-search-toggle"
            >
              <Search className="w-5 h-5" />
            </button>

            {user && (
              <NotificationBell
                userRole={user.role}
                storeId={user.store_id}
                userId={user.id}
              />
            )}

            <button
              onClick={() => navigate('/checkout')}
              className="relative text-gray-700"
              aria-label="Cart"
            >
              <ShoppingCart className="w-5 h-5" />
              {cartCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-amber-700 text-white rounded-full w-4 h-4 flex items-center justify-center text-[10px]">
                  {cartCount}
                </span>
              )}
            </button>
          </div>

          {/* Collapsible mobile search field — only shows when the search icon above is tapped */}
          {showMobileSearch && (
            <div className="md:hidden w-full order-3 relative">
              <div className={`flex items-center rounded-full border transition-colors bg-gray-50 ${
                isSearchFocused ? 'border-amber-700 bg-white' : 'border-gray-200'
              }`}>
                <Search className="w-4 h-4 text-gray-400 ml-3 flex-shrink-0" />
                <input
                  type="text"
                  placeholder="Search for Products"
                  autoFocus
                  className="flex-1 min-w-0 px-2 py-2.5 bg-transparent text-sm focus:outline-none"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={handleSearchKeyPress}
                  onFocus={() => { setIsSearchFocused(true); setShowSuggestions(true); }}
                  onBlur={() => setTimeout(() => { setIsSearchFocused(false); setShowSuggestions(false); }, 150)}
                />
                <button
                  onClick={handleSearch}
                  className="px-4 py-2.5 text-amber-700 flex-shrink-0"
                  aria-label="Search"
                >
                  <Search className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setShowMobileSearch(false)}
                  className="pr-3 text-gray-400 flex-shrink-0"
                  aria-label="Close search"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {showSuggestions && searchSuggestions.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white rounded-lg shadow-xl border border-gray-100 z-50 overflow-hidden">
                  {searchSuggestions.map((product, idx) => (
                    <button
                      key={product.id || idx}
                      onMouseDown={(e) => { e.preventDefault(); handleSuggestionClick(product); }}
                      className="w-full text-left px-4 py-3 hover:bg-amber-50 transition-colors flex items-center justify-between border-b border-gray-50 last:border-0"
                    >
                      <div className="min-w-0">
                        <div className="text-sm font-medium text-gray-900 truncate">{product.name}</div>
                        <div className="text-xs text-gray-500 truncate">{product.brand} · {product.category}</div>
                      </div>
                      {product.price && (
                        <div className="text-sm font-semibold text-amber-700 whitespace-nowrap ml-3">₹{product.price.toLocaleString()}</div>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Right Section — desktop only; AI Chat, Login/Account and WhatsApp/Contact now live in the mobile bottom bar */}
          <div className="hidden md:flex items-center space-x-4">
            {/* Enhanced AI Chat Button */}
            <button
              onClick={onAIChat}
              className="group relative flex items-center space-x-2 px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-xl font-semibold transition-all duration-300 text-sm"
              data-testid="ai-chat-btn"
            >
              <MessageCircle className="w-5 h-5" />
              <span>AI Chat</span>
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse" />
            </button>

            {/* Notification Bell - Shows for logged-in users */}
            {user && (
              <NotificationBell
                userRole={user.role}
                storeId={user.store_id}
                userId={user.id}
              />
            )}

            {/* User Account - Unified Login */}
            {user ? (
              <div className="relative group">
                <button
                  className="flex items-center space-x-2 px-3 py-2 bg-amber-50 hover:bg-amber-100 rounded-lg transition-colors"
                  data-testid="user-menu-btn"
                >
                  <div className="w-8 h-8 bg-amber-700 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                    {user.first_name?.[0]?.toUpperCase() || user.full_name?.[0]?.toUpperCase() || 'U'}
                  </div>
                  <span className="hidden lg:block text-sm font-medium text-gray-700">
                    {user.first_name || user.full_name?.split(' ')[0] || 'User'}
                  </span>
                </button>

                {/* User Dropdown */}
                <div className="absolute right-0 top-full mt-2 w-56 bg-white rounded-xl shadow-xl border opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                  <div className="p-4 border-b bg-gradient-to-r from-amber-50 to-orange-50 rounded-t-xl">
                    <p className="font-semibold text-gray-900">
                      {user.first_name || user.full_name?.split(' ')[0]} {user.last_name || user.full_name?.split(' ').slice(1).join(' ') || ''}
                    </p>
                    <p className="text-xs text-gray-600 truncate">{user.email}</p>
                    {user.role && user.role !== 'customer' && (
                      <span className="inline-block mt-1 px-2 py-0.5 bg-amber-200 text-amber-800 text-xs rounded-full capitalize">
                        {user.role === 'store_manager' ? 'Store Manager' : user.role}
                      </span>
                    )}
                  </div>
                  <div className="p-2">
                    {/* Show Dashboard link for admin/store users */}
                    {(user.role === 'admin' || user.role === 'super_admin' || user.role === 'manager' || user.role === 'accountant' || user.role === 'sales' || user.role === 'marketing') && (
                      <button
                        onClick={() => navigate('/admin')}
                        className="w-full text-left px-3 py-2.5 text-sm text-gray-700 hover:bg-amber-50 rounded-lg flex items-center space-x-3"
                        data-testid="admin-dashboard-link"
                      >
                        <LayoutDashboard className="w-4 h-4 text-amber-600" />
                        <span>Admin Dashboard</span>
                      </button>
                    )}
                    {/* Show Store Dashboard link for store-side staff on revisit */}
                    {(user.role === 'store_manager' || user.role === 'cashier' || user.role === 'purchase_manager' || user.role === 'sales_executive') && (
                      <button
                        onClick={() => navigate('/store/dashboard')}
                        className="w-full text-left px-3 py-2.5 text-sm text-gray-700 hover:bg-amber-50 rounded-lg flex items-center space-x-3"
                        data-testid="store-dashboard-link"
                      >
                        <LayoutDashboard className="w-4 h-4 text-amber-600" />
                        <span>Your Dashboard</span>
                      </button>
                    )}
                    <button
                      onClick={() => navigate('/my-account')}
                      className="w-full text-left px-3 py-2.5 text-sm text-gray-700 hover:bg-amber-50 rounded-lg flex items-center space-x-3"
                      data-testid="your-account-link"
                    >
                      <User className="w-4 h-4 text-amber-600" />
                      <span>Your Account</span>
                    </button>
                    <button
                      onClick={() => navigate('/my-account?tab=orders')}
                      className="w-full text-left px-3 py-2.5 text-sm text-gray-700 hover:bg-amber-50 rounded-lg flex items-center space-x-3"
                      data-testid="orders-link"
                    >
                      <Package className="w-4 h-4 text-amber-600" />
                      <span>Orders</span>
                    </button>
                    <button
                      onClick={() => navigate('/wishlist')}
                      className="w-full text-left px-3 py-2.5 text-sm text-gray-700 hover:bg-amber-50 rounded-lg flex items-center space-x-3"
                      data-testid="wishlist-link"
                    >
                      <Heart className="w-4 h-4 text-amber-600" />
                      <span>Wishlist</span>
                    </button>
                    <div className="border-t my-2"></div>
                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-3 py-2.5 text-sm text-red-600 hover:bg-red-50 rounded-lg flex items-center space-x-3"
                      data-testid="logout-btn"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Logout</span>
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <button
                onClick={() => setIsLoginOpen(true)}
                className="flex items-center space-x-2 px-4 py-2 bg-amber-700 hover:bg-amber-800 text-white rounded-lg transition-colors text-sm font-medium"
                data-testid="login-btn"
              >
                <User className="w-4 h-4" />
                <span>Login</span>
              </button>
            )}

            {/* Install App Button */}
            <InstallAppButton variant="header" />

            {/* Cart */}
            <button
              onClick={() => navigate('/checkout')}
              className="flex items-center space-x-2 text-gray-600 hover:text-amber-700 transition-colors relative"
            >
              <ShoppingCart className="w-6 h-6" />
              {cartCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-amber-700 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">
                  {cartCount}
                </span>
              )}
              <div>
                <div className="text-sm">₹{cartTotal.toLocaleString()}</div>
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Backdrop */}
      {isMobileMenuOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/50 z-40"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Navigation Menu */}
      <nav className={`
        ${navBg} text-white
        fixed top-0 left-0 h-full w-72 max-w-[80vw] z-50 overflow-y-auto shadow-2xl
        transform transition-transform duration-300 ease-in-out
        ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}
        md:static md:h-auto md:w-auto md:max-w-none md:translate-x-0 md:shadow-none md:overflow-visible md:block
      `}>
        <div className="flex items-center justify-between px-4 py-4 md:hidden border-b border-amber-600">
          <span className="font-semibold text-lg">Menu</span>
          <button onClick={() => setIsMobileMenuOpen(false)} aria-label="Close menu">
            <X className="w-6 h-6" />
          </button>
        </div>
        <div className="w-full px-4 md:px-8">
          {!categoriesReady ? (
            <div className="h-[44px] md:h-[38px]" />
          ) : (
          <div className="flex flex-col md:flex-row md:flex-wrap md:items-center md:justify-center py-2 md:py-2 text-sm md:text-base md:gap-x-6 md:gap-y-1.5">
            <button
              onClick={() => handleCategoryClick(null)}
              className="py-3 md:py-1.5 hover:text-amber-200 transition-colors font-medium text-left w-full md:w-auto border-b border-amber-600/40 md:border-0"
              data-testid="nav-home"
            >
              Home
            </button>
            {navCategories.map(category => {
              const brands = getBrandsForCategory(category.name);
              const hasBrands = brands.length > 0;
              return (
                <div
                  key={category.id}
                  className={`relative group/cat ${category.id.toString().startsWith('dyn-') ? 'nav-cat-new' : ''}`}
                  onMouseEnter={() => { if (window.innerWidth >= 768) setHoveredCategory(category.id); }}
                  onMouseLeave={() => { if (window.innerWidth >= 768) setHoveredCategory(null); }}
                >
                  <button
                    onClick={() => {
                      if (hasBrands) {
                        setHoveredCategory(hoveredCategory === category.id ? null : category.id);
                      } else {
                        handleCategoryClick(category.name);
                      }
                    }}
                    className="py-3 md:py-1.5 hover:text-amber-200 transition-colors text-left flex items-center justify-between gap-0.5 w-full md:w-auto whitespace-nowrap border-b border-amber-600/40 md:border-0"
                    data-testid={`nav-category-${category.name.toLowerCase().replace(/\s+/g, '-')}`}
                  >
                    <span className="font-medium">{category.name}</span>
                    {hasBrands && (
                      <ChevronDown className={`w-4 h-4 opacity-70 transition-transform duration-200 md:hidden ${hoveredCategory === category.id ? 'rotate-180' : ''}`} />
                    )}
                    {hasBrands && <ChevronDown className="w-3 h-3 opacity-60 hidden md:block" />}
                  </button>

                  {/* Brand Dropdown — desktop hover only */}
                  {hasBrands && (
                    <div className={`
                      hidden md:block
                      md:absolute md:left-0 md:top-full md:w-48 md:bg-white md:rounded-b-lg md:shadow-xl md:border md:border-gray-100
                      md:opacity-0 md:invisible md:translate-y-1 md:group-hover/cat:opacity-100 md:group-hover/cat:visible md:group-hover/cat:translate-y-0
                      md:transition-all md:duration-200 md:z-50
                    `}>
                      {/* "All" link */}
                      <button
                        onClick={() => handleCategoryClick(category.name)}
                        className="w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-amber-50 hover:text-amber-800 transition-colors font-medium md:block hidden border-b border-gray-100"
                        data-testid={`nav-brand-all-${category.name.toLowerCase().replace(/\s+/g, '-')}`}
                      >
                        All {category.name}
                      </button>
                      {brands.map(brand => (
                        <button
                          key={brand}
                          onClick={() => handleBrandClick(category.name, brand)}
                          className="w-full text-left px-4 py-2.5 text-sm transition-colors md:text-gray-700 md:hover:bg-amber-50 md:hover:text-amber-800 text-amber-100 hover:text-white"
                          data-testid={`nav-brand-${brand.toLowerCase()}-${category.name.toLowerCase().replace(/\s+/g, '-')}`}
                        >
                          {brand}
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Mobile brand list — toggleable, animated */}
                  {hasBrands && (
                    <div
                      className={`md:hidden overflow-hidden transition-all duration-200 ${
                        isMobileMenuOpen && hoveredCategory === category.id ? 'max-h-96' : 'max-h-0'
                      }`}
                    >
                      <div className="pl-4 pb-2 bg-black/10">
                        <button
                          onClick={() => handleCategoryClick(category.name)}
                          className="block w-full text-left py-2 text-sm text-amber-100 hover:text-white font-medium"
                        >
                          View All {category.name}
                        </button>
                        {brands.map(brand => (
                          <button
                            key={brand}
                            onClick={() => handleBrandClick(category.name, brand)}
                            className="block w-full text-left py-2 text-sm text-amber-200/90 hover:text-white"
                          >
                            {brand}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
            <button
              onClick={() => navigate('/blog')}
              className="py-2 md:py-1.5 hover:text-amber-200 transition-colors"
              data-testid="nav-blog"
            >
              Blog
            </button>
            <button
              onClick={handleContactClick}
              className="py-2 md:py-1.5 hover:text-amber-200 transition-colors"
              data-testid="nav-contact-us"
            >
              Contact Us
            </button>
          </div>
          )}
        </div>
      </nav>

      {/* Login Modal */}
      <Login
        isOpen={isLoginOpen}
        onClose={() => setIsLoginOpen(false)}
        onLogin={handleLogin}
        onSwitchToRegister={switchToRegister}
      />

      {/* Register Modal */}
      <Register
        isOpen={isRegisterOpen}
        onClose={() => setIsRegisterOpen(false)}
        onRegister={handleLogin}
        onSwitchToLogin={switchToLogin}
      />
      </header>
      {/* Spacer to account for fixed header height */}
      <div className="h-[100px] md:h-[200px]"></div>
      {/* Why Buy from Aditya Retail — prominent trust band on every page */}
      <div className="bg-gradient-to-r from-amber-50 to-orange-50 border-b border-amber-100 py-1 md:py-3">
        <div className="max-w-[1400px] mx-auto px-3 md:px-8">
          <WhyBuyStrip variant="inline" />
        </div>
      </div>

      {/* Fixed Mobile Bottom Bar — AI Chat / WhatsApp / Contact Us / Login-Account */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 h-14 bg-white border-t border-gray-200 shadow-[0_-2px_10px_rgba(0,0,0,0.06)] z-50">
        <div className="flex h-full items-center justify-around">
          <button
            onClick={onAIChat}
            className="flex flex-col items-center justify-center text-gray-700 px-2 py-1"
            data-testid="ai-chat-btn-mobile"
          >
            <div className="relative">
              <MessageCircle className="w-5 h-5 text-purple-600" />
              <div className="absolute -top-1 -right-1 w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            </div>
            <span className="text-[10px] mt-0.5">AI Chat</span>
          </button>

          <a
            href={`https://wa.me/${WHATSAPP_NUMBER}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex flex-col items-center justify-center text-gray-700 px-2 py-1"
            data-testid="whatsapp-btn-mobile"
          >
            <svg viewBox="0 0 24 24" className="w-5 h-5" fill="#25D366" aria-hidden="true">
              <path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.79.47 3.47 1.29 4.94L2 22l5.29-1.39c1.42.78 3.03 1.19 4.75 1.19h.01c5.46 0 9.91-4.45 9.91-9.91C21.95 6.45 17.5 2 12.04 2zm5.76 14.11c-.24.68-1.4 1.3-1.93 1.38-.49.08-1.11.11-1.79-.11-.41-.13-.94-.3-1.62-.6-2.85-1.23-4.71-4.1-4.85-4.29-.14-.19-1.16-1.55-1.16-2.95 0-1.41.74-2.1 1-2.39.26-.29.57-.36.76-.36.19 0 .38 0 .55.01.18.01.41-.03.64.49.24.58.81 2 .88 2.14.07.14.11.31.02.5-.09.19-.14.31-.28.48-.14.17-.29.37-.42.5-.14.14-.28.29-.12.57.16.28.71 1.17 1.52 1.9 1.05.94 1.93 1.23 2.21 1.37.28.14.44.12.61-.07.17-.19.71-.83.9-1.11.19-.28.38-.24.64-.14.26.09 1.66.78 1.94.92.28.14.47.21.54.33.07.12.07.7-.17 1.38z"/>
            </svg>
            <span className="text-[10px] mt-0.5">WhatsApp</span>
          </a>

          <button
            onClick={handleContactClick}
            className="flex flex-col items-center justify-center text-gray-700 px-2 py-1"
            data-testid="contact-us-btn-mobile"
          >
            <Phone className="w-5 h-5" />
            <span className="text-[10px] mt-0.5">Contact</span>
          </button>

          <button
            onClick={() => (user ? navigate('/my-account') : setIsLoginOpen(true))}
            className="flex flex-col items-center justify-center text-gray-700 px-2 py-1"
            data-testid="account-btn-mobile"
          >
            {user ? (
              <div className="w-5 h-5 bg-amber-700 rounded-full flex items-center justify-center text-white font-semibold text-[10px]">
                {user.first_name?.[0]?.toUpperCase() || user.full_name?.[0]?.toUpperCase() || 'U'}
              </div>
            ) : (
              <User className="w-5 h-5" />
            )}
            <span className="text-[10px] mt-0.5">{user ? 'Account' : 'Login'}</span>
          </button>
        </div>
      </div>
    </>
  );
};

export default Header;