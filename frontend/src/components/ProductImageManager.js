import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { Upload, Save, X, Image as ImageIcon, Link, Trash2, Star } from 'lucide-react';

const ProductImageManager = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [imageUrl, setImageUrl] = useState('');
  const [imageFiles, setImageFiles] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);
  const [existingImages, setExistingImages] = useState([]);
  const [uploadMethod, setUploadMethod] = useState('url');
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');

  
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
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMultipleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    
    // Limit to 4 images total
    const currentTotal = existingImages.length + imageFiles.length;
    const availableSlots = 4 - currentTotal;
    
    if (files.length > availableSlots) {
      setMessage(`❌ You can only add ${availableSlots} more image(s). Maximum 4 images per product.`);
      return;
    }

    // Validate file sizes
    const oversized = files.filter(f => f.size > 5 * 1024 * 1024);
    if (oversized.length > 0) {
      setMessage('❌ All files must be less than 5MB');
      return;
    }

    setImageFiles(prev => [...prev, ...files]);

    // Create previews
    files.forEach(file => {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreviews(prev => [...prev, reader.result]);
      };
      reader.readAsDataURL(file);
    });
  };

  const removePreview = (index) => {
    setImageFiles(prev => prev.filter((_, i) => i !== index));
    setImagePreviews(prev => prev.filter((_, i) => i !== index));
  };

  const removeExistingImage = async (imageUrl) => {
    if (!window.confirm('Remove this image from the product?')) return;

    const updatedImages = existingImages.filter(img => img !== imageUrl);
    setExistingImages(updatedImages);

    // Update product
    await updateProductImages(updatedImages);
  };

  const setAsMainImage = async (imageUrl) => {
    const updatedImages = [imageUrl, ...existingImages.filter(img => img !== imageUrl)];
    setExistingImages(updatedImages);

    // Update product with new image order
    await updateProductImages(updatedImages);
  };

  const uploadMultipleImages = async () => {
    if (imageFiles.length === 0 || !selectedProduct) {
      setMessage('❌ Please select images to upload');
      return;
    }

    setUploading(true);
    setMessage('⏳ Uploading images...');

    try {
      const uploadedUrls = [];

      // Upload each file
      for (const file of imageFiles) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${BACKEND_URL}/api/upload-image`, {
          method: 'POST',
          body: formData
        });

        const data = await response.json();
        
        if (response.ok && data.image_url) {
          uploadedUrls.push(data.image_url);
        } else {
          throw new Error(`Failed to upload ${file.name}`);
        }
      }

      // Combine with existing images
      const allImages = [...existingImages, ...uploadedUrls];
      
      // Update product with all images
      await updateProductImages(allImages);

      setImageFiles([]);
      setImagePreviews([]);
      
    } catch (error) {
      setMessage('❌ Error uploading images: ' + error.message);
      setUploading(false);
    }
  };

  const addImageUrl = async () => {
    if (!imageUrl) {
      setMessage('❌ Please enter an image URL');
      return;
    }

    if (existingImages.length >= 4) {
      setMessage('❌ Maximum 4 images per product');
      return;
    }

    const allImages = [...existingImages, imageUrl];
    await updateProductImages(allImages);
    setImageUrl('');
  };

  const updateProductImages = async (imageUrls) => {
    if (!selectedProduct) return;

    setUploading(true);
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/products/${selectedProduct.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...selectedProduct,
          image: imageUrls[0] || '', // First image is the main image
          images: imageUrls
        })
      });

      if (response.ok) {
        setMessage(`✅ Successfully updated images for ${selectedProduct.modelNumber}`);
        setExistingImages(imageUrls);
        fetchProducts();
      } else {
        setMessage('❌ Failed to update product images');
      }
    } catch (error) {
      setMessage('❌ Error: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  const productsWithIssues = products.filter(p => 
    !p.image || 
    p.image === 'N/A' || 
    !p.images || 
    p.images.length === 0
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
        <h1 className="text-3xl font-bold mb-8">Product Image Manager (Multiple Images)</h1>

        {message && (
          <div className={`mb-4 p-4 rounded-lg ${
            message.includes('✅') ? 'bg-green-100 text-green-800' : 
            message.includes('⏳') ? 'bg-blue-100 text-blue-800' :
            'bg-red-100 text-red-800'
          }`}>
            {message}
            <button onClick={() => setMessage('')} className="float-right">
              <X className="w-5 h-5" />
            </button>
          </div>
        )}

        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
          <p className="font-semibold">⚠️ Products with missing images: {productsWithIssues.length}</p>
          <p className="text-sm text-gray-600 mt-1">Each product can have up to 4 images. The first image is the main/cover image.</p>
        </div>

        {selectedProduct && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-xl font-bold mb-4">Manage Images for {selectedProduct.name}</h2>
            <p className="text-sm text-gray-600 mb-4">Model: {selectedProduct.modelNumber}</p>

            {/* Existing Images */}
            <div className="mb-6">
              <h3 className="font-semibold mb-3">
                Current Images ({existingImages.length}/4)
                {existingImages.length > 0 && <span className="text-sm text-gray-500 ml-2">(First image is the main image)</span>}
              </h3>
              
              {existingImages.length > 0 ? (
                <div className="grid grid-cols-4 gap-4">
                  {existingImages.map((img, index) => (
                    <div key={index} className="relative border rounded-lg p-2">
                      {index === 0 && (
                        <div className="absolute top-1 left-1 bg-yellow-400 text-white px-2 py-1 rounded text-xs flex items-center gap-1">
                          <Star className="w-3 h-3" fill="white" />
                          Main
                        </div>
                      )}
                      <img 
                        src={img} 
                        alt={`Product ${index + 1}`}
                        className="w-full h-40 object-contain mb-2"
                        onError={(e) => e.target.src = 'https://via.placeholder.com/200?text=Error'}
                      />
                      <div className="flex gap-2">
                        {index !== 0 && (
                          <button
                            onClick={() => setAsMainImage(img)}
                            className="flex-1 text-xs bg-blue-100 text-blue-700 py-1 rounded hover:bg-blue-200"
                            title="Set as main image"
                          >
                            Set Main
                          </button>
                        )}
                        <button
                          onClick={() => removeExistingImage(img)}
                          className="flex-1 text-xs bg-red-100 text-red-700 py-1 rounded hover:bg-red-200 flex items-center justify-center gap-1"
                        >
                          <Trash2 className="w-3 h-3" />
                          Remove
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center p-8 border-2 border-dashed rounded-lg text-gray-400">
                  <ImageIcon className="w-12 h-12 mx-auto mb-2" />
                  <p>No images yet. Add images below.</p>
                </div>
              )}
            </div>

            {/* Only show add options if less than 4 images */}
            {existingImages.length < 4 && (
              <>
                {/* Upload Method Toggle */}
                <div className="flex gap-4 mb-4">
                  <button
                    onClick={() => {
                      setUploadMethod('url');
                      setImageFiles([]);
                      setImagePreviews([]);
                    }}
                    className={`flex items-center gap-2 px-4 py-2 rounded ${
                      uploadMethod === 'url' ? 'bg-blue-600 text-white' : 'bg-gray-200'
                    }`}
                  >
                    <Link className="w-4 h-4" />
                    Add URL
                  </button>
                  <button
                    onClick={() => {
                      setUploadMethod('file');
                      setImageUrl('');
                    }}
                    className={`flex items-center gap-2 px-4 py-2 rounded ${
                      uploadMethod === 'file' ? 'bg-blue-600 text-white' : 'bg-gray-200'
                    }`}
                  >
                    <Upload className="w-4 h-4" />
                    Upload Files
                  </button>
                </div>

                {/* URL Input */}
                {uploadMethod === 'url' && (
                  <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                    <label className="block text-sm font-medium mb-2">Add Image URL</label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={imageUrl}
                        onChange={(e) => setImageUrl(e.target.value)}
                        placeholder="e.g., /product-images/MODEL.webp"
                        className="flex-1 p-3 border rounded-lg"
                      />
                      <button
                        onClick={addImageUrl}
                        disabled={uploading || !imageUrl}
                        className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                      >
                        Add
                      </button>
                    </div>
                  </div>
                )}

                {/* File Upload */}
                {uploadMethod === 'file' && (
                  <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                    <label className="block text-sm font-medium mb-2">
                      Upload Images (Max {4 - existingImages.length} more)
                    </label>
                    
                    {/* Upload Area */}
                    <div className="border-2 border-dashed rounded-lg p-8 text-center hover:border-blue-400 transition mb-4">
                      <input
                        type="file"
                        accept="image/*"
                        multiple
                        onChange={handleMultipleFileSelect}
                        className="hidden"
                        id="multiFileInput"
                      />
                      <label htmlFor="multiFileInput" className="cursor-pointer block">
                        <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                        <p className="text-sm text-gray-600">
                          Click to select multiple images
                        </p>
                        <p className="text-xs text-gray-400 mt-2">
                          JPG, PNG, WebP (Max 5MB each) | {imageFiles.length} selected
                        </p>
                      </label>
                    </div>

                    {/* Image Previews */}
                    {imagePreviews.length > 0 && (
                      <div className="mb-4">
                        <p className="text-sm font-medium mb-2">Selected Images ({imagePreviews.length}):</p>
                        <div className="grid grid-cols-4 gap-4">
                          {imagePreviews.map((preview, index) => (
                            <div key={index} className="relative border rounded p-2">
                              <img 
                                src={preview} 
                                alt={`Preview ${index + 1}`}
                                className="w-full h-32 object-contain mb-2"
                              />
                              <button
                                onClick={() => removePreview(index)}
                                className="w-full text-xs bg-red-100 text-red-700 py-1 rounded hover:bg-red-200"
                              >
                                Remove
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <button
                      onClick={uploadMultipleImages}
                      disabled={uploading || imageFiles.length === 0}
                      className="w-full bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:bg-gray-400 flex items-center justify-center gap-2"
                    >
                      <Upload className="w-5 h-5" />
                      {uploading ? 'Uploading...' : `Upload ${imageFiles.length} Image(s)`}
                    </button>
                  </div>
                )}
              </>
            )}
            
            <button
              onClick={() => {
                setSelectedProduct(null);
                setImageUrl('');
                setImageFiles([]);
                setImagePreviews([]);
                setExistingImages([]);
              }}
              className="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600"
            >
              Close
            </button>
          </div>
        )}

        {/* Products List */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4">All Products ({products.length})</h2>
          
          <div className="space-y-2 max-h-[600px] overflow-y-auto">
            {products.map((product) => {
              const imageCount = product.images?.length || 0;
              return (
                <div
                  key={product.id}
                  className={`flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition ${
                    productsWithIssues.includes(product) ? 'border-red-300 bg-red-50' : ''
                  }`}
                  onClick={() => {
                    setSelectedProduct(product);
                    setExistingImages(product.images || []);
                    setImageUrl('');
                    setImageFiles([]);
                    setImagePreviews([]);
                    setUploadMethod('file');
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                  }}
                >
                  <div className="flex items-center gap-4 flex-1">
                    <div className="relative">
                      <img
                        src={product.image || product.images?.[0]}
                        alt={product.name}
                        className="w-16 h-16 object-contain border rounded"
                        onError={(e) => e.target.src = 'https://via.placeholder.com/100?text=No+Image'}
                      />
                      {imageCount > 1 && (
                        <div className="absolute -bottom-1 -right-1 bg-blue-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                          {imageCount}
                        </div>
                      )}
                    </div>
                    <div>
                      <p className="font-semibold">{product.name}</p>
                      <p className="text-sm text-gray-600">
                        {product.modelNumber} | {product.category}
                      </p>
                      {imageCount > 0 ? (
                        <span className="text-xs text-green-600">✓ {imageCount} image{imageCount > 1 ? 's' : ''}</span>
                      ) : (
                        <span className="text-xs text-red-600">⚠️ No images</span>
                      )}
                    </div>
                  </div>
                  <button className="text-blue-600 hover:text-blue-800 p-2">
                    <Upload className="w-5 h-5" />
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductImageManager;
