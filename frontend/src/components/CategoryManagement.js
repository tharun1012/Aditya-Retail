import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { FolderTree, Plus, Trash2, ChevronRight, ChevronDown } from 'lucide-react';
import AdminPageHeader from './AdminPageHeader';


const CategoryManagement = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('category'); // 'category' or 'subcategory'
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [expandedCategories, setExpandedCategories] = useState({});
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    icon: '',
    cover_image: '',
    display_order: 0
  });

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      setLoading(true);
      // Fetch all categories (including inactive) for admin view
      const response = await fetch(`${BACKEND_URL}/api/categories/all`);
      const data = await response.json();
      setCategories(data.categories || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching categories:', error);
      setLoading(false);
    }
  };

  const handleAutoPopulate = async () => {
    if (!window.confirm('Auto-populate categories from existing product data?')) return;
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/categories/populate-from-products`, {
        method: 'POST'
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        alert(`✅ Created ${data.created_count} categories!`);
        fetchCategories();
      }
    } catch (error) {
      console.error('Error auto-populating:', error);
      alert('Failed to auto-populate categories');
    }
  };

  const handleCreateCategory = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${BACKEND_URL}/api/categories/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();
      
      if (response.ok && (data.status === 'success' || data.category)) {
        alert('✅ Category created successfully!');
        setShowModal(false);
        setFormData({ name: '', description: '', icon: '', cover_image: '', display_order: 0 });
        fetchCategories();
      } else {
        alert(`❌ Failed: ${data.detail || data.message || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error creating category:', error);
      alert(`❌ Error: ${error.message}`);
    }
  };

  const handleCreateSubCategory = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${BACKEND_URL}/api/categories/sub-category`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category_id: selectedCategory.id,
          ...formData
        })
      });

      const data = await response.json();
      
      if (response.ok && (data.status === 'success' || data.sub_category)) {
        alert('✅ Sub-category created successfully!');
        setShowModal(false);
        setFormData({ name: '', description: '', icon: '', cover_image: '', display_order: 0 });
        setSelectedCategory(null);
        // Expand the parent category to show new subcategory
        setExpandedCategories(prev => ({
          ...prev,
          [selectedCategory.id]: true
        }));
        fetchCategories();
      }
    } catch (error) {
      console.error('Error creating sub-category:', error);
      alert('Failed to create sub-category');
    }
  };

  const handleDeleteCategory = async (categoryId) => {
    if (!window.confirm('Are you sure you want to delete this category?')) return;
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/categories/${categoryId}`, {
        method: 'DELETE'
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        alert('Category deleted successfully!');
        fetchCategories();
      }
    } catch (error) {
      console.error('Error deleting category:', error);
      alert('Failed to delete category');
    }
  };

  const toggleExpanded = (categoryId) => {
    setExpandedCategories({
      ...expandedCategories,
      [categoryId]: !expandedCategories[categoryId]
    });
  };

  const openCategoryModal = () => {
    setModalType('category');
    setSelectedCategory(null);
    setFormData({ name: '', description: '', icon: '', display_order: 0 });
    setShowModal(true);
  };

  const openSubCategoryModal = (category) => {
    setModalType('subcategory');
    setSelectedCategory(category);
    setFormData({ name: '', description: '', icon: '', cover_image: '', display_order: 0 });
    setShowModal(true);
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-700"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <FolderTree className="w-8 h-8 text-amber-700" />
            Category Management
          </h1>
          <p className="text-gray-600 mt-2">Organize your products with categories and sub-categories</p>
        </div>
        <div className="flex gap-3">
          {categories.length === 0 && (
            <button
              onClick={handleAutoPopulate}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <FolderTree className="w-5 h-5" />
              Auto-Populate from Products
            </button>
          )}
          <button
            onClick={openCategoryModal}
            className="bg-amber-700 text-white px-6 py-3 rounded-lg hover:bg-amber-800 transition-colors flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Add Category
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-gray-900">{categories.length}</div>
          <div className="text-sm text-gray-600">Total Categories</div>
        </div>
        <div className="bg-amber-50 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-amber-700">
            {categories.reduce((sum, cat) => sum + (cat.sub_categories?.length || 0), 0)}
          </div>
          <div className="text-sm text-amber-600">Total Sub-Categories</div>
        </div>
        <div className="bg-green-50 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-green-700">
            {categories.filter(c => c.is_active).length}
          </div>
          <div className="text-sm text-green-600">Active Categories</div>
        </div>
      </div>

      {/* Categories Tree */}
      <div className="bg-white rounded-lg shadow">
        {categories.length === 0 ? (
          <div className="p-12 text-center">
            <FolderTree className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Categories Yet</h3>
            <p className="text-gray-600 mb-6">
              Start by auto-populating categories from your existing products or create them manually
            </p>
            <div className="flex gap-3 justify-center">
              <button
                onClick={handleAutoPopulate}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                <FolderTree className="w-5 h-5" />
                Auto-Populate from Products
              </button>
              <button
                onClick={() => {
                  setShowModal(true);
                  setModalType('category');
                }}
                className="bg-amber-700 text-white px-6 py-3 rounded-lg hover:bg-amber-800 transition-colors flex items-center gap-2"
              >
                <Plus className="w-5 h-5" />
                Add Manually
              </button>
            </div>
          </div>
        ) : (
          <div className="divide-y">
            {categories.map((category) => (
            <div key={category.id} className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  <button
                    onClick={() => toggleExpanded(category.id)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    {expandedCategories[category.id] ? (
                      <ChevronDown className="w-5 h-5" />
                    ) : (
                      <ChevronRight className="w-5 h-5" />
                    )}
                  </button>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900">{category.name}</h3>
                    {category.description && (
                      <p className="text-sm text-gray-500">{category.description}</p>
                    )}
                    <span className="text-xs text-gray-400">
                      {category.sub_categories?.length || 0} sub-categories
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => openSubCategoryModal(category)}
                    className="text-amber-600 hover:text-amber-800 px-3 py-1 border border-amber-600 rounded-lg text-sm"
                  >
                    Add Sub-Category
                  </button>
                  <button
                    onClick={() => handleDeleteCategory(category.id)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Sub-categories */}
              {expandedCategories[category.id] && category.sub_categories && (
                <div className="mt-4 ml-8 space-y-2">
                  {category.sub_categories.map((subCat) => (
                    <div key={subCat.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <h4 className="font-medium text-gray-900">{subCat.name}</h4>
                        {subCat.description && (
                          <p className="text-sm text-gray-500">{subCat.description}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6">
              <h2 className="text-2xl font-bold mb-6">
                {modalType === 'category' ? 'Add Category' : `Add Sub-Category to ${selectedCategory?.name}`}
              </h2>

              <form onSubmit={modalType === 'category' ? handleCreateCategory : handleCreateSubCategory}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({...formData, description: e.target.value})}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                      rows="3"
                    ></textarea>
                  </div>

                  {modalType === 'category' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Cover Image URL
                        <span className="text-xs text-gray-500 ml-2">(Product image URL)</span>
                      </label>
                      <input
                        type="url"
                        value={formData.cover_image}
                        onChange={(e) => setFormData({...formData, cover_image: e.target.value})}
                        placeholder="https://example.com/image.jpg"
                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                      />
                      {formData.cover_image && (
                        <img 
                          src={formData.cover_image} 
                          alt="Preview" 
                          className="mt-2 h-24 w-24 object-cover rounded border"
                          onError={(e) => e.target.style.display = 'none'}
                        />
                      )}
                    </div>
                  )}

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Display Order</label>
                    <input
                      type="number"
                      value={formData.display_order}
                      onChange={(e) => setFormData({...formData, display_order: parseInt(e.target.value)})}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-amber-600"
                    />
                  </div>
                </div>

                <div className="flex gap-3 mt-6">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 bg-amber-700 text-white px-4 py-2 rounded-lg hover:bg-amber-800"
                  >
                    Create
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CategoryManagement;
