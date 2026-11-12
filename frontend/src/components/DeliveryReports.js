import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { useNavigate } from 'react-router-dom';
import { 
  Truck, ArrowLeft, RefreshCw, Calendar, Download, 
  CheckCircle, Clock, XCircle, TrendingUp, Users, FileText,
  ChevronDown, ChevronUp
} from 'lucide-react';

const DeliveryReports = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [reportData, setReportData] = useState(null);
  const [dateRange, setDateRange] = useState({
    start_date: new Date(new Date().setDate(1)).toISOString().split('T')[0], // First of month
    end_date: new Date().toISOString().split('T')[0] // Today
  });
  const [expandedDriver, setExpandedDriver] = useState(null);

  useEffect(() => {
    fetchReports();
  }, [dateRange]);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (dateRange.start_date) params.append('start_date', dateRange.start_date);
      if (dateRange.end_date) params.append('end_date', dateRange.end_date);
      
      const response = await fetch(`${BACKEND_URL}/api/delivery-challans/reports/summary?${params}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setReportData(data);
      }
    } catch (error) {
      console.error('Error fetching delivery reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric'
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'delivered': return 'bg-green-100 text-green-700';
      case 'in_transit': return 'bg-blue-100 text-blue-700';
      case 'failed': return 'bg-red-100 text-red-700';
      default: return 'bg-amber-100 text-amber-700';
    }
  };

  const exportToCSV = () => {
    if (!reportData?.challans?.length) return;
    
    const headers = ['Challan #', 'Invoice/SO #', 'Driver', 'Vehicle', 'Customer', 'Amount', 'Status', 'Created Date'];
    const rows = reportData.challans.map(c => [
      c.challan_number,
      c.invoice_number || c.so_number || '-',
      c.delivery_person_name || 'Unassigned',
      c.vehicle_number || '-',
      c.customer?.name || '-',
      c.total_amount || 0,
      c.status,
      c.created_at?.split('T')[0] || '-'
    ]);
    
    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `delivery-report-${dateRange.start_date}-${dateRange.end_date}.csv`;
    a.click();
  };

  if (loading && !reportData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 text-teal-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading delivery reports...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate(-1)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                  <Truck className="w-6 h-6 text-teal-600" />
                  Delivery Reports
                </h1>
                <p className="text-sm text-gray-500">Track delivery performance and driver statistics</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={fetchReports}
                disabled={loading}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="Refresh"
              >
                <RefreshCw className={`w-5 h-5 text-gray-600 ${loading ? 'animate-spin' : ''}`} />
              </button>
              <button
                onClick={exportToCSV}
                disabled={!reportData?.challans?.length}
                className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 flex items-center gap-2 disabled:opacity-50"
              >
                <Download className="w-4 h-4" />
                Export CSV
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* Date Filter */}
        <div className="bg-white rounded-xl shadow-sm p-4">
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">Date Range:</span>
            </div>
            <input
              type="date"
              value={dateRange.start_date}
              onChange={(e) => setDateRange({...dateRange, start_date: e.target.value})}
              className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:outline-none"
            />
            <span className="text-gray-500">to</span>
            <input
              type="date"
              value={dateRange.end_date}
              onChange={(e) => setDateRange({...dateRange, end_date: e.target.value})}
              className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:outline-none"
            />
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <div className="bg-white rounded-xl shadow-sm p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <FileText className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-xs text-gray-500">Total Challans</p>
                <p className="text-xl font-bold text-gray-800">{reportData?.summary?.total_challans || 0}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-xs text-gray-500">Completed</p>
                <p className="text-xl font-bold text-green-600">{reportData?.summary?.completed || 0}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-amber-100 rounded-lg">
                <Clock className="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <p className="text-xs text-gray-500">Pending</p>
                <p className="text-xl font-bold text-amber-600">{reportData?.summary?.pending || 0}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <XCircle className="w-5 h-5 text-red-600" />
              </div>
              <div>
                <p className="text-xs text-gray-500">Failed</p>
                <p className="text-xl font-bold text-red-600">{reportData?.summary?.failed || 0}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <TrendingUp className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <p className="text-xs text-gray-500">Completion Rate</p>
                <p className="text-xl font-bold text-purple-600">{reportData?.summary?.completion_rate || 0}%</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-teal-100 rounded-lg">
                <Users className="w-5 h-5 text-teal-600" />
              </div>
              <div>
                <p className="text-xs text-gray-500">Active Drivers</p>
                <p className="text-xl font-bold text-teal-600">{reportData?.driver_stats?.length || 0}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Driver-wise Performance */}
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="p-4 border-b bg-purple-50">
            <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
              <Users className="w-5 h-5 text-purple-600" />
              Driver-wise Performance
            </h2>
          </div>
          
          {reportData?.driver_stats?.length > 0 ? (
            <div className="divide-y">
              {reportData.driver_stats.map((driver, index) => (
                <div key={index} className="hover:bg-gray-50">
                  <div 
                    className="p-4 cursor-pointer flex items-center justify-between"
                    onClick={() => setExpandedDriver(expandedDriver === index ? null : index)}
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                        <span className="text-purple-700 font-semibold">
                          {driver.driver_name?.charAt(0)?.toUpperCase() || 'D'}
                        </span>
                      </div>
                      <div>
                        <p className="font-medium text-gray-800">{driver.driver_name}</p>
                        <p className="text-sm text-gray-500">{driver.total_deliveries} total deliveries</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-6">
                      <div className="text-center">
                        <p className="text-lg font-bold text-green-600">{driver.completed}</p>
                        <p className="text-xs text-gray-500">Completed</p>
                      </div>
                      <div className="text-center">
                        <p className="text-lg font-bold text-amber-600">{driver.pending + driver.in_transit}</p>
                        <p className="text-xs text-gray-500">Pending</p>
                      </div>
                      <div className="text-center">
                        <p className="text-lg font-bold text-red-600">{driver.failed}</p>
                        <p className="text-xs text-gray-500">Failed</p>
                      </div>
                      <div className="text-center">
                        <p className="text-lg font-bold text-teal-600">{formatCurrency(driver.collected_amount)}</p>
                        <p className="text-xs text-gray-500">Collected</p>
                      </div>
                      {expandedDriver === index ? (
                        <ChevronUp className="w-5 h-5 text-gray-400" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-gray-400" />
                      )}
                    </div>
                  </div>
                  
                  {/* Expanded - Show driver's challans */}
                  {expandedDriver === index && (
                    <div className="bg-gray-50 px-4 pb-4">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="text-left text-gray-500">
                            <th className="pb-2">Challan #</th>
                            <th className="pb-2">Invoice/SO</th>
                            <th className="pb-2">Customer</th>
                            <th className="pb-2">Amount</th>
                            <th className="pb-2">Status</th>
                            <th className="pb-2">Date</th>
                          </tr>
                        </thead>
                        <tbody>
                          {reportData.challans
                            .filter(c => c.delivery_person_name === driver.driver_name)
                            .map((challan) => (
                              <tr key={challan.id} className="border-t border-gray-200">
                                <td className="py-2 font-medium text-blue-600">{challan.challan_number}</td>
                                <td className="py-2">{challan.invoice_number || '-'}</td>
                                <td className="py-2">{challan.customer?.name || '-'}</td>
                                <td className="py-2">{formatCurrency(challan.total_amount)}</td>
                                <td className="py-2">
                                  <span className={`px-2 py-0.5 text-xs rounded-full ${getStatusColor(challan.status)}`}>
                                    {challan.status?.replace('_', ' ')}
                                  </span>
                                </td>
                                <td className="py-2 text-gray-500">{formatDate(challan.created_at)}</td>
                              </tr>
                            ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center text-gray-500">
              <Users className="w-12 h-12 text-gray-300 mx-auto mb-2" />
              <p>No delivery data for the selected period</p>
            </div>
          )}
        </div>

        {/* All Challans List */}
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="p-4 border-b bg-blue-50">
            <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" />
              All Delivery Challans
            </h2>
          </div>
          
          {reportData?.challans?.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium text-gray-600">Challan #</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-600">Invoice/SO #</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-600">Driver</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-600">Vehicle</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-600">Customer</th>
                    <th className="px-4 py-3 text-right font-medium text-gray-600">Amount</th>
                    <th className="px-4 py-3 text-center font-medium text-gray-600">Status</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-600">Created</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {reportData.challans.map((challan) => (
                    <tr key={challan.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium text-blue-600">{challan.challan_number}</td>
                      <td className="px-4 py-3">{challan.invoice_number || challan.so_number || '-'}</td>
                      <td className="px-4 py-3">{challan.delivery_person_name || 'Unassigned'}</td>
                      <td className="px-4 py-3">{challan.vehicle_number || '-'}</td>
                      <td className="px-4 py-3">
                        <div>
                          <p className="font-medium">{challan.customer?.name || '-'}</p>
                          <p className="text-xs text-gray-500">{challan.customer?.city}</p>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-right font-medium">{formatCurrency(challan.total_amount)}</td>
                      <td className="px-4 py-3 text-center">
                        <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(challan.status)}`}>
                          {challan.status?.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-500">{formatDate(challan.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-8 text-center text-gray-500">
              <FileText className="w-12 h-12 text-gray-300 mx-auto mb-2" />
              <p>No delivery challans found for the selected period</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DeliveryReports;
