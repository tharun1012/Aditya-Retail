#!/usr/bin/env python3
import shutil

TARGET = "frontend/src/components/AdminPORequestsView.js"

with open(TARGET, "r") as f:
    content = f.read()

shutil.copy(TARGET, TARGET + ".bak")

old_1 = """import { 
  Check, X, Clock, Package, RefreshCw, Eye, 
  AlertTriangle, Truck, MapPin, User, Phone, 
  FileText, Calendar, Building, ChevronDown
} from 'lucide-react';"""
new_1 = """import { 
  Check, X, Clock, Package, RefreshCw, Eye, 
  AlertTriangle, Truck, MapPin, User, Phone, 
  FileText, Calendar, Building, ChevronDown, Plus, Pencil
} from 'lucide-react';"""
assert old_1 in content, "EDIT 1 anchor not found (icon imports)"
content = content.replace(old_1, new_1, 1)

old_2 = "  const [filterStatus, setFilterStatus] = useState('all');"
new_2 = """  const [filterStatus, setFilterStatus] = useState('all');
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingRequest, setEditingRequest] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);"""
assert old_2 in content, "EDIT 2 anchor not found (state vars)"
content = content.replace(old_2, new_2, 1)

old_3 = """            <button
              onClick={fetchPORequests}
              className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
              title="Refresh"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
          </div>
        </div>"""
new_3 = """            <button
              onClick={fetchPORequests}
              className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
              title="Refresh"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
            >
              <Plus className="w-4 h-4" />
              Create PO Request
            </button>
          </div>
        </div>"""
assert old_3 in content, "EDIT 3 anchor not found (header button)"
content = content.replace(old_3, new_3, 1)

old_4 = """                      {(request.status === 'pending' || request.status === 'pending_review') && (
                        <>
                          <button
                            onClick={() => {
                              setSelectedRequest(request);
                              setApprovalAction('approve');
                              setShowApprovalModal(true);
                            }}
                            className="p-1.5 text-green-600 hover:bg-green-50 rounded"
                            title="Approve"
                          >
                            <Check className="w-4 h-4" />
                          </button>"""
new_4 = """                      {(request.status === 'pending' || request.status === 'pending_review') && (
                        <>
                          <button
                            onClick={() => {
                              setEditingRequest(request);
                              setShowEditModal(true);
                            }}
                            className="p-1.5 text-blue-600 hover:bg-blue-50 rounded"
                            title="Edit"
                          >
                            <Pencil className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => {
                              setSelectedRequest(request);
                              setApprovalAction('approve');
                              setShowApprovalModal(true);
                            }}
                            className="p-1.5 text-green-600 hover:bg-green-50 rounded"
                            title="Approve"
                          >
                            <Check className="w-4 h-4" />
                          </button>"""
assert old_4 in content, "EDIT 4 anchor not found (table action buttons)"
content = content.replace(old_4, new_4, 1)

old_5 = """      )}
    </div>
  );
};

export default AdminPORequestsView;"""

