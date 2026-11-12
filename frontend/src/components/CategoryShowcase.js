import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { Link } from 'react-router-dom';
import { ArrowRight, Eye, Image as ImageIcon, Sparkles } from 'lucide-react';


const CategoryShowcase = ({ onCategorySelect }) => {
  const [categoryImages, setCategoryImages] = useState({});
  const [loadingImages, setLoadingImages] = useState(true);

  // Default showcase categories with fallback images and attractive taglines
  const showcaseCategories = [
    {
      id: 1,
      name: "Chimney",
      tagline: "Premium Kitchen Hoods",
      description: "Keep your kitchen fresh & smoke-free",
      fallbackImage: "https://media3.bsh-group.com/Product_Shots/5120x/MCSA01858394_DIB098G50I_ChimneyHood_Bosch_STP_def.webp",
      subcategories: ["Island Hood", "Wall-Mounted", "Telescopic", "Inclined Hood", "Box Design", "90cm Width"],
      count: 15
    },
    {
      id: 2,
      name: "Gas Hob",
      tagline: "Wide Range of Hobs",
      description: "Cook like a pro with precision burners",
      fallbackImage: "https://media3.bsh-group.com/Product_Shots/900x/MCSA01656668_PRA3A6D70_def.webp",
      subcategories: ["60cm", "75cm", "90cm", "Domino 30cm", "Wok Burner", "stepFlame Technology"],
      count: 21
    },
    {
      id: 3,
      name: "Induction Hob",
      tagline: "Smart Induction Cooking",
      description: "Energy-efficient & ultra-fast heating",
      fallbackImage: "https://media3.bsh-group.com/Product_Shots/900x/14486486_PVQ811F15E_STP_def.webp",
      subcategories: ["60cm", "80cm", "Domino 30cm", "InductionAir", "flexInduction", "powerMove Plus"],
      count: 8
    },
    {
      id: 4,
      name: "Oven",
      tagline: "Built-in Excellence",
      description: "Professional baking at home",
      fallbackImage: "https://media3.bsh-group.com/Product_Shots/5120x/26055174_HS736G3B1I_STP_def.webp",
      subcategories: ["Built-In Oven", "Microwave", "Steam Oven", "Coffee Machine", "Warming Drawer", "Pyrolytic Cleaning"],
      count: 11
    },
    {
      id: 5,
      name: "Mixer Grinder",
      tagline: "Powerful Kitchen Partners",
      description: "From grinding to blending - do it all",
      fallbackImage: "https://media3.bsh-group.com/Product_Shots/5120x/22535822_MGM8856BIN_STP_D_def.webp",
      subcategories: ["500W", "600W", "750W", "1000W", "TrueMixx Series", "Stone Pounding"],
      count: 19
    },
    {
      id: 6,
      name: "Washing Machine",
      tagline: "Laundry Made Easy",
      description: "Gentle care for your clothes",
      fallbackImage: "https://media3.bsh-group.com/Product_Shots/900x/26214365_WGA2420SIN_STP_def.webp",
      subcategories: ["Front Load", "9 KG", "10 KG", "AntiWrinkle", "EcoSilence Drive", "SpeedPerfect"],
      count: 2
    },
    {
      id: 7,
      name: "Dishwasher",
      tagline: "Spotless Every Time",
      description: "Save time, water & energy",
      fallbackImage: "https://media3.bsh-group.com/Product_Shots/5120x/16535439_SMS6ZCW37Q_STP_def.webp",
      subcategories: ["Free-Standing", "Fully Integrated", "Semi-Integrated", "12-14 Place Settings", "Home Connect", "Zeolith Drying"],
      count: 9
    },
    {
      id: 8,
      name: "Refrigerator",
      tagline: "Keep It Fresh",
      description: "Advanced cooling technology",
      fallbackImage: "https://media3.bsh-group.com/Product_Shots/5120x/23256751_CMC36K03GI_STP_def.webp",
      subcategories: ["Built-In Fridge", "Built-In Freezer", "Freestanding", "noFrost", "hyperFresh", "Home Connect"],
      count: 3
    },
    {
      id: 9,
      name: "Air Fryer",
      tagline: "Healthy Frying",
      description: "Crispy food with less oil",
      fallbackImage: "https://media3.bsh-group.com/Product_Shots/5120x/25767357_MAF671B0GB_STP_def.webp",
      subcategories: ["Series 2", "Series 6", "6L Capacity", "8L Capacity", "Digital Display", "11 Auto Programs"],
      count: 4
    },
    {
      id: 10,
      name: "Coffee Machine",
      tagline: "Barista at Home",
      description: "Perfect espresso every morning",
      fallbackImage: "https://media3.bsh-group.com/Product_Shots/5120x/19924515_CTL7181B0_STP_def.webp",
      subcategories: ["Built-In", "Fully Automatic", "Series 2", "Series 6", "Series 8", "Home Connect"],
      count: 3
    }
  ];

  // Fetch product images for each category from the backend
  useEffect(() => {
    const fetchCategoryImages = async () => {
      try {
        const images = {};
        const categoryCounts = {};
        
        // Fetch products to get real images for each category
        const response = await fetch(`${BACKEND_URL}/api/products?limit=200`);
        if (response.ok) {
          const data = await response.json();
          const products = data.products || data || [];
          
          // Group products by category and get first image
          products.forEach(product => {
            const category = product.category;
            if (category) {
              // Count products per category
              categoryCounts[category] = (categoryCounts[category] || 0) + 1;
              
              // Get first image for category if not already set
              if (!images[category] && product.images && product.images.length > 0) {
                images[category] = product.images[0];
              }
            }
          });
        }
        
        setCategoryImages(images);
        setLoadingImages(false);
      } catch (error) {
        console.error('Error fetching category images:', error);
        setLoadingImages(false);
      }
    };

    fetchCategoryImages();
  }, []);

  // Get image for a category - use fetched image if available, otherwise fallback
  const getCategoryImage = (category) => {
    return categoryImages[category.name] || category.fallbackImage;
  };

  // Handle image load error - use fallback
  const handleImageError = (e, category) => {
    e.target.onerror = null; // Prevent infinite loop
    e.target.src = category.fallbackImage;
  };

  return (
    <div className="bg-gradient-to-b from-gray-50 to-white py-16">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 bg-copper/10 border border-copper/20 px-4 py-2 rounded-full mb-4">
            <Sparkles className="w-4 h-4 text-copper" />
            <span className="text-copper font-medium text-sm">Explore Categories</span>
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Shop by Category</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Explore our wide range of premium home appliances from trusted brands like Bosch, Siemens, Electrolux & Hindware
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {showcaseCategories.map((category) => (
            <Link
              key={category.id}
              to={`/${category.name.toLowerCase().replace(/\s+/g, '-')}`}
              className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden group cursor-pointer block border border-gray-100 hover:border-copper/30"
            >
              {/* Category Image */}
              <div className="relative h-52 bg-gradient-to-br from-gray-50 to-gray-100 overflow-hidden">
                {loadingImages ? (
                  <div className="w-full h-full flex items-center justify-center bg-gray-200 animate-pulse">
                    <ImageIcon className="w-12 h-12 text-gray-400" />
                  </div>
                ) : (
                  <img
                    src={getCategoryImage(category)}
                    alt={`${category.name} - Browse ${category.name} appliances and products at Aditya Retail`}
                    loading="lazy"
                    decoding="async"
                    onError={(e) => handleImageError(e, category)}
                    className="w-full h-full object-contain bg-white group-hover:scale-105 transition-transform duration-500"
                  />
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                
                {/* Tagline Badge */}
                <div className="absolute top-4 left-4 bg-gradient-to-r from-copper to-amber-600 text-white px-3 py-1.5 rounded-full text-xs font-semibold shadow-lg">
                  {category.tagline}
                </div>
                
                <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <Eye className="w-5 h-5 text-gray-700" />
                </div>
              </div>

              {/* Category Info */}
              <div className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-xl font-bold text-gray-900 group-hover:text-copper transition-colors">{category.name}</h3>
                  <div className="flex items-center space-x-2">
                    {category.count && (
                      <span className="bg-red-100 text-red-700 text-xs font-semibold px-2.5 py-1 rounded-full">
                        {category.count} products
                      </span>
                    )}
                    <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-copper group-hover:translate-x-1 transition-all duration-300" />
                  </div>
                </div>
                
                {/* Description */}
                <p className="text-sm text-gray-500 mb-4">{category.description}</p>

                {/* Subcategories */}
                <div className="space-y-2">
                  {category.subcategories.slice(0, 4).map((subcategory, index) => (
                    <div key={index} className="flex items-center text-sm text-gray-600 hover:text-copper transition-colors">
                      <div className="w-1.5 h-1.5 bg-copper rounded-full mr-2 opacity-60" />
                      {subcategory}
                    </div>
                  ))}
                  {category.subcategories.length > 4 && (
                    <div className="text-sm text-gray-500 font-medium">
                      +{category.subcategories.length - 4} more categories
                    </div>
                  )}
                </div>

                {/* See All Button */}
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <div className="text-red-700 hover:text-red-800 font-medium text-sm flex items-center space-x-2 group-hover:underline">
                    <span>See all</span>
                    <ArrowRight className="w-4 h-4" />
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CategoryShowcase;
