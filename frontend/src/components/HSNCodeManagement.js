import React, { useState, useEffect, useRef } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import { Hash, Plus, Edit, Trash2, Search, Save, X, ArrowLeft, Download, Upload, FileSpreadsheet, AlertCircle } from 'lucide-react';
import * as XLSX from 'xlsx';


const HSNCodeManagement = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [hsnCodes, setHsnCodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingHSN, setEditingHSN] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [message, setMessage] = useState({ type: '', text: '' });
  const [uploadPreview, setUploadPreview] = useState(null);
  const [validationErrors, setValidationErrors] = useState([]);
  const [autoAssigning, setAutoAssigning] = useState(false);
  const [showAutoAssignPreview, setShowAutoAssignPreview] = useState(null);
  
  const [formData, setFormData] = useState({
    code: '',
    description: '',
    gst_rate: 18.0,
    category: ''
  });

  useEffect(() => {
    fetchHSNCodes();
  }, []);

  const fetchHSNCodes = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/hsn/?active_only=false`);
      const data = await response.json();
      setHsnCodes(data);
    } catch (error) {
      showMessage('error', 'Failed to fetch HSN codes');
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 5000);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate HSN code (minimum 6 digits)
    const validation = validateHSNCode(formData.code);
    if (!validation.valid) {
      showMessage('error', validation.error);
      return;
    }
    
    const submitData = { ...formData, code: validation.code };
    
    try {
      const url = editingHSN 
        ? `${BACKEND_URL}/api/hsn/${editingHSN.id}`
        : `${BACKEND_URL}/api/hsn/`;
      
      const method = editingHSN ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(submitData)
      });

      if (response.ok) {
        showMessage('success', `HSN code ${editingHSN ? 'updated' : 'created'} successfully`);
        setShowModal(false);
        setEditingHSN(null);
        setFormData({ code: '', description: '', gst_rate: 18.0, category: '' });
        fetchHSNCodes();
      } else {
        const error = await response.json();
        showMessage('error', error.detail || 'Failed to save HSN code');
      }
    } catch (error) {
      showMessage('error', 'Error: ' + error.message);
    }
  };

  // Auto-assign HSN codes to products
  const handleAutoAssignPreview = async () => {
    try {
      setAutoAssigning(true);
      const response = await fetch(`${BACKEND_URL}/api/hsn/bulk-assign-to-products?dry_run=true`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.status === 'success') {
        setShowAutoAssignPreview(data);
      } else {
        showMessage('error', data.detail || 'Failed to preview auto-assignment');
      }
    } catch (error) {
      showMessage('error', 'Error: ' + error.message);
    } finally {
      setAutoAssigning(false);
    }
  };

  const handleAutoAssignConfirm = async () => {
    try {
      setAutoAssigning(true);
      const response = await fetch(`${BACKEND_URL}/api/hsn/bulk-assign-to-products?dry_run=false`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.status === 'success') {
        showMessage('success', `Successfully assigned HSN codes to ${data.updated} products!`);
        setShowAutoAssignPreview(null);
      } else {
        showMessage('error', data.detail || 'Failed to auto-assign HSN codes');
      }
    } catch (error) {
      showMessage('error', 'Error: ' + error.message);
    } finally {
      setAutoAssigning(false);
    }
  };

  const handleEdit = (hsn) => {
    setEditingHSN(hsn);
    setFormData({
      code: hsn.code,
      description: hsn.description,
      gst_rate: hsn.gst_rate,
      category: hsn.category || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (hsnId) => {
    if (!window.confirm('Are you sure you want to delete this HSN code?')) return;

    try {
      const response = await fetch(`${BACKEND_URL}/api/hsn/${hsnId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        showMessage('success', 'HSN code deleted successfully');
        fetchHSNCodes();
      } else {
        showMessage('error', 'Failed to delete HSN code');
      }
    } catch (error) {
      showMessage('error', 'Error: ' + error.message);
    }
  };

  // Validate HSN code (minimum 6 digits)
  const validateHSNCode = (code) => {
    const cleanCode = String(code).replace(/\s/g, '');
    if (cleanCode.length < 6) {
      return { valid: false, error: 'HSN code must be at least 6 digits' };
    }
    if (!/^\d+$/.test(cleanCode)) {
      return { valid: false, error: 'HSN code must contain only numbers' };
    }
    return { valid: true, code: cleanCode };
  };

  // Download Excel template
  const downloadTemplate = () => {
    const templateData = [
      { code: '84151010', description: 'Air Conditioners - Split Type', gst_rate: 28, category: 'Home Appliances' },
      { code: '85287300', description: 'Television Sets - LED/LCD', gst_rate: 18, category: 'Electronics' },
      { code: '84182100', description: 'Refrigerators - Household Type', gst_rate: 18, category: 'Home Appliances' },
    ];
    
    const ws = XLSX.utils.json_to_sheet(templateData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'HSN Codes');
    
    // Set column widths
    ws['!cols'] = [
      { wch: 12 },  // code
      { wch: 45 },  // description
      { wch: 10 },  // gst_rate
      { wch: 20 },  // category
    ];
    
    XLSX.writeFile(wb, 'HSN_Code_Template.xlsx');
    showMessage('success', 'Template downloaded! Fill in your HSN codes and upload.');
  };

  // Handle file selection
  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const validExtensions = ['.xlsx', '.xls', '.csv'];
    const fileName = file.name.toLowerCase();
    if (!validExtensions.some(ext => fileName.endsWith(ext))) {
      showMessage('error', 'Please upload an Excel (.xlsx, .xls) or CSV file');
      return;
    }

    try {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data);
      const sheetName = workbook.SheetNames[0];
      const sheet = workbook.Sheets[sheetName];
      const jsonData = XLSX.utils.sheet_to_json(sheet);

      if (jsonData.length === 0) {
        showMessage('error', 'The file is empty');
        return;
      }

      // Validate and preview data
      const errors = [];
      const validRecords = [];

      jsonData.forEach((row, index) => {
        const rowNum = index + 2; // +2 because of header row and 0-indexing
        const rowErrors = [];

        // Check required fields
        if (!row.code) {
          rowErrors.push('Missing HSN code');
        } else {
          const validation = validateHSNCode(row.code);
          if (!validation.valid) {
            rowErrors.push(validation.error);
          } else {
            row.code = validation.code;
          }
        }

        if (!row.description) {
          rowErrors.push('Missing description');
        }

        // Set default GST rate if not provided
        if (row.gst_rate === undefined || row.gst_rate === null || row.gst_rate === '') {
          row.gst_rate = 18;
        } else {
          row.gst_rate = parseFloat(row.gst_rate);
          if (isNaN(row.gst_rate) || row.gst_rate < 0 || row.gst_rate > 100) {
            rowErrors.push('Invalid GST rate (must be 0-100)');
          }
        }

        if (rowErrors.length > 0) {
          errors.push({ row: rowNum, errors: rowErrors, data: row });
        } else {
          validRecords.push({
            code: String(row.code),
            description: String(row.description),
            gst_rate: row.gst_rate,
            category: row.category ? String(row.category) : ''
          });
        }
      });

      setValidationErrors(errors);
      setUploadPreview({ total: jsonData.length, valid: validRecords, invalid: errors.length });

      if (errors.length > 0 && validRecords.length === 0) {
        showMessage('error', 'All records have validation errors. Please fix and re-upload.');
      }

    } catch (error) {
      showMessage('error', 'Error reading file: ' + error.message);
    }

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Upload validated HSN codes
  const uploadHSNCodes = async () => {
    if (!uploadPreview || uploadPreview.valid.length === 0) {
      showMessage('error', 'No valid records to upload');
      return;
    }

    setUploading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/hsn/bulk-upload`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(uploadPreview.valid)
      });

      const result = await response.json();
      
      if (response.ok) {
        showMessage('success', `Successfully uploaded: ${result.created} new, ${result.skipped} skipped (duplicates)`);
        setUploadPreview(null);
        setValidationErrors([]);
        fetchHSNCodes();
      } else {
        showMessage('error', result.detail || 'Upload failed');
      }
    } catch (error) {
      showMessage('error', 'Upload error: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  // Cancel upload preview
  const cancelUpload = () => {
    setUploadPreview(null);
    setValidationErrors([]);
  };

  const filteredHSNCodes = hsnCodes.filter(hsn =>
    hsn.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
    hsn.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-violet-700"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
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
      <div className="mb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Hash className="w-8 h-8 text-violet-700" />
            HSN Code Management
          </h1>
          <p className="text-gray-600 mt-2">Manage HSN/SAC codes for GST compliance (minimum 6 digits required)</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={handleAutoAssignPreview}
            disabled={autoAssigning}
            className="bg-amber-600 text-white px-4 py-2 rounded-lg hover:bg-amber-700 transition-colors flex items-center gap-2 disabled:opacity-50"
            data-testid="auto-assign-hsn-btn"
            title="Automatically assign HSN codes to products based on their names"
          >
            {autoAssigning ? 'Scanning...' : 'Auto-Assign to Products'}
          </button>
          <button
            onClick={downloadTemplate}
            className="bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 transition-colors flex items-center gap-2"
            data-testid="download-template-btn"
          >
            <Download className="w-4 h-4" />
            Download Template
          </button>
          <label className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 cursor-pointer">
            <Upload className="w-4 h-4" />
            Upload Excel
            <input
              ref={fileInputRef}
              type="file"
              accept=".xlsx,.xls,.csv"
              onChange={handleFileSelect}
              className="hidden"
              data-testid="upload-file-input"
            />
          </label>
          <button
            onClick={() => {
              setEditingHSN(null);
              setFormData({ code: '', description: '', gst_rate: 18.0, category: '' });
              setShowModal(true);
            }}
            className="bg-violet-700 text-white px-4 py-2 rounded-lg hover:bg-violet-800 transition-colors flex items-center gap-2"
            data-testid="add-hsn-btn"
          >
            <Plus className="w-4 h-4" />
            Add HSN Code
          </button>
        </div>
      </div>

      {/* Auto-Assign Preview Modal */}
      {showAutoAssignPreview && (
        <div className="mb-6 bg-white rounded-lg shadow-lg border border-amber-200 overflow-hidden">
          <div className="bg-amber-50 px-6 py-4 border-b border-amber-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Hash className="w-6 h-6 text-amber-600" />
                <h3 className="text-lg font-semibold text-amber-900">Auto-Assign HSN Codes to Products</h3>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowAutoAssignPreview(null)}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAutoAssignConfirm}
                  disabled={autoAssigning || showAutoAssignPreview.matched === 0}
                  className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {autoAssigning ? 'Assigning...' : `Assign to ${showAutoAssignPreview.matched} Products`}
                </button>
              </div>
            </div>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-gray-800">{showAutoAssignPreview.total_products_without_hsn}</div>
                <div className="text-sm text-gray-600">Products Without HSN</div>
              </div>
              <div className="bg-green-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-green-700">{showAutoAssignPreview.matched}</div>
                <div className="text-sm text-green-600">Can Auto-Assign</div>
              </div>
              <div className="bg-orange-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-orange-700">{showAutoAssignPreview.unmatched}</div>
                <div className="text-sm text-orange-600">Need Manual Assignment</div>
              </div>
            </div>

            {showAutoAssignPreview.assignments?.length > 0 && (
              <div className="mt-4">
                <h4 className="font-semibold text-gray-800 mb-2">Preview (showing first 20)</h4>
                <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-2">Product</th>
                        <th className="text-left py-2">HSN Code</th>
                        <th className="text-left py-2">GST Rate</th>
                      </tr>
                    </thead>
                    <tbody>
                      {showAutoAssignPreview.assignments.slice(0, 20).map((a, idx) => (
                        <tr key={idx} className="border-b border-gray-200">
                          <td className="py-2">{a.model_number} - {a.product_name}</td>
                          <td className="py-2 font-mono">{a.hsn_code}</td>
                          <td className="py-2">{a.gst_rate}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Upload Preview */}
      {uploadPreview && (
        <div className="mb-6 bg-white rounded-lg shadow-lg border border-blue-200 overflow-hidden">
          <div className="bg-blue-50 px-6 py-4 border-b border-blue-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FileSpreadsheet className="w-6 h-6 text-blue-600" />
                <h3 className="text-lg font-semibold text-blue-900">Upload Preview</h3>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={cancelUpload}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  onClick={uploadHSNCodes}
                  disabled={uploading || uploadPreview.valid.length === 0}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {uploading ? 'Uploading...' : `Upload ${uploadPreview.valid.length} Records`}
                </button>
              </div>
            </div>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-gray-800">{uploadPreview.total}</div>
                <div className="text-sm text-gray-600">Total Rows</div>
              </div>
              <div className="bg-green-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-green-700">{uploadPreview.valid.length}</div>
                <div className="text-sm text-green-600">Valid Records</div>
              </div>
              <div className="bg-red-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-red-700">{uploadPreview.invalid}</div>
                <div className="text-sm text-red-600">Errors</div>
              </div>
            </div>

            {validationErrors.length > 0 && (
              <div className="mt-4">
                <h4 className="font-semibold text-red-800 mb-2 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  Validation Errors (these rows will be skipped)
                </h4>
                <div className="bg-red-50 rounded-lg p-4 max-h-48 overflow-y-auto">
                  {validationErrors.map((err, idx) => (
                    <div key={idx} className="text-sm text-red-700 mb-1">
                      <span className="font-medium">Row {err.row}:</span> {err.errors.join(', ')}
                      {err.data.code && <span className="text-gray-500 ml-2">(Code: {err.data.code})</span>}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {uploadPreview.valid.length > 0 && (
              <div className="mt-4">
                <h4 className="font-semibold text-green-800 mb-2">Preview of Valid Records (first 5)</h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-green-50">
                        <th className="px-3 py-2 text-left">HSN Code</th>
                        <th className="px-3 py-2 text-left">Description</th>
                        <th className="px-3 py-2 text-right">GST %</th>
                        <th className="px-3 py-2 text-left">Category</th>
                      </tr>
                    </thead>
                    <tbody>
                      {uploadPreview.valid.slice(0, 5).map((record, idx) => (
                        <tr key={idx} className="border-b">
                          <td className="px-3 py-2 font-mono">{record.code}</td>
                          <td className="px-3 py-2">{record.description}</td>
                          <td className="px-3 py-2 text-right">{record.gst_rate}%</td>
                          <td className="px-3 py-2">{record.category || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {uploadPreview.valid.length > 5 && (
                    <p className="text-sm text-gray-500 mt-2">... and {uploadPreview.valid.length - 5} more records</p>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Message */}
      {message.text && (
        <div className={`mb-4 p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {message.text}
        </div>
      )}

      {/* Search */}
      <div className="mb-6 bg-white rounded-lg shadow p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search HSN codes or descriptions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
          />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-gray-900">{hsnCodes.length}</div>
          <div className="text-sm text-gray-600">Total HSN Codes</div>
        </div>
        <div className="bg-violet-50 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-violet-700">
            {hsnCodes.filter(h => h.is_active).length}
          </div>
          <div className="text-sm text-violet-600">Active Codes</div>
        </div>
        <div className="bg-blue-50 rounded-lg shadow p-4">
          <div className="text-2xl font-bold text-blue-700">
            {[...new Set(hsnCodes.map(h => h.category))].filter(Boolean).length}
          </div>
          <div className="text-sm text-blue-600">Categories</div>
        </div>
      </div>

      {/* HSN Codes Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="text-left py-4 px-6 font-semibold text-sm text-gray-600">HSN Code</th>
                <th className="text-left py-4 px-6 font-semibold text-sm text-gray-600">Description</th>
                <th className="text-left py-4 px-6 font-semibold text-sm text-gray-600">Category</th>
                <th className="text-right py-4 px-6 font-semibold text-sm text-gray-600">GST Rate</th>
                <th className="text-center py-4 px-6 font-semibold text-sm text-gray-600">Status</th>
                <th className="text-center py-4 px-6 font-semibold text-sm text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredHSNCodes.map((hsn) => (
                <tr key={hsn.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                  <td className="py-4 px-6 font-semibold text-violet-700">{hsn.code}</td>
                  <td className="py-4 px-6 text-sm text-gray-600">{hsn.description}</td>
                  <td className="py-4 px-6 text-sm text-gray-600">{hsn.category || '-'}</td>
                  <td className="py-4 px-6 text-right">
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                      {hsn.gst_rate}%
                    </span>
                  </td>
                  <td className="py-4 px-6 text-center">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      hsn.is_active 
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {hsn.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="py-4 px-6">
                    <div className="flex items-center justify-center gap-2">
                      <button
                        onClick={() => handleEdit(hsn)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                      >
                        <Edit className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => handleDelete(hsn.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                      >
                        <Trash2 className="h-5 w-5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  {editingHSN ? 'Edit HSN Code' : 'Add New HSN Code'}
                </h2>
                <button
                  onClick={() => setShowModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <form onSubmit={handleSubmit}>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">HSN Code * <span className="text-xs text-gray-500">(min 6 digits)</span></label>
                    <input
                      type="text"
                      value={formData.code}
                      onChange={(e) => setFormData({...formData, code: e.target.value.replace(/\D/g, '')})}
                      className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-violet-600 ${
                        formData.code && formData.code.length < 6 ? 'border-red-300 bg-red-50' : ''
                      }`}
                      required
                      minLength={6}
                      placeholder="e.g., 851610"
                    />
                    {formData.code && formData.code.length > 0 && formData.code.length < 6 && (
                      <p className="text-xs text-red-500 mt-1">HSN code must be at least 6 digits ({6 - formData.code.length} more needed)</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">GST Rate (%) *</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.gst_rate}
                      onChange={(e) => setFormData({...formData, gst_rate: parseFloat(e.target.value)})}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-violet-600"
                      required
                    />
                  </div>
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description *</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-violet-600"
                    rows="3"
                    required
                    placeholder="e.g., Electric instantaneous or storage water heaters"
                  ></textarea>
                </div>

                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Category (Optional)</label>
                  <input
                    type="text"
                    value={formData.category}
                    onChange={(e) => setFormData({...formData, category: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-violet-600"
                    placeholder="e.g., Home Appliances, Electronics"
                  />
                </div>

                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 bg-violet-700 text-white px-4 py-2 rounded-lg hover:bg-violet-800 flex items-center justify-center gap-2"
                  >
                    <Save className="w-5 h-5" />
                    {editingHSN ? 'Update' : 'Create'}
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

export default HSNCodeManagement;