new_5 = """      )}

      {showEditModal && editingRequest && (
        <EditPORequestModal
          request={editingRequest}
          onClose={() => { setShowEditModal(false); setEditingRequest(null); }}
          onSuccess={() => {
            setShowEditModal(false);
            setEditingRequest(null);
            fetchPORequests();
          }}
        />
      )}

      {showCreateModal && (
        <AdminCreatePORequestModal
          stores={stores}
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false);
            fetchPORequests();
          }}
        />
      )}
    </div>
  );
};

const EditPORequestModal = ({ request, onClose, onSuccess }) => {
  const [items, setItems] = useState(
    (request.items || []).map(i => ({
      model_number: i.model_number || '',
      product_name: i.product_name || '',
      sku: i.sku || '',
      product_id: i.product_id || '',
      quantity: i.quantity || 1,
      cost_price: i.cost_price || i.unit_price || 0,
      notes: i.notes || ''
    }))
  );
  const [supplierName, setSupplierName] = useState(request.supplier_name || request.vendor_name || '');
  const [urgency, setUrgency] = useState(request.urgency || 'normal');
  const [notes, setNotes] = useState(request.notes || '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const updateItem = (index, field, value) => {
    const next = [...items];
    next[index][field] = value;
    setItems(next);
  };

  const addItem = () => {
    setItems([...items, { model_number: '', product_name: '', sku: '', product_id: '', quantity: 1, cost_price: 0, notes: '' }]);
  };

  const removeItem = (index) => {
    if (items.length > 1) setItems(items.filter((_, i) => i !== index));
  };

  const handleSave = async () => {
    setError('');
    setSaving(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/stock-transfer/po-requests/${request.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          items: items.map(i => ({
            ...i,
            quantity: parseInt(i.quantity) || 0,
            cost_price: parseFloat(i.cost_price) || 0
          })),
          supplier_name: supplierName,
          urgency,
          notes
        })
      });
      const data = await response.json();
      if (response.ok) {
        onSuccess();
      } else {
        setError(data.detail || 'Failed to update request');
      }
    } catch (err) {
      setError('Connection error: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  const total = items.reduce((sum, i) => sum + (parseFloat(i.quantity) || 0) * (parseFloat(i.cost_price) || 0), 0);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <div className="p-4 border-b bg-blue-600 text-white flex items-center justify-between">
          <h3 className="text-lg font-bold">Edit PO Request</h3>
          <button onClick={onClose} className="p-1 hover:bg-white/20 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Items</label>
            <div className="space-y-2">
              {items.map((item, idx) => (
                <div key={idx} className="grid grid-cols-12 gap-2 items-center">
                  <input
                    className="col-span-3 px-2 py-1.5 border rounded text-sm"
                    placeholder="Model / SKU"
                    value={item.model_number}
                    onChange={(e) => updateItem(idx, 'model_number', e.target.value)}
                  />
                  <input
                    className="col-span-3 px-2 py-1.5 border rounded text-sm"
                    placeholder="Product name"
                    value={item.product_name}
                    onChange={(e) => updateItem(idx, 'product_name', e.target.value)}
                  />
                  <input
                    type="number"
                    className="col-span-2 px-2 py-1.5 border rounded text-sm"
                    placeholder="Qty"
                    value={item.quantity}
                    onChange={(e) => updateItem(idx, 'quantity', e.target.value)}
                  />
                  <input
                    type="number"
                    className="col-span-2 px-2 py-1.5 border rounded text-sm"
                    placeholder="Unit price"
                    value={item.cost_price}
                    onChange={(e) => updateItem(idx, 'cost_price', e.target.value)}
                  />
                  <span className="col-span-1 text-xs text-gray-600 text-right">
                    ₹{((parseFloat(item.quantity) || 0) * (parseFloat(item.cost_price) || 0)).toLocaleString()}
                  </span>
                  <button
                    type="button"
                    onClick={() => removeItem(idx)}
                    className="col-span-1 p-1 text-red-500 hover:bg-red-50 rounded"
                    disabled={items.length === 1}
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
            <button type="button" onClick={addItem} className="mt-2 text-sm text-blue-600 hover:text-blue-700">
              + Add Item
            </button>
            <p className="mt-2 text-sm font-medium text-gray-700">Estimated total: ₹{total.toLocaleString()}</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Supplier / Vendor</label>
              <input
                className="w-full px-3 py-2 border rounded-lg text-sm"
                value={supplierName}
                onChange={(e) => setSupplierName(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Urgency</label>
              <select
                className="w-full px-3 py-2 border rounded-lg text-sm"
                value={urgency}
                onChange={(e) => setUrgency(e.target.value)}
              >
                <option value="normal">Normal</option>
                <option value="urgent">Urgent</option>
                <option value="critical">Critical</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
            <textarea
              className="w-full px-3 py-2 border rounded-lg text-sm"
              rows={3}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>
        </div>

        <div className="p-4 border-t bg-gray-50 flex justify-end gap-2">
          <button onClick={onClose} className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300" disabled={saving}>
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
};

const AdminCreatePORequestModal = ({ stores, onClose, onSuccess }) => {
  const [storeId, setStoreId] = useState('');
  const [items, setItems] = useState([{ model_number: '', quantity: 1, notes: '' }]);
  const [urgency, setUrgency] = useState('normal');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const addItem = () => setItems([...items, { model_number: '', quantity: 1, notes: '' }]);
  const removeItem = (index) => { if (items.length > 1) setItems(items.filter((_, i) => i !== index)); };
  const updateItem = (index, field, value) => {
    const next = [...items];
    next[index][field] = value;
    setItems(next);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!storeId) {
      setError('Please select a requesting store');
      return;
    }

    const validItems = items.filter(item => item.model_number.trim() && item.quantity > 0);
    if (validItems.length === 0) {
      setError('Please add at least one item with model number and quantity');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/stock-transfer/po-request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          store_id: storeId,
          items: validItems,
          urgency,
          notes
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        onSuccess();
      } else {
        setError(data.detail || 'Failed to create PO request');
      }
    } catch (err) {
      setError('Connection error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-800">Create PO Request</h2>
            <p className="text-sm text-gray-500">Raise a procurement request on behalf of a store</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" />
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Requesting Store *</label>
            <select
              value={storeId}
              onChange={(e) => setStoreId(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
              required
            >
              <option value="">-- Select Store --</option>
              {stores.map(store => (
                <option key={store.code || store.id} value={store.id}>
                  {store.name} ({store.code})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Items Required</label>
            <div className="space-y-3">
              {items.map((item, index) => (
                <div key={index} className="flex gap-2 items-start">
                  <input
                    type="text"
                    value={item.model_number}
                    onChange={(e) => updateItem(index, 'model_number', e.target.value)}
                    placeholder="Model Number / SKU"
                    className="flex-1 px-3 py-2 border rounded-lg text-sm"
                    required
                  />
                  <input
                    type="number"
                    value={item.quantity}
                    onChange={(e) => updateItem(index, 'quantity', parseInt(e.target.value) || 1)}
                    placeholder="Qty"
                    min="1"
                    className="w-24 px-3 py-2 border rounded-lg text-sm"
                    required
                  />
                  <input
                    type="text"
                    value={item.notes}
                    onChange={(e) => updateItem(index, 'notes', e.target.value)}
                    placeholder="Notes (optional)"
                    className="flex-1 px-3 py-2 border rounded-lg text-sm"
                  />
                  <button type="button" onClick={() => removeItem(index)} className="p-2 text-red-500 hover:bg-red-50 rounded-lg" disabled={items.length === 1}>
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
            <button type="button" onClick={addItem} className="mt-2 text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1">
              <Plus className="w-4 h-4" /> Add Another Item
            </button>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Urgency</label>
            <div className="flex gap-2">
              {['normal', 'urgent', 'critical'].map((level) => (
                <button
                  key={level}
                  type="button"
                  onClick={() => setUrgency(level)}
                  className={`px-4 py-2 rounded-lg border text-sm font-medium transition-colors ${
                    urgency === level
                      ? level === 'critical' ? 'bg-red-100 border-red-300 text-red-700'
                        : level === 'urgent' ? 'bg-orange-100 border-orange-300 text-orange-700'
                        : 'bg-blue-100 border-blue-300 text-blue-700'
                      : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {level.charAt(0).toUpperCase() + level.slice(1)}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Additional Notes</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border rounded-lg text-sm"
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t">
            <button type="button" onClick={onClose} className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Submitting...' : 'Submit Request'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AdminPORequestsView;"""

assert old_5 in content, "EDIT 5 anchor not found (component end / export default)"
content = content.replace(old_5, new_5, 1)

with open(TARGET, "w") as f:
    f.write(content)

print("Patched", TARGET)
print("Backup saved at", TARGET + ".bak")
