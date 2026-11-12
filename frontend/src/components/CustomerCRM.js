import { ViewQuotationModal } from './QuotationManagement';
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Users, TrendingUp, UserCheck, AlertCircle, Search, Filter, ArrowLeft, Eye, Download, Send } from 'lucide-react';
import { utils } from '../services/api';
import { BACKEND_URL } from '../config/api';
import { CustomerDetailModal } from './crm/CustomerDetailModal';

const CustomerCRM = () => {
  const navigate = useNavigate();
  const [customers, setCustomers] = useState([]);
  const [stats, setStats] = useState({});
  const [segments, setSegments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSegment, setSelectedSegment] = useState(null);
  const [selectedQuotation, setSelectedQuotation] = useState(null);
  const [showViewModal, setShowViewModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedCustomerId, setSelectedCustomerId] = useState(null);
  const [quotations, setQuotations] = useState([]);
  const [quotationsLoading, setQuotationsLoading] = useState(true);

  useEffect(() => {
    fetchCustomerData();
  }, [selectedSegment, currentPage]);

  const fetchCustomerData = async () => {
    try {
      setLoading(true);
      
      // Fetch customers with pagination and segmentation
      const customersUrl = selectedSegment 
        ? `/api/admin/customers/?page=${currentPage}&segment=${selectedSegment}`
        : `/api/admin/customers/?page=${currentPage}`;
      
      const customersRes = await utils.fetchAPI(customersUrl);
      const customersData = await customersRes.json();
      setCustomers(customersData.customers || []);

      // Fetch customer stats
      const statsRes = await utils.fetchAPI('/api/admin/customers/stats/summary');
      const statsData = await statsRes.json();
      setStats(statsData.data || {});

      // Fetch customer segments
      const segmentsRes = await utils.fetchAPI('/api/admin/customers/segments/breakdown');
      const segmentsData = await segmentsRes.json();
      setSegments(segmentsData.data || []);

      setLoading(false);

      // Fetch recent quotations
      try {
        const quotationsRes = await utils.fetchAPI('/api/quotations/list?limit=20');
        const quotationsData = await quotationsRes.json();
        setQuotations(quotationsData.quotations || []);
      } catch (qError) {
        console.error('Error fetching quotations:', qError);
      } finally {
        setQuotationsLoading(false);
      }
    } catch (error) {
      console.error('Error fetching customer data:', error);
      setLoading(false);
      setQuotationsLoading(false);
    }
  };

  const handleViewQuotation = async (quotationId) => {
    try {
      const response = await utils.fetchAPI(`/api/quotations/${quotationId}`);
      if (response.ok) {
        const data = await response.json();
        setSelectedQuotation(data.quotation);
        setShowViewModal(true);
      }
    } catch (error) {
      console.error('Failed to load quotation details:', error);
    }
  };

  const handleDownloadPDF = async (quotationId) => {
    try {
      window.open(`${BACKEND_URL}/api/quotations/${quotationId}/pdf`, '_blank');
    } catch (error) {
      console.error('Failed to download PDF:', error);
    }
  };

  const handleWhatsApp = async (quotationId) => {
    try {
      const response = await utils.fetchAPI(`/api/quotations/${quotationId}/whatsapp`);
      if (response.ok) {
        const data = await response.json();
        window.open(data.whatsapp_link, '_blank');
      }
    } catch (error) {
      console.error('Failed to generate WhatsApp link:', error);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    try {
      return new Date(dateStr).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  const quotationStatusBadge = (status) => {
    const s = (status || 'draft').toLowerCase();
    const styles = {
      draft: 'bg-gray-100 text-gray-700',
      sent: 'bg-blue-100 text-blue-800',
      accepted: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      expired: 'bg-orange-100 text-orange-800',
      converted: 'bg-purple-100 text-purple-800',
    };
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[s] || 'bg-gray-100 text-gray-700'}`}>
        {s.charAt(0).toUpperCase() + s.slice(1)}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading customer data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Customer Relationship Management</h1>
          <p className="text-gray-600">Manage and analyze your customer base</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-gray-600">Total Customers</CardTitle>
                <Users className="h-5 w-5 text-blue-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">{stats.total_customers || 0}</div>
              <p className="text-xs text-green-600 mt-1">+{stats.new_this_month || 0} this month</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-gray-600">VIP Customers</CardTitle>
                <TrendingUp className="h-5 w-5 text-purple-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">{stats.vip_customers || 0}</div>
              <p className="text-xs text-gray-500 mt-1">{'>'}{formatCurrency(50000)} spent</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-gray-600">Regular Customers</CardTitle>
                <UserCheck className="h-5 w-5 text-green-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">{stats.regular_customers || 0}</div>
              <p className="text-xs text-gray-500 mt-1">{'≥'}5 orders</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-gray-600">Average CLV</CardTitle>
                <TrendingUp className="h-5 w-5 text-orange-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">{formatCurrency(stats.average_clv || 0)}</div>
              <p className="text-xs text-gray-500 mt-1">Customer Lifetime Value</p>
            </CardContent>
          </Card>
        </div>

        {/* Segmentation Chart */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Customer Segmentation</CardTitle>
            <CardDescription>Distribution by spending tier</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {segments.map((segment, index) => (
                <div key={index} className="flex items-center">
                  <div className="w-32 text-sm font-medium text-gray-700">{segment.segment}</div>
                  <div className="flex-1 mx-4">
                    <div className="h-8 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-500"
                        style={{ 
                          width: `${((segment.count / (stats.total_customers || 1)) * 100)}%` 
                        }}
                      ></div>
                    </div>
                  </div>
                  <div className="w-16 text-right text-sm font-semibold text-gray-900">{segment.count}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Filters and Search */}
        <Card className="mb-8">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search customers by name, email, or phone..."
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setSelectedSegment(null)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    selectedSegment === null 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  All
                </button>
                <button
                  onClick={() => setSelectedSegment('vip')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    selectedSegment === 'vip' 
                      ? 'bg-purple-600 text-white' 
                      : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  VIP
                </button>
                <button
                  onClick={() => setSelectedSegment('regular')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    selectedSegment === 'regular' 
                      ? 'bg-green-600 text-white' 
                      : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  Regular
                </button>
                <button
                  onClick={() => setSelectedSegment('new')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    selectedSegment === 'new' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  New
                </button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Customer List */}
        <Card>
          <CardHeader>
            <CardTitle>Customers List</CardTitle>
            <CardDescription>
              {selectedSegment 
                ? `Showing ${selectedSegment} customers` 
                : 'All customers in your database'
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            {customers.length === 0 ? (
              <div className="text-center py-12">
                <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No Customers Found</h3>
                <p className="text-gray-600">
                  {selectedSegment 
                    ? `No customers in the ${selectedSegment} segment yet.` 
                    : 'No customers in the database yet. Start making sales to see customer data here!'
                  }
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 font-semibold text-sm text-gray-600">Customer</th>
                      <th className="text-left py-3 px-4 font-semibold text-sm text-gray-600">Contact</th>
                      <th className="text-right py-3 px-4 font-semibold text-sm text-gray-600">Orders</th>
                      <th className="text-right py-3 px-4 font-semibold text-sm text-gray-600">Total Spent</th>
                      <th className="text-center py-3 px-4 font-semibold text-sm text-gray-600">Segment</th>
                      <th className="text-center py-3 px-4 font-semibold text-sm text-gray-600">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {customers.map((customer, index) => (
                      <tr key={customer.id || index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                        <td className="py-4 px-4">
                          <div className="flex items-center">
                            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold">
                              {(customer.name || 'U')[0].toUpperCase()}
                            </div>
                            <div className="ml-3">
                              <div className="font-semibold text-gray-900">{customer.name || 'Unknown'}</div>
                              <div className="text-sm text-gray-500">{customer.id}</div>
                            </div>
                          </div>
                        </td>
                        <td className="py-4 px-4">
                          <div className="text-sm text-gray-900">{customer.email}</div>
                          <div className="text-sm text-gray-500">{customer.phone}</div>
                        </td>
                        <td className="py-4 px-4 text-right">
                          <span className="text-sm font-semibold text-gray-900">{customer.order_count || 0}</span>
                        </td>
                        <td className="py-4 px-4 text-right">
                          <span className="text-sm font-semibold text-gray-900">
                            {formatCurrency(customer.total_spent || 0)}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-center">
                          {(customer.total_spent || 0) >= 50000 ? (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                              VIP
                            </span>
                          ) : (customer.order_count || 0) >= 5 ? (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              Regular
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              New
                            </span>
                          )}
                        </td>
                        <td className="py-4 px-4 text-center">
                          <button
                            onClick={() => setSelectedCustomerId(customer.id)}
                            className="text-blue-600 hover:text-blue-800 font-medium text-sm"
                            data-testid={`view-customer-btn-${customer.id}`}
                          >
                            View Details
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quotations Section */}
        <Card className="mb-8 mt-8">
          <CardHeader>
            <CardTitle>Quotations</CardTitle>
            <CardDescription>All quotations created, across all customers</CardDescription>
          </CardHeader>
          <CardContent>
            {quotationsLoading ? (
              <div className="text-center py-8 text-gray-500 text-sm">Loading quotations...</div>
            ) : quotations.length === 0 ? (
              <div className="text-center py-12">
                <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No Quotations Found</h3>
                <p className="text-gray-600">Quotations you create will show up here.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 font-semibold text-sm text-gray-600">Quotation #</th>
                      <th className="text-left py-3 px-4 font-semibold text-sm text-gray-600">Customer</th>
                      <th className="text-left py-3 px-4 font-semibold text-sm text-gray-600">Contact</th>
                      <th className="text-right py-3 px-4 font-semibold text-sm text-gray-600">Amount</th>
                      <th className="text-center py-3 px-4 font-semibold text-sm text-gray-600">Status</th>
                      <th className="text-right py-3 px-4 font-semibold text-sm text-gray-600">Created</th>
                      <th className="text-center py-3 px-4 font-semibold text-sm text-gray-600">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {quotations.map((q, index) => (
                      <tr key={q.id || index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                        <td className="py-4 px-4">
                          <span className="font-semibold text-orange-600">{q.quotation_number || '-'}</span>
                        </td>
                        <td className="py-4 px-4">
                          <span className="text-sm text-gray-900">{q.customer_name || 'Unknown'}</span>
                        </td>
                        <td className="py-4 px-4">
                          <span className="text-sm text-gray-500">{q.customer_phone || '-'}</span>
                        </td>
                        <td className="py-4 px-4 text-right">
                          <span className="text-sm font-semibold text-gray-900">
                            {formatCurrency(q.totals?.grand_total || q.total_amount || q.grand_total || q.total || 0)}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-center">
                          {quotationStatusBadge(q.status)}
                        </td>
                        <td className="py-4 px-4 text-right">
                          <span className="text-sm text-gray-500">{formatDate(q.created_at)}</span>
                        </td>
                        <td className="py-4 px-4">
                          <div className="flex items-center justify-center space-x-1">
                            <button
                              onClick={() => handleViewQuotation(q.id)}
                              className="p-2 text-gray-500 hover:text-amber-600 hover:bg-amber-50 rounded-lg"
                              title="View"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDownloadPDF(q.id)}
                              className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg"
                              title="Download PDF"
                            >
                              <Download className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleWhatsApp(q.id)}
                              className="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg"
                              title="Share on WhatsApp"
                            >
                              <Send className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>

        {selectedCustomerId && (
          <CustomerDetailModal
            customerId={selectedCustomerId}
            onClose={() => setSelectedCustomerId(null)}
          />
        )}

        {showViewModal && selectedQuotation && (
          <ViewQuotationModal
            quotation={selectedQuotation}
            onClose={() => setShowViewModal(false)}
            onDownload={() => handleDownloadPDF(selectedQuotation.id)}
            onWhatsApp={() => handleWhatsApp(selectedQuotation.id)}
            API_URL={BACKEND_URL}
          />
        )}
      </div>
    </div>
  );
};

export default CustomerCRM;
