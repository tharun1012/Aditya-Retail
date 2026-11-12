import React, { useState, useEffect } from 'react';
import { Plus, Edit3, Trash2, Upload, Image, Save, X, Eye, Package, Users, BarChart3, Settings } from 'lucide-react';
import { useProducts } from '../hooks/useProducts';
import { productAPI } from '../services/api';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('products');
  const [showProductForm, setShowProductForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const { products, loading, refresh } = useProducts();

  const [productForm, setProductForm] = useState({
    name: '',
    description: '',
    short_description: '',
    sku: '',
    price: '',
    original_price: '',
    cost_price: '',
    brand: '',
    category: '',
    images: ['', '', '', ''], // Support for 4 images
    features: [''],
    specifications: {},
    stock_quantity: '',
    reorder_level: '10',
    weight: '1',
    dimensions: { length: '', width: '', height: '' },
    is_featured: false,
    seo_title: '',
    seo_description: ''
  });

  const [specForm, setSpecForm] = useState([
    { key: '', value: '' }
  ]);

  const categories = [
    'Built-In Microven', 'Microwave', 'Cooking Range', 'Induction', 
    '10 KG TOP LOAD WM', '226 Liters Single Door Fridge', 'Hood',
    'Dishwasher', 'Chimney', 'Oven', 'Washing Machine', 'Fridge'
  ];

  const brands = ['Bosch', 'Siemens', 'Hindware', 'Dona', 'Dino'];

  const handleInputChange = (field, value) => {
    setProductForm(prev => ({ ...prev, [field]: value }));
  };

  const handleImageChange = (index, value) => {
    const newImages = [...productForm.images];
    newImages[index] = value;
    setProductForm(prev => ({ ...prev, images: newImages }));
  };

  const handleFeatureChange = (index, value) => {
    const newFeatures = [...productForm.features];
    newFeatures[index] = value;
    setProductForm(prev => ({ ...prev, features: newFeatures }));
  };

  const addFeature = () => {
    setProductForm(prev => ({ ...prev, features: [...prev.features, ''] }));
  };

  const removeFeature = (index) => {
    const newFeatures = productForm.features.filter((_, i) => i !== index);
    setProductForm(prev => ({ ...prev, features: newFeatures }));
  };

  const handleSpecChange = (index, field, value) => {
    const newSpecs = [...specForm];
    newSpecs[index][field] = value;
    setSpecForm(newSpecs);
    
    // Update specifications object
    const specsObj = {};
    specForm.forEach(spec => {
      if (spec.key && spec.value) {
        specsObj[spec.key] = spec.value;
      }
    });
    setProductForm(prev => ({ ...prev, specifications: specsObj }));
  };

  const addSpecification = () => {
    setSpecForm(prev => [...prev, { key: '', value: '' }]);
  };

  const removeSpecification = (index) => {
    const newSpecs = specForm.filter((_, i) => i !== index);
    setSpecForm(newSpecs);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const productData = {
        ...productForm,
        price: parseFloat(productForm.price),
        original_price: productForm.original_price ? parseFloat(productForm.original_price) : null,
        cost_price: productForm.cost_price ? parseFloat(productForm.cost_price) : null,
        stock_quantity: parseInt(productForm.stock_quantity),
        reorder_level: parseInt(productForm.reorder_level),
        weight: parseFloat(productForm.weight),
        images: productForm.images.filter(img => img.trim() !== ''),
        features: productForm.features.filter(feature => feature.trim() !== '')
      };

      if (editingProduct) {
        // Update existing product
        await productAPI.updateProduct(editingProduct.id, productData);
      } else {
        // Create new product
        await productAPI.createProduct(productData);
      }

      setShowProductForm(false);
      setEditingProduct(null);
      resetForm();
      refresh();
    } catch (error) {
      console.error('Error saving product:', error);
    }
  };

  const resetForm = () => {
    setProductForm({
      name: '',
      description: '',
      short_description: '',
      sku: '',
      price: '',
      original_price: '',
      cost_price: '',
      brand: '',
      category: '',
      images: ['', '', '', ''],
      features: [''],
      specifications: {},
      stock_quantity: '',
      reorder_level: '10',
      weight: '1',
      dimensions: { length: '', width: '', height: '' },
      is_featured: false,
      seo_title: '',
      seo_description: ''
    });
    setSpecForm([{ key: '', value: '' }]);
  };

  const editProduct = (product) => {
    setEditingProduct(product);
    setProductForm({
      ...product,
      images: [...product.images, '', '', '', ''].slice(0, 4),
      features: product.features.length > 0 ? product.features : ['']
    });
    
    // Convert specifications to form format
    const specs = Object.entries(product.specifications || {}).map(([key, value]) => ({ key, value }));
    setSpecForm(specs.length > 0 ? specs : [{ key: '', value: '' }]);
    
    setShowProductForm(true);
  };

  const deleteProduct = async (productId) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await productAPI.deleteProduct(productId);
        refresh();
      } catch (error) {
        console.error('Error deleting product:', error);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">
              🤖 AI Ecommerce Admin Dashboard
            </h1>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Welcome, Admin</span>
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                A
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex space-x-8">
          {/* Sidebar */}
          <div className="w-64 bg-white rounded-xl shadow-sm p-6">
            <nav className="space-y-2">
              {[
                { id: 'products', label: 'Products', icon: Package },
                { id: 'orders', label: 'Orders', icon: BarChart3 },
                { id: 'customers', label: 'Customers', icon: Users },
                { id: 'settings', label: 'Settings', icon: Settings }
              ].map(item => {
                const IconComponent = item.icon;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                      activeTab === item.id
                        ? 'bg-blue-50 text-blue-700 border-l-4 border-blue-700'
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <IconComponent className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {activeTab === 'products' && (
              <div>
                {/* Products Header */}
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">Product Management</h2>
                  <button
                    onClick={() => {
                      resetForm();
                      setShowProductForm(true);
                    }}
                    className="flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-3 rounded-xl font-medium transition-all duration-300 transform hover:scale-105"
                  >
                    <Plus className="w-5 h-5" />
                    <span>Add New Product</span>
                  </button>
                </div>

                {/* Product Form Modal */}
                {showProductForm && (
                  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
                      <div className="p-6 border-b">
                        <div className="flex items-center justify-between">
                          <h3 className="text-xl font-semibold text-gray-900">
                            {editingProduct ? 'Edit Product' : 'Add New Product'}
                          </h3>
                          <button
                            onClick={() => {
                              setShowProductForm(false);
                              setEditingProduct(null);
                              resetForm();
                            }}
                            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                          >
                            <X className="w-6 h-6" />
                          </button>
                        </div>
                      </div>

                      <form onSubmit={handleSubmit} className="p-6 space-y-6">
                        {/* Basic Information */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Product Name *</label>
                            <input
                              type="text"
                              value={productForm.name}
                              onChange={(e) => handleInputChange('name', e.target.value)}
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              required
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">SKU *</label>
                            <input
                              type="text"
                              value={productForm.sku}
                              onChange={(e) => handleInputChange('sku', e.target.value)}
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              required
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Brand *</label>
                            <select
                              value={productForm.brand}
                              onChange={(e) => handleInputChange('brand', e.target.value)}
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              required
                            >
                              <option value="">Select Brand</option>
                              {brands.map(brand => (
                                <option key={brand} value={brand}>{brand}</option>
                              ))}
                            </select>
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Category *</label>
                            <select
                              value={productForm.category}
                              onChange={(e) => handleInputChange('category', e.target.value)}
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              required
                            >
                              <option value="">Select Category</option>
                              {categories.map(category => (
                                <option key={category} value={category}>{category}</option>
                              ))}
                            </select>
                          </div>
                        </div>

                        {/* Pricing */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Selling Price *</label>
                            <input
                              type="number"
                              value={productForm.price}
                              onChange={(e) => handleInputChange('price', e.target.value)}
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              required
                              step="0.01"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Original Price</label>
                            <input
                              type="number"
                              value={productForm.original_price}
                              onChange={(e) => handleInputChange('original_price', e.target.value)}
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              step="0.01"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Cost Price</label>
                            <input
                              type="number"
                              value={productForm.cost_price}
                              onChange={(e) => handleInputChange('cost_price', e.target.value)}
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              step="0.01"
                            />
                          </div>
                        </div>

                        {/* Images */}
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-4">Product Images (Up to 4)</label>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {productForm.images.map((image, index) => (
                              <div key={index}>
                                <label className="block text-xs text-gray-500 mb-1">Image {index + 1}</label>
                                <input
                                  type="url"
                                  value={image}
                                  onChange={(e) => handleImageChange(index, e.target.value)}
                                  placeholder="Enter image URL"
                                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
                                {image && (
                                  <div className="mt-2">
                                    <img 
                                      src={image} 
                                      alt={`Preview ${index + 1}`}
                                      className="w-full h-32 object-cover rounded-lg border"
                                      onError={(e) => {
                                        e.target.style.display = 'none';
                                      }}
                                    />
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Descriptions */}
                        <div className="space-y-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Short Description</label>
                            <input
                              type="text"
                              value={productForm.short_description}
                              onChange={(e) => handleInputChange('short_description', e.target.value)}
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              placeholder="Brief product description"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Full Description</label>
                            <textarea
                              value={productForm.description}
                              onChange={(e) => handleInputChange('description', e.target.value)}
                              rows="4"
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              placeholder="Detailed product description"
                            />
                          </div>
                        </div>

                        {/* Features */}
                        <div>
                          <div className="flex items-center justify-between mb-4">
                            <label className="block text-sm font-medium text-gray-700">Key Features</label>
                            <button
                              type="button"
                              onClick={addFeature}
                              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                            >
                              + Add Feature
                            </button>
                          </div>
                          <div className="space-y-2">
                            {productForm.features.map((feature, index) => (
                              <div key={index} className="flex items-center space-x-2">
                                <input
                                  type="text"
                                  value={feature}
                                  onChange={(e) => handleFeatureChange(index, e.target.value)}
                                  placeholder={`Feature ${index + 1}`}
                                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
                                {productForm.features.length > 1 && (
                                  <button
                                    type="button"
                                    onClick={() => removeFeature(index)}
                                    className="p-2 text-red-500 hover:text-red-700"
                                  >
                                    <Trash2 className="w-4 h-4" />
                                  </button>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Technical Specifications */}
                        <div>
                          <div className="flex items-center justify-between mb-4">
                            <label className="block text-sm font-medium text-gray-700">Technical Specifications</label>
                            <button
                              type="button"
                              onClick={addSpecification}
                              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                            >
                              + Add Specification
                            </button>
                          </div>
                          <div className="space-y-2">
                            {specForm.map((spec, index) => (
                              <div key={index} className="flex items-center space-x-2">
                                <input
                                  type="text"
                                  value={spec.key}
                                  onChange={(e) => handleSpecChange(index, 'key', e.target.value)}
                                  placeholder="Specification name"
                                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
                                <input
                                  type="text"
                                  value={spec.value}
                                  onChange={(e) => handleSpecChange(index, 'value', e.target.value)}
                                  placeholder="Specification value"
                                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
                                {specForm.length > 1 && (
                                  <button
                                    type="button"
                                    onClick={() => removeSpecification(index)}
                                    className="p-2 text-red-500 hover:text-red-700"
                                  >
                                    <Trash2 className="w-4 h-4" />
                                  </button>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Inventory & Physical Properties */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Stock Quantity *</label>
                            <input
                              type="number"
                              value={productForm.stock_quantity}
                              onChange={(e) => handleInputChange('stock_quantity', e.target.value)}
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              required
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Reorder Level</label>
                            <input
                              type="number"
                              value={productForm.reorder_level}
                              onChange={(e) => handleInputChange('reorder_level', e.target.value)}
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Weight (kg)</label>
                            <input
                              type="number"
                              value={productForm.weight}
                              onChange={(e) => handleInputChange('weight', e.target.value)}
                              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              step="0.1"
                            />
                          </div>

                          <div>
                            <label className="flex items-center space-x-2 text-sm font-medium text-gray-700">
                              <input
                                type="checkbox"
                                checked={productForm.is_featured}
                                onChange={(e) => handleInputChange('is_featured', e.target.checked)}
                                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                              />
                              <span>Featured Product</span>
                            </label>
                          </div>
                        </div>

                        {/* Form Actions */}
                        <div className="flex items-center justify-end space-x-4 pt-6 border-t">
                          <button
                            type="button"
                            onClick={() => {
                              setShowProductForm(false);
                              setEditingProduct(null);
                              resetForm();
                            }}
                            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                          >
                            Cancel
                          </button>
                          <button
                            type="submit"
                            className="flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 rounded-lg font-medium transition-all duration-300"
                          >
                            <Save className="w-5 h-5" />
                            <span>{editingProduct ? 'Update Product' : 'Create Product'}</span>
                          </button>
                        </div>
                      </form>
                    </div>
                  </div>
                )}

                {/* Products List */}
                <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Product</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                          <th className="px-6 py-4 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {loading ? (
                          <tr>
                            <td colSpan="6" className="px-6 py-12 text-center text-gray-500">
                              Loading products...
                            </td>
                          </tr>
                        ) : products.length === 0 ? (
                          <tr>
                            <td colSpan="6" className="px-6 py-12 text-center text-gray-500">
                              No products found. Add your first product to get started.
                            </td>
                          </tr>
                        ) : (
                          products.map((product) => (
                            <tr key={product.id} className="hover:bg-gray-50">
                              <td className="px-6 py-4">
                                <div className="flex items-center">
                                  <div className="flex-shrink-0 h-16 w-16">
                                    <img
                                      className="h-16 w-16 rounded-lg object-cover border"
                                      src={product.images?.[0] || '/api/placeholder/64/64'}
                                      alt={product.name}
                                      onError={(e) => {
                                        e.target.src = '/api/placeholder/64/64';
                                      }}
                                    />
                                  </div>
                                  <div className="ml-4">
                                    <div className="text-sm font-medium text-gray-900">{product.name}</div>
                                    <div className="text-sm text-gray-500">{product.brand}</div>
                                  </div>
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {product.category}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                ₹{product.price?.toLocaleString()}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                  product.stock_quantity > 10 
                                    ? 'bg-green-100 text-green-800'
                                    : product.stock_quantity > 0
                                    ? 'bg-yellow-100 text-yellow-800'
                                    : 'bg-red-100 text-red-800'
                                }`}>
                                  {product.stock_quantity} in stock
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                  product.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                }`}>
                                  {product.is_active ? 'Active' : 'Inactive'}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                <div className="flex items-center justify-end space-x-2">
                                  <button
                                    onClick={() => editProduct(product)}
                                    className="text-blue-600 hover:text-blue-900 p-2 hover:bg-blue-50 rounded-lg transition-colors"
                                  >
                                    <Edit3 className="w-4 h-4" />
                                  </button>
                                  <button
                                    onClick={() => deleteProduct(product.id)}
                                    className="text-red-600 hover:text-red-900 p-2 hover:bg-red-50 rounded-lg transition-colors"
                                  >
                                    <Trash2 className="w-4 h-4" />
                                  </button>
                                </div>
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {activeTab !== 'products' && (
              <div className="bg-white rounded-xl shadow-sm p-12 text-center">
                <div className="text-gray-400 mb-4">
                  <Package className="w-16 h-16 mx-auto" />
                </div>
                <h3 className="text-xl font-semibold text-gray-600 mb-2">
                  {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} Management
                </h3>
                <p className="text-gray-500">
                  This section is coming soon. Focus on product management for now.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;