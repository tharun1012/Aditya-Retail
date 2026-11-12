import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { Edit, Trash2, Plus, Save, X, Upload, Image as ImageIcon } from 'lucide-react';

const ProductManager = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingProduct, setEditingProduct] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [searchTerm, setSearchTerm] = useState('');

  
  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/products`);
      const data = await response.json();
      if (data.status === 'success') {
        setProducts(data.products);
      }
    } catch (error) {
      showMessage('error', 'Error fetching products: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 5000);
  };

  const handleEdit = (product) => {
    setEditingProduct({...product});
    setShowAddForm(false);
  };

  const handleDelete = async (productId) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;

    try {
      const response = await fetch(`${BACKEND_URL}/api/products/${productId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        showMessage('success', 'Product deleted successfully');
        fetchProducts();
      } else {
        showMessage('error', 'Failed to delete product');
      }
    } catch (error) {
      showMessage('error', 'Error: ' + error.message);
    }
  };

  const handleSave = async () => {
    if (!editingProduct) return;

    try {
      const url = editingProduct.id 
        ? `${BACKEND_URL}/api/products/${editingProduct.id}`
        : `${BACKEND_URL}/api/products`;
      
      const method = editingProduct.id ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editingProduct)
      });

      if (response.ok) {
        showMessage('success', `Product ${editingProduct.id ? 'updated' : 'created'} successfully`);
        setEditingProduct(null);
        setShowAddForm(false);
        fetchProducts();
      } else {
        const error = await response.json();
        showMessage('error', error.message || 'Failed to save product');
      }
    } catch (error) {
      showMessage('error', 'Error: ' + error.message);
    }
  };

  const handleAddNew = () => {
    setEditingProduct({
      name: '',
      model_number: '',
      brand: '',
      category: '',
      price: 0,
      original_price: 0,
      stock_quantity: 0,
      description: '',
      image: '',
      images: []
    });
    setShowAddForm(true);
  };

  const updateField = (field, value) => {
    setEditingProduct(prev => ({ ...prev, [field]: value }));
  };

  const filteredProducts = products.filter(p => 
    p.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.modelNumber?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.category?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl">Loading products...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Product Manager</h1>
          <button
            onClick={handleAddNew}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Add New Product
          </button>
        </div>

        {/* Message */}
        {message.text && (
          <div className={`mb-4 p-4 rounded-lg ${
            message.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {message.text}
            <button onClick={() => setMessage({ type: '', text: '' })} className="float-right">
              <X className="w-5 h-5" />
            </button>
          </div>
        )}

        {/* Search */}
        <div className="mb-6">
          <input
            type="text"
            placeholder="Search products by name, model, or category..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full p-3 border rounded-lg"
          />
        </div>

        {/* Edit/Add Form */}
        {(editingProduct || showAddForm) && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-2xl font-bold mb-6">
              {editingProduct?.id ? 'Edit Product' : 'Add New Product'}
            </h2>

            <div className="grid grid-cols-2 gap-6">
              {/* Basic Info */}
              <div>
                <label className="block text-sm font-medium mb-2">Product Name *</label>
                <input
                  type="text"
                  value={editingProduct?.name || ''}
                  onChange={(e) => updateField('name', e.target.value)}
                  className="w-full p-3 border rounded-lg"
                  placeholder="e.g., Bosch Series 6 Air Fryer"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Model Number *</label>
                <input
                  type="text"
                  value={editingProduct?.model_number || editingProduct?.modelNumber || ''}
                  onChange={(e) => updateField('model_number', e.target.value)}
                  className="w-full p-3 border rounded-lg"
                  placeholder="e.g., MAF671B5IN"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Brand *</label>
                <select
                  value={editingProduct?.brand || ''}
                  onChange={(e) => updateField('brand', e.target.value)}
                  className="w-full p-3 border rounded-lg"
                >
                  <option value="">Select Brand</option>
                  <option value="Bosch">Bosch</option>
                  <option value="Siemens">Siemens</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Category *</label>
                <select
                  value={editingProduct?.category || ''}
                  onChange={(e) => updateField('category', e.target.value)}
                  className="w-full p-3 border rounded-lg"
                >
                  <option value="">Select Category</option>
                  <option value="Air Fryer">Air Fryer</option>
                  <option value="Chimney">Chimney</option>
                  <option value="Coffee Machine">Coffee Machine</option>
                  <option value="Dishwasher">Dishwasher</option>
                  <option value="Gas Hob">Gas Hob</option>
                  <option value="Induction Hob">Induction Hob</option>
                  <option value="Mixer Grinder">Mixer Grinder</option>
                  <option value="Oven">Oven</option>
                  <option value="Refrigerator">Refrigerator</option>
                  <option value="Washing Machine">Washing Machine</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">HSN Code</label>
                <input
                  type="text"
                  value={editingProduct?.hsn_code || ''}
                  onChange={(e) => updateField('hsn_code', e.target.value)}
                  className="w-full p-3 border rounded-lg"
                  placeholder="e.g., 84501200"
                />
                <p className="text-xs text-gray-500 mt-1">8-digit HSN code for GST</p>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Price (₹) *</label>
                <input
                  type="number"
                  value={editingProduct?.price || 0}
                  onChange={(e) => updateField('price', parseFloat(e.target.value))}
                  className="w-full p-3 border rounded-lg"
                  placeholder="e.g., 15999"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Original Price (₹)</label>
                <input
                  type="number"
                  value={editingProduct?.original_price || editingProduct?.originalPrice || 0}
                  onChange={(e) => updateField('original_price', parseFloat(e.target.value))}
                  className="w-full p-3 border rounded-lg"
                  placeholder="e.g., 19999"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Stock Quantity *</label>
                <input
                  type="number"
                  value={editingProduct?.stock_quantity || editingProduct?.stockQuantity || 0}
                  onChange={(e) => updateField('stock_quantity', parseInt(e.target.value))}
                  className="w-full p-3 border rounded-lg"
                  placeholder="e.g., 50"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Main Image URL *</label>
                <input
                  type="text"
                  value={editingProduct?.image || ''}
                  onChange={(e) => updateField('image', e.target.value)}
                  className="w-full p-3 border rounded-lg"
                  placeholder="/product-images/MODEL.webp or full URL"
                />
              </div>

              <div className="col-span-2">
                <label className="block text-sm font-medium mb-2">Description</label>
                <textarea
                  value={editingProduct?.description || ''}
                  onChange={(e) => updateField('description', e.target.value)}
                  className="w-full p-3 border rounded-lg"
                  rows="4"
                  placeholder="Product description..."
                />
              </div>
            </div>

            {/* Image Preview */}
            {editingProduct?.image && (
              <div className="mt-4">
                <label className="block text-sm font-medium mb-2">Image Preview:</label>
                <img
                  src={editingProduct.image}
                  alt="Preview"
                  className="w-48 h-48 object-contain border rounded-lg"
                  onError={(e) => e.target.src = 'https://via.placeholder.com/200?text=Invalid+Image'}
                />
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-4 mt-6">
              <button
                onClick={handleSave}
                className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 flex items-center gap-2"
              >
                <Save className="w-5 h-5" />
                Save Product
              </button>
              <button
                onClick={() => {
                  setEditingProduct(null);
                  setShowAddForm(false);
                }}
                className="bg-gray-500 text-white px-8 py-3 rounded-lg hover:bg-gray-600"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Products List */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4">
            All Products ({filteredProducts.length})
          </h2>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left">Image</th>
                  <th className="px-4 py-3 text-left">Name</th>
                  <th className="px-4 py-3 text-left">Model</th>
                  <th className="px-4 py-3 text-left">Category</th>
                  <th className="px-4 py-3 text-left">HSN</th>
                  <th className="px-4 py-3 text-left">Price</th>
                  <th className="px-4 py-3 text-left">Stock</th>
                  <th className="px-4 py-3 text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredProducts.map((product) => (
                  <tr key={product.id} className="border-t hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <img
                        src={product.image || product.images?.[0]}
                        alt={product.name}
                        className="w-16 h-16 object-contain"
                        onError={(e) => e.target.src = 'https://via.placeholder.com/100?text=No+Image'}
                      />
                    </td>
                    <td className="px-4 py-3 font-medium">{product.name}</td>
                    <td className="px-4 py-3 text-gray-600">{product.modelNumber}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                        {product.category}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="font-mono text-xs text-gray-600">
                        {product.hsn_code || '-'}
                      </span>
                    </td>
                    <td className="px-4 py-3">₹{product.price?.toLocaleString()}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded text-sm ${
                        product.stock > 10 ? 'bg-green-100 text-green-800' : 
                        product.stock > 0 ? 'bg-yellow-100 text-yellow-800' : 
                        'bg-red-100 text-red-800'
                      }`}>
                        {product.stock}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2 justify-center">
                        <button
                          onClick={() => handleEdit(product)}
                          className="text-blue-600 hover:text-blue-800 p-2"
                          title="Edit"
                        >
                          <Edit className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => handleDelete(product.id)}
                          className="text-red-600 hover:text-red-800 p-2"
                          title="Delete"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductManager;
