import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { LogOut, Package, Upload, Download, RefreshCw, Users } from 'lucide-react';

const SimpleAdminDashboard = ({ user, onLogout }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalCategories: 0,
    totalBrands: 0
  });

  useEffect(() => {
    fetchProducts();
    fetchStats();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/products`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setProducts(data.products || []);
      }
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/products`);
      const data = await response.json();
      
      if (data.status === 'success') {
        const products = data.products || [];
        const brands = [...new Set(products.map(p => p.brand))];
        const categories = [...new Set(products.map(p => p.category))];
        
        setStats({
          totalProducts: products.length,
          totalCategories: categories.length,
          totalBrands: brands.length
        });
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const downloadCSV = () => {
    // Use the direct download endpoint
    const downloadUrl = `${BACKEND_URL}/api/download/products-csv`;
    
    console.log('Starting CSV download from:', downloadUrl);
    
    // Method 1: Direct window.open (most reliable)
    try {
      window.open(downloadUrl, '_blank');
      
      setTimeout(() => {
        alert('✅ CSV download started! If download didn\'t start automatically, check if pop-ups are blocked.\n\nFile: products_for_update.csv\nLocation: Your Downloads folder');
      }, 1000);
      
    } catch (error) {
      console.error('Download failed:', error);
      
      // Fallback: Copy URL to clipboard
      navigator.clipboard.writeText(downloadUrl).then(() => {
        alert(`⚠️ Download failed. URL copied to clipboard:\n${downloadUrl}\n\nPaste this URL in your browser to download the CSV file.`);
      }).catch(() => {
        alert(`⚠️ Download failed. Please copy this URL manually and paste in browser:\n${downloadUrl}`);
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <Package className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
                <p className="text-sm text-gray-600">Aditya Retail Management Portal</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">Welcome, {user?.first_name || 'Admin'}</p>
                <p className="text-xs text-gray-500">{user?.email}</p>
              </div>
              <button
                onClick={onLogout}
                className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <div className="flex items-center">
              <Package className="w-8 h-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Products</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalProducts}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <div className="flex items-center">
              <Users className="w-8 h-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Brands</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalBrands}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <div className="flex items-center">
              <RefreshCw className="w-8 h-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Categories</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalCategories}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Bulk Product Management Section */}
        <div className="bg-white rounded-xl shadow-sm border mb-8">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold text-gray-900">Bulk Product Management</h2>
            <p className="text-gray-600 mt-1">Update all your products with comprehensive details</p>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* Export Section */}
              <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
                <div className="flex items-center mb-4">
                  <Download className="w-6 h-6 text-blue-600" />
                  <h3 className="text-lg font-semibold text-blue-900 ml-2">Export Products</h3>
                </div>
                <p className="text-blue-700 mb-4">
                  Download your current product catalog as CSV for editing with complete specifications, images, and features.
                </p>
                <button
                  onClick={downloadCSV}
                  className="flex items-center space-x-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Download className="w-5 h-5" />
                  <span>Download CSV</span>
                </button>
                <div className="mt-4 text-sm text-blue-600">
                  <p><strong>Includes:</strong></p>
                  <ul className="list-disc list-inside mt-2 space-y-1">
                    <li>Complete specifications (dimensions, power, capacity)</li>
                    <li>Multiple image slots (5 per product)</li>
                    <li>Features, benefits, and installation guides</li>
                    <li>Warranty and service information</li>
                  </ul>
                </div>
              </div>

              {/* Import Section */}
              <div className="bg-green-50 p-6 rounded-lg border border-green-200">
                <div className="flex items-center mb-4">
                  <Upload className="w-6 h-6 text-green-600" />
                  <h3 className="text-lg font-semibold text-green-900 ml-2">Import Updated Products</h3>
                </div>
                <p className="text-green-700 mb-4">
                  After editing the CSV with complete product details, upload it back to update all products at once.
                </p>
                <div className="space-y-3">
                  <input
                    type="file"
                    accept=".csv"
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-green-600 file:text-white hover:file:bg-green-700"
                  />
                  <button className="flex items-center space-x-2 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors w-full justify-center">
                    <Upload className="w-5 h-5" />
                    <span>Upload & Update Products</span>
                  </button>
                </div>
                <div className="mt-4 text-sm text-green-600">
                  <p><strong>AI Enhancement:</strong></p>
                  <p>All updated details will be automatically available to AI agents for customer queries.</p>
                </div>
              </div>
            </div>
            
            {/* Instructions */}
            <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <h4 className="font-semibold text-yellow-900 mb-3">📋 How to Update Your Products:</h4>
              <ol className="list-decimal list-inside space-y-2 text-yellow-800">
                <li><strong>Download CSV:</strong> Export your current products using the download button</li>
                <li><strong>Edit Details:</strong> Add specifications, images, features, and descriptions in Excel/Google Sheets</li>
                <li><strong>Upload CSV:</strong> Import the updated file to apply changes to all products</li>
                <li><strong>Test AI:</strong> Verify AI agents can answer detailed product questions</li>
              </ol>
              
              <div className="mt-4 p-4 bg-white rounded border">
                <p className="text-sm text-gray-700">
                  <strong>Current Status:</strong> {stats.totalProducts} products ready for enhancement. 
                  Each product can have up to 5 images, detailed specifications, installation guides, and AI-powered recommendations.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Product List */}
        <div className="bg-white rounded-xl shadow-sm border">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold text-gray-900">Current Products</h2>
            <p className="text-gray-600 mt-1">Overview of your product catalog</p>
          </div>
          
          <div className="overflow-x-auto">
            {loading ? (
              <div className="p-8 text-center">
                <RefreshCw className="w-8 h-8 animate-spin mx-auto text-gray-400" />
                <p className="text-gray-600 mt-2">Loading products...</p>
              </div>
            ) : (
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Product</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Brand</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {products.slice(0, 10).map((product) => (
                    <tr key={product.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <img
                            className="w-12 h-12 rounded-lg object-cover"
                            src={product.images?.[0] || product.image}
                            alt={product.name}
                          />
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{product.name}</div>
                            <div className="text-sm text-gray-500">{product.short_description}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{product.brand}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{product.category}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₹{product.price?.toLocaleString()}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          product.stock > 10 ? 'bg-green-100 text-green-800' :
                          product.stock > 0 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {product.stock} in stock
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            
            {products.length > 10 && (
              <div className="px-6 py-4 bg-gray-50 border-t text-sm text-gray-600">
                Showing 10 of {products.length} products. Use the CSV export to manage all products.
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default SimpleAdminDashboard;