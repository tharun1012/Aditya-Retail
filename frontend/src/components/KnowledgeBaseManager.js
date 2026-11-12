import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, Trash2, Search, BookOpen, CheckCircle, AlertCircle, ArrowLeft } from 'lucide-react';


const KnowledgeBaseManager = () => {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState('');
  const [uploadError, setUploadError] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  // Upload form state
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [documentType, setDocumentType] = useState('manual');
  const [brand, setBrand] = useState('');
  const [category, setCategory] = useState('');
  const [productIds, setProductIds] = useState('');

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/knowledge-base/`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setDocuments(data.documents || []);
      }
    } catch (error) {
      console.error('Error fetching documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = async (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    
    // Auto-populate title from filename
    if (selectedFile && !title) {
      const autoTitle = selectedFile.name.replace(/\.[^/.]+$/, '');
      setTitle(autoTitle);
      
      // Auto-detect document type, brand, and category from filename
      const filename = autoTitle.toLowerCase();
      
      // Auto-detect document type
      if (filename.includes('manual') || filename.includes('guide') || filename.includes('instruction')) {
        setDocumentType('manual');
      } else if (filename.includes('spec') || filename.includes('datasheet')) {
        setDocumentType('specification');
      } else if (filename.includes('warranty')) {
        setDocumentType('warranty');
      } else if (filename.includes('troubleshoot') || filename.includes('faq')) {
        setDocumentType('troubleshooting');
      }
      
      // Auto-detect brand
      const brands = ['bosch', 'siemens', 'hindware', 'lg', 'samsung', 'whirlpool'];
      for (const brandName of brands) {
        if (filename.includes(brandName)) {
          setBrand(brandName.charAt(0).toUpperCase() + brandName.slice(1));
          break;
        }
      }
      
      // Auto-detect category
      const categories = {
        'washing': 'Washing Machines',
        'refrigerator': 'Refrigerators',
        'dishwasher': 'Dishwashers',
        'oven': 'Ovens',
        'microwave': 'Microwaves',
        'dryer': 'Dryers',
        'mixer': 'Kitchen Appliances'
      };
      
      for (const [keyword, cat] of Object.entries(categories)) {
        if (filename.includes(keyword)) {
          setCategory(cat);
          break;
        }
      }
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setUploadError('Please select a file');
      return;
    }

    try {
      setUploading(true);
      setUploadSuccess('');
      setUploadError('');

      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', title || file.name);
      formData.append('document_type', documentType);
      if (brand) formData.append('brand', brand);
      if (category) formData.append('category', category);
      if (productIds) formData.append('product_ids', productIds);

      const response = await fetch(`${BACKEND_URL}/api/knowledge-base/upload`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (data.status === 'success') {
        setUploadSuccess(`✅ Document uploaded successfully! Extracted ${data.words} words.`);
        
        // Reset form
        setFile(null);
        setTitle('');
        setBrand('');
        setCategory('');
        setProductIds('');
        document.getElementById('fileInput').value = '';
        
        // Refresh list
        fetchDocuments();
      } else {
        setUploadError(data.detail || 'Upload failed');
      }
    } catch (error) {
      setUploadError(`Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (documentId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/knowledge-base/${documentId}`, {
        method: 'DELETE'
      });

      const data = await response.json();

      if (data.status === 'success') {
        fetchDocuments();
      } else {
        alert('Delete failed');
      }
    } catch (error) {
      console.error('Error deleting document:', error);
      alert('Delete failed');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const getDocumentTypeColor = (type) => {
    const colors = {
      manual: 'bg-blue-100 text-blue-800',
      troubleshooting: 'bg-red-100 text-red-800',
      installation: 'bg-green-100 text-green-800',
      warranty: 'bg-purple-100 text-purple-800',
      faq: 'bg-yellow-100 text-yellow-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Back Button */}
        <button
          onClick={() => navigate('/admin')}
          className="flex items-center px-4 py-2 mb-6 text-gray-700 bg-white hover:bg-gray-100 rounded-lg transition-all border border-gray-300 hover:border-gray-400 shadow-sm"
          data-testid="back-to-dashboard-btn"
        >
          <ArrowLeft className="h-5 w-5 mr-2" />
          <span className="font-medium">Back to Dashboard</span>
        </button>

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <BookOpen className="w-8 h-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">Knowledge Base Manager</h1>
          </div>
          <p className="text-gray-600">
            Upload product manuals, brochures, and technical documents to train your AI agents
          </p>
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Upload className="w-5 h-5" />
            Upload New Document
          </h2>

          {/* AI-Powered Simple Upload Notice */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-blue-900 mb-1">🤖 AI-Powered Auto-Detection</h3>
                <p className="text-sm text-blue-800">
                  Just upload your PDF! Our AI automatically extracts document details, brand, category, and type from the filename and content. 
                  You can review and adjust if needed.
                </p>
              </div>
            </div>
          </div>

          <form onSubmit={handleUpload} className="space-y-4">
            {/* Simple File Input */}
            <div>
              <label className="block text-lg font-medium text-gray-900 mb-3">
                📄 Select Document (PDF, DOCX, TXT)
              </label>
              <input
                id="fileInput"
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={handleFileChange}
                required
                className="block w-full text-lg text-gray-900 border-2 border-gray-300 rounded-xl cursor-pointer bg-gray-50 focus:outline-none p-4 hover:border-blue-500 transition-colors"
              />
              {file && (
                <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-sm text-green-800">
                    ✅ Selected: <strong>{file.name}</strong>
                  </p>
                </div>
              )}
            </div>

            {/* Auto-detected info preview */}
            {file && (title || documentType || brand || category) && (
              <div className="bg-gray-50 border border-gray-300 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  AI Auto-Detected Information:
                </h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  {title && <div><span className="text-gray-600">Title:</span> <strong>{title}</strong></div>}
                  {documentType && <div><span className="text-gray-600">Type:</span> <strong>{documentType}</strong></div>}
                  {brand && <div><span className="text-gray-600">Brand:</span> <strong>{brand}</strong></div>}
                  {category && <div><span className="text-gray-600">Category:</span> <strong>{category}</strong></div>}
                </div>
              </div>
            )}

            {/* Advanced Options Toggle */}
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center gap-2"
            >
              {showAdvanced ? '▼' : '▶'} Advanced Options (Optional)
            </button>

            {/* Advanced Fields - Collapsible */}
            {showAdvanced && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 border-t pt-4">
                {/* Title */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Document Title
                  </label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Auto-detected from filename"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Document Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Document Type
                  </label>
                  <select
                    value={documentType}
                    onChange={(e) => setDocumentType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="manual">Product Manual</option>
                    <option value="troubleshooting">Troubleshooting Guide</option>
                    <option value="installation">Installation Guide</option>
                    <option value="warranty">Warranty Information</option>
                    <option value="faq">FAQ</option>
                    <option value="specification">Technical Specification</option>
                  </select>
                </div>

                {/* Brand */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Brand
                  </label>
                  <input
                    type="text"
                    value={brand}
                    onChange={(e) => setBrand(e.target.value)}
                    placeholder="Auto-detected from filename"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Category */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category
                  </label>
                  <input
                    type="text"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    placeholder="Auto-detected from filename"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Product IDs */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Product IDs (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={productIds}
                    onChange={(e) => setProductIds(e.target.value)}
                    placeholder="e.g., WAJ2846IIN, WAK2406IIN"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            )}

            {/* Success/Error Messages */}
            {uploadSuccess && (
              <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg text-green-800">
                <CheckCircle className="w-5 h-5" />
                <span>{uploadSuccess}</span>
              </div>
            )}

            {uploadError && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-800">
                <AlertCircle className="w-5 h-5" />
                <span>{uploadError}</span>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={uploading || !file}
              className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium flex items-center justify-center gap-2"
            >
              {uploading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Uploading & Processing...
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5" />
                  Upload Document
                </>
              )}
            </button>
          </form>
        </div>

        {/* Documents List */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Uploaded Documents ({documents.length})
          </h2>

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-600 mt-4">Loading documents...</p>
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg">No documents uploaded yet</p>
              <p className="text-sm">Upload your first product manual to get started</p>
            </div>
          ) : (
            <div className="space-y-3">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <FileText className="w-5 h-5 text-gray-400" />
                        <h3 className="font-semibold text-gray-900">{doc.title}</h3>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getDocumentTypeColor(doc.document_type)}`}>
                          {doc.document_type}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm text-gray-600">
                        {doc.brand && (
                          <div>
                            <span className="font-medium">Brand:</span> {doc.brand}
                          </div>
                        )}
                        {doc.category && (
                          <div>
                            <span className="font-medium">Category:</span> {doc.category}
                          </div>
                        )}
                        {doc.file_size && (
                          <div>
                            <span className="font-medium">Size:</span> {formatFileSize(doc.file_size)}
                          </div>
                        )}
                        <div>
                          <span className="font-medium">Uploaded:</span> {new Date(doc.created_at).toLocaleDateString()}
                        </div>
                      </div>

                      {doc.product_ids && doc.product_ids.length > 0 && (
                        <div className="mt-2 text-sm">
                          <span className="font-medium text-gray-700">Linked Products:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {doc.product_ids.map((pid, idx) => (
                              <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                                {pid}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="ml-4 p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="Delete document"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default KnowledgeBaseManager;
