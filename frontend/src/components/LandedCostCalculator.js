import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  Package, Plus, Search, Calculator, X, Save, Trash2,
  IndianRupee, Truck, FileText, ChevronDown, ChevronUp,
  PieChart, TrendingUp, Eye, RefreshCw
} from 'lucide-react';
import { showToast } from '../utils/toast';


const LandedCostCalculator = () => {
  const [purchaseBills, setPurchaseBills] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('calculate');
  const [selectedBill, setSelectedBill] = useState(null);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [showCalculation, setShowCalculation] = useState(false);
  
  // Cost components for calculation
  const [costComponents, setCostComponents] = useState([
    { name: 'Freight', amount: 0, is_percentage: false, allocation_method: 'value' },
    { name: 'Insurance', amount: 0, is_percentage: true, allocation_method: 'value' }
  ]);
  
  const [calculationResult, setCalculationResult] = useState(null);
  
  // Template form
  const [templateForm, setTemplateForm] = useState({
    name: '',
    description: '',
    components: [],
    is_default: false
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    await Promise.all([
      fetchPurchaseBills(),
      fetchTemplates(),
      fetchHistory(),
      fetchStats()
    ]);
    setLoading(false);
  };

  const fetchPurchaseBills = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/purchase-bills?has_landed_cost=false&limit=100`);
      const data = await response.json();
      if (data.status === 'success') {
        setPurchaseBills(data.bills || []);
      }
    } catch (error) {
      console.error('Failed to fetch purchase bills:', error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/landed-cost/templates`);
      const data = await response.json();
      if (data.status === 'success') {
        setTemplates(data.templates || []);
      }
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/landed-cost/history?limit=20`);
      const data = await response.json();
      if (data.status === 'success') {
        setHistory(data.records || []);
      }
    } catch (error) {
      console.error('Failed to fetch history:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/landed-cost/stats`);
      const data = await response.json();
      if (data.status === 'success') {
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const handleAddComponent = () => {
    setCostComponents([
      ...costComponents,
      { name: '', amount: 0, is_percentage: false, allocation_method: 'value' }
    ]);
  };

  const handleRemoveComponent = (index) => {
    setCostComponents(costComponents.filter((_, i) => i !== index));
  };

  const handleComponentChange = (index, field, value) => {
    const newComponents = [...costComponents];
    newComponents[index][field] = value;
    setCostComponents(newComponents);
  };

  const handleApplyTemplate = (template) => {
    setCostComponents(template.components.map(c => ({
      name: c.name,
      amount: c.amount,
      is_percentage: c.is_percentage,
      allocation_method: c.allocation_method
    })));
    showToast.success(`Applied template: ${template.name}`);
  };

  const handleCalculate = async () => {
    if (!selectedBill) {
      showToast.error('Please select a purchase bill');
      return;
    }
    
    const validComponents = costComponents.filter(c => c.name && c.amount > 0);
    if (validComponents.length === 0) {
      showToast.error('Please add at least one cost component');
      return;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/landed-cost/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          purchase_bill_id: selectedBill.id,
          additional_costs: validComponents,
          notes: ''
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setCalculationResult(data);
        setShowCalculation(true);
        showToast.success('Landed cost calculated successfully');
        fetchHistory();
        fetchStats();
        fetchPurchaseBills();
      } else {
        showToast.error(data.detail || 'Calculation failed');
      }
    } catch (error) {
      showToast.error('Failed to calculate landed cost');
    }
  };

  const handleSaveTemplate = async () => {
    if (!templateForm.name) {
      showToast.error('Please enter a template name');
      return;
    }
    
    const validComponents = costComponents.filter(c => c.name);
    if (validComponents.length === 0) {
      showToast.error('Please add at least one cost component');
      return;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/landed-cost/templates/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: templateForm.name,
          description: templateForm.description,
          components: validComponents,
          is_default: templateForm.is_default
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        showToast.success(data.message);
        setShowTemplateModal(false);
        setTemplateForm({ name: '', description: '', components: [], is_default: false });
        fetchTemplates();
      } else {
        showToast.error(data.detail || 'Failed to save template');
      }
    } catch (error) {
      showToast.error('Failed to save template');
    }
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen" data-testid="landed-cost-page">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Package className="text-orange-500" />
              Landed Cost Calculator
            </h1>
            <p className="text-gray-600 mt-1">Calculate total cost including freight, customs, and expenses</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 border-b border-gray-200">
          {[
            { id: 'calculate', label: 'Calculate', icon: Calculator },
            { id: 'history', label: 'History', icon: FileText },
            { id: 'templates', label: 'Templates', icon: Package }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 flex items-center gap-2 border-b-2 transition ${
                activeTab === tab.id 
                  ? 'border-orange-500 text-orange-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <tab.icon size={18} />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Total Calculations</p>
            <p className="text-2xl font-bold text-gray-900">{stats.stats?.total_records || 0}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Total Base Cost</p>
            <p className="text-2xl font-bold text-blue-600">₹{(stats.stats?.total_base_cost || 0).toLocaleString()}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Additional Costs</p>
            <p className="text-2xl font-bold text-orange-600">₹{(stats.stats?.total_additional || 0).toLocaleString()}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Avg. Cost Increase</p>
            <p className="text-2xl font-bold text-green-600">{stats.stats?.average_increase_percent || 0}%</p>
          </div>
        </div>
      )}

      {/* Calculate Tab */}
      {activeTab === 'calculate' && (
        <div className="grid grid-cols-3 gap-6">
          {/* Left - Bill Selection & Costs */}
          <div className="col-span-2 space-y-6">
            {/* Select Purchase Bill */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="font-semibold text-gray-900 mb-4">1. Select Purchase Bill</h2>
              
              {loading ? (
                <div className="text-center py-4">
                  <div className="animate-spin h-8 w-8 border-b-2 border-orange-500 rounded-full mx-auto"></div>
                </div>
              ) : purchaseBills.length === 0 ? (
                <div className="text-center py-6 text-gray-500">
                  <Package size={48} className="mx-auto mb-2 text-gray-300" />
                  <p>No pending purchase bills</p>
                  <p className="text-sm">All bills have landed cost calculated</p>
                </div>
              ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {purchaseBills.map(bill => (
                    <div
                      key={bill.id}
                      onClick={() => setSelectedBill(bill)}
                      className={`p-3 border rounded-lg cursor-pointer transition ${
                        selectedBill?.id === bill.id
                          ? 'border-orange-500 bg-orange-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium">{bill.bill_number}</p>
                          <p className="text-sm text-gray-500">{bill.vendor?.name}</p>
                          <p className="text-xs text-gray-400">{bill.bill_date}</p>
                        </div>
                        <p className="font-bold text-gray-900">₹{(bill.grand_total || 0).toLocaleString()}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Cost Components */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="font-semibold text-gray-900">2. Add Additional Costs</h2>
                <div className="flex gap-2">
                  <select
                    onChange={(e) => {
                      const template = templates.find(t => t.id === e.target.value);
                      if (template) handleApplyTemplate(template);
                    }}
                    className="px-3 py-1 border border-gray-300 rounded text-sm"
                    defaultValue=""
                  >
                    <option value="" disabled>Apply Template...</option>
                    {templates.map(t => (
                      <option key={t.id} value={t.id}>{t.name}</option>
                    ))}
                  </select>
                  <button
                    onClick={handleAddComponent}
                    className="px-3 py-1 bg-orange-100 text-orange-600 rounded text-sm hover:bg-orange-200"
                  >
                    + Add Cost
                  </button>
                </div>
              </div>

              <div className="space-y-3">
                {costComponents.map((component, index) => (
                  <div key={index} className="flex gap-3 items-start p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <input
                        type="text"
                        value={component.name}
                        onChange={(e) => handleComponentChange(index, 'name', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded"
                        placeholder="Cost name (e.g., Freight)"
                      />
                    </div>
                    <div className="w-32">
                      <input
                        type="number"
                        value={component.amount}
                        onChange={(e) => handleComponentChange(index, 'amount', parseFloat(e.target.value) || 0)}
                        className="w-full px-3 py-2 border border-gray-300 rounded"
                        placeholder="Amount"
                      />
                    </div>
                    <div className="w-24">
                      <select
                        value={component.is_percentage ? 'percent' : 'fixed'}
                        onChange={(e) => handleComponentChange(index, 'is_percentage', e.target.value === 'percent')}
                        className="w-full px-2 py-2 border border-gray-300 rounded text-sm"
                      >
                        <option value="fixed">₹ Fixed</option>
                        <option value="percent">% of Bill</option>
                      </select>
                    </div>
                    <div className="w-28">
                      <select
                        value={component.allocation_method}
                        onChange={(e) => handleComponentChange(index, 'allocation_method', e.target.value)}
                        className="w-full px-2 py-2 border border-gray-300 rounded text-sm"
                      >
                        <option value="value">By Value</option>
                        <option value="quantity">By Qty</option>
                        <option value="weight">By Weight</option>
                      </select>
                    </div>
                    <button
                      onClick={() => handleRemoveComponent(index)}
                      className="p-2 text-gray-400 hover:text-red-600"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                ))}
              </div>

              <div className="mt-4 flex gap-3">
                <button
                  onClick={handleCalculate}
                  disabled={!selectedBill}
                  className="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 flex items-center gap-2"
                >
                  <Calculator size={18} />
                  Calculate Landed Cost
                </button>
                <button
                  onClick={() => setShowTemplateModal(true)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Save as Template
                </button>
              </div>
            </div>
          </div>

          {/* Right - Preview/Result */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="font-semibold text-gray-900 mb-4">Preview</h2>
            
            {selectedBill ? (
              <div className="space-y-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500">Selected Bill</p>
                  <p className="font-bold text-lg">{selectedBill.bill_number}</p>
                  <p className="text-gray-600">{selectedBill.vendor?.name}</p>
                </div>
                
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-600">Base Cost</p>
                  <p className="font-bold text-2xl text-blue-700">
                    ₹{(selectedBill.grand_total || 0).toLocaleString()}
                  </p>
                </div>
                
                <div className="p-4 bg-orange-50 rounded-lg">
                  <p className="text-sm text-orange-600">Additional Costs</p>
                  <p className="font-bold text-2xl text-orange-700">
                    ₹{costComponents.reduce((sum, c) => {
                      if (c.is_percentage) {
                        return sum + (selectedBill.grand_total * (c.amount / 100));
                      }
                      return sum + c.amount;
                    }, 0).toLocaleString()}
                  </p>
                </div>
                
                <div className="p-4 bg-green-50 rounded-lg border-2 border-green-200">
                  <p className="text-sm text-green-600">Estimated Landed Cost</p>
                  <p className="font-bold text-2xl text-green-700">
                    ₹{(selectedBill.grand_total + costComponents.reduce((sum, c) => {
                      if (c.is_percentage) {
                        return sum + (selectedBill.grand_total * (c.amount / 100));
                      }
                      return sum + c.amount;
                    }, 0)).toLocaleString()}
                  </p>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Package size={48} className="mx-auto mb-3 text-gray-300" />
                <p>Select a purchase bill to preview</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h2 className="font-semibold">Calculation History</h2>
          </div>
          <div className="divide-y">
            {history.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <FileText size={48} className="mx-auto mb-3 text-gray-300" />
                <p>No calculations yet</p>
              </div>
            ) : (
              history.map(record => (
                <div key={record.id} className="p-4 hover:bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium">{record.bill_number}</p>
                      <p className="text-sm text-gray-500">{record.vendor_name}</p>
                      <p className="text-xs text-gray-400">
                        {new Date(record.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-500">Base: ₹{record.base_total?.toLocaleString()}</p>
                      <p className="text-sm text-orange-600">+₹{record.total_additional_cost?.toLocaleString()}</p>
                      <p className="font-bold text-green-600">₹{record.landed_total?.toLocaleString()}</p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Templates Tab */}
      {activeTab === 'templates' && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b flex justify-between items-center">
            <h2 className="font-semibold">Cost Templates</h2>
            <button
              onClick={() => setShowTemplateModal(true)}
              className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 flex items-center gap-2"
            >
              <Plus size={18} />
              Create Template
            </button>
          </div>
          <div className="divide-y">
            {templates.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <Package size={48} className="mx-auto mb-3 text-gray-300" />
                <p>No templates created</p>
                <p className="text-sm">Create templates for frequently used cost structures</p>
              </div>
            ) : (
              templates.map(template => (
                <div key={template.id} className="p-4 hover:bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium flex items-center gap-2">
                        {template.name}
                        {template.is_default && (
                          <span className="text-xs bg-blue-100 text-blue-600 px-2 py-0.5 rounded">Default</span>
                        )}
                      </p>
                      <p className="text-sm text-gray-500">{template.description}</p>
                      <div className="flex gap-2 mt-2">
                        {template.components?.map((c, i) => (
                          <span key={i} className="text-xs bg-gray-100 px-2 py-1 rounded">
                            {c.name}: {c.is_percentage ? `${c.amount}%` : `₹${c.amount}`}
                          </span>
                        ))}
                      </div>
                    </div>
                    <button
                      onClick={() => { handleApplyTemplate(template); setActiveTab('calculate'); }}
                      className="px-3 py-1 text-orange-600 border border-orange-200 rounded hover:bg-orange-50"
                    >
                      Use Template
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Save Template Modal */}
      {showTemplateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <h2 className="text-xl font-bold mb-4">Save as Template</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Template Name *</label>
                <input
                  type="text"
                  value={templateForm.name}
                  onChange={(e) => setTemplateForm({...templateForm, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="e.g., Standard Import Costs"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <input
                  type="text"
                  value={templateForm.description}
                  onChange={(e) => setTemplateForm({...templateForm, description: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="Template description..."
                />
              </div>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={templateForm.is_default}
                  onChange={(e) => setTemplateForm({...templateForm, is_default: e.target.checked})}
                  className="rounded"
                />
                <span className="text-sm text-gray-600">Set as default template</span>
              </label>
            </div>
            <div className="mt-6 flex justify-end gap-2">
              <button
                onClick={() => setShowTemplateModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveTemplate}
                className="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
              >
                Save Template
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Calculation Result Modal */}
      {showCalculation && calculationResult && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b bg-green-600">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold text-white">Landed Cost Calculated</h2>
                <button onClick={() => setShowCalculation(false)} className="text-white hover:text-gray-200">
                  <X size={24} />
                </button>
              </div>
            </div>
            
            <div className="p-6 max-h-[60vh] overflow-y-auto">
              {/* Summary */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="p-4 bg-blue-50 rounded-lg text-center">
                  <p className="text-sm text-blue-600">Base Cost</p>
                  <p className="text-xl font-bold text-blue-700">
                    ₹{calculationResult.summary?.base_total?.toLocaleString()}
                  </p>
                </div>
                <div className="p-4 bg-orange-50 rounded-lg text-center">
                  <p className="text-sm text-orange-600">Additional Costs</p>
                  <p className="text-xl font-bold text-orange-700">
                    ₹{calculationResult.summary?.additional_costs?.toLocaleString()}
                  </p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg text-center">
                  <p className="text-sm text-green-600">Landed Total</p>
                  <p className="text-xl font-bold text-green-700">
                    ₹{calculationResult.summary?.landed_total?.toLocaleString()}
                  </p>
                  <p className="text-xs text-green-500">
                    +{calculationResult.summary?.cost_increase_percent}%
                  </p>
                </div>
              </div>
              
              {/* Item Details */}
              <h3 className="font-semibold mb-3">Item-wise Landed Cost</h3>
              <div className="border rounded-lg overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left">Item</th>
                      <th className="px-4 py-2 text-right">Base Cost</th>
                      <th className="px-4 py-2 text-right">Additional</th>
                      <th className="px-4 py-2 text-right">Landed Cost</th>
                      <th className="px-4 py-2 text-right">Unit Cost</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {calculationResult.items?.map((item, idx) => (
                      <tr key={idx}>
                        <td className="px-4 py-2">{item.product_name || item.description}</td>
                        <td className="px-4 py-2 text-right">₹{item.base_cost?.toLocaleString()}</td>
                        <td className="px-4 py-2 text-right text-orange-600">+₹{item.total_additional?.toLocaleString()}</td>
                        <td className="px-4 py-2 text-right font-bold">₹{item.landed_cost?.toLocaleString()}</td>
                        <td className="px-4 py-2 text-right text-green-600">₹{item.landed_unit_cost?.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            
            <div className="p-6 border-t bg-gray-50 flex justify-end gap-2">
              <button
                onClick={() => setShowCalculation(false)}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LandedCostCalculator;
