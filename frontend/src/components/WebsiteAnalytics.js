import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  MessageSquare, 
  Users, 
  ShoppingCart, 
  TrendingUp,
  Mail,
  Clock,
  Bot,
  Send,
  RefreshCw,
  ChevronRight,
  AlertCircle,
  CheckCircle,
  XCircle,
  Eye,
  Filter,
  Download,
  ArrowLeft,
  Search,
  Phone,
  DollarSign,
  Package,
  Calendar,
  BarChart3,
  PieChart
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { useNavigate } from 'react-router-dom';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';

const WebsiteAnalytics = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('ai-chat');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // AI Chat State
  const [chatSummary, setChatSummary] = useState(null);
  const [chatSessions, setChatSessions] = useState([]);
  const [chatPage, setChatPage] = useState(1);
  const [chatTotalPages, setChatTotalPages] = useState(1);
  const [selectedSession, setSelectedSession] = useState(null);
  const [sessionMessages, setSessionMessages] = useState([]);
  
  // Consultations State
  const [consultationSummary, setConsultationSummary] = useState(null);
  const [consultations, setConsultations] = useState([]);
  const [consultationPage, setConsultationPage] = useState(1);
  const [consultationTotalPages, setConsultationTotalPages] = useState(1);
  const [consultationFilter, setConsultationFilter] = useState('');
  
  // Abandoned Carts State
  const [cartSummary, setCartSummary] = useState(null);
  const [abandonedCarts, setAbandonedCarts] = useState([]);
  const [cartPage, setCartPage] = useState(1);
  const [cartTotalPages, setCartTotalPages] = useState(1);
  const [selectedCart, setSelectedCart] = useState(null);
  const [recoveryEmail, setRecoveryEmail] = useState('');
  const [recoveryMessage, setRecoveryMessage] = useState('');
  const [sendingRecovery, setSendingRecovery] = useState(false);
  const [showRecoveryDialog, setShowRecoveryDialog] = useState(false);
  
  const getAuthToken = () => {
    return localStorage.getItem('adminToken');
  };
  
  const fetchWithAuth = async (url, options = {}) => {
    const token = getAuthToken();
    return fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
  };

  // ======================= AI CHAT FUNCTIONS =======================
  
  const fetchChatSummary = async () => {
    try {
      const response = await fetchWithAuth(`${BACKEND_URL}/api/website-analytics/ai-chat/summary?days=30`);
      const data = await response.json();
      if (data.status === 'success') {
        setChatSummary(data);
      }
    } catch (err) {
      console.error('Error fetching chat summary:', err);
    }
  };
  
  const fetchChatSessions = async (page = 1) => {
    try {
      const response = await fetchWithAuth(`${BACKEND_URL}/api/website-analytics/ai-chat/sessions?page=${page}&limit=10`);
      const data = await response.json();
      if (data.status === 'success') {
        setChatSessions(data.sessions);
        setChatTotalPages(data.pages);
      }
    } catch (err) {
      console.error('Error fetching chat sessions:', err);
    }
  };
  
  const fetchSessionDetail = async (sessionId) => {
    try {
      const response = await fetchWithAuth(`${BACKEND_URL}/api/website-analytics/ai-chat/session/${sessionId}`);
      const data = await response.json();
      if (data.status === 'success') {
        setSessionMessages(data.messages);
      }
    } catch (err) {
      console.error('Error fetching session detail:', err);
    }
  };

  // ======================= CONSULTATION FUNCTIONS =======================
  
  const fetchConsultationSummary = async () => {
    try {
      const response = await fetchWithAuth(`${BACKEND_URL}/api/website-analytics/consultations/summary?days=30`);
      const data = await response.json();
      if (data.status === 'success') {
        setConsultationSummary(data);
      }
    } catch (err) {
      console.error('Error fetching consultation summary:', err);
    }
  };
  
  const fetchConsultations = async (page = 1, status = '') => {
    try {
      let url = `${BACKEND_URL}/api/website-analytics/consultations/list?page=${page}&limit=10`;
      if (status) url += `&status=${status}`;
      
      const response = await fetchWithAuth(url);
      const data = await response.json();
      if (data.status === 'success') {
        setConsultations(data.consultations);
        setConsultationTotalPages(data.pages);
      }
    } catch (err) {
      console.error('Error fetching consultations:', err);
    }
  };

  // ======================= ABANDONED CART FUNCTIONS =======================
  
  const fetchCartSummary = async () => {
    try {
      const response = await fetchWithAuth(`${BACKEND_URL}/api/website-analytics/abandoned-carts/summary?days=30`);
      const data = await response.json();
      if (data.status === 'success') {
        setCartSummary(data);
      }
    } catch (err) {
      console.error('Error fetching cart summary:', err);
    }
  };
  
  const fetchAbandonedCarts = async (page = 1) => {
    try {
      const response = await fetchWithAuth(`${BACKEND_URL}/api/website-analytics/abandoned-carts/list?page=${page}&limit=10`);
      const data = await response.json();
      if (data.status === 'success') {
        setAbandonedCarts(data.carts);
        setCartTotalPages(data.pages);
      }
    } catch (err) {
      console.error('Error fetching abandoned carts:', err);
    }
  };
  
  const sendRecoveryEmail = async () => {
    if (!selectedCart || !recoveryEmail) return;
    
    setSendingRecovery(true);
    try {
      const response = await fetchWithAuth(`${BACKEND_URL}/api/website-analytics/abandoned-carts/send-recovery-email`, {
        method: 'POST',
        body: JSON.stringify({
          session_id: selectedCart.session_id,
          email: recoveryEmail,
          custom_message: recoveryMessage || null
        })
      });
      
      const data = await response.json();
      if (data.status === 'success') {
        alert(`Recovery email sent to ${recoveryEmail}!`);
        setShowRecoveryDialog(false);
        setSelectedCart(null);
        setRecoveryEmail('');
        setRecoveryMessage('');
        fetchAbandonedCarts(cartPage);
      } else {
        alert(`Error: ${data.detail || 'Failed to send email'}`);
      }
    } catch (err) {
      console.error('Error sending recovery email:', err);
      alert('Failed to send recovery email');
    } finally {
      setSendingRecovery(false);
    }
  };
  
  const sendBulkRecoveryEmails = async () => {
    if (!window.confirm('This will send recovery emails to all eligible carts (users with email, cart value > ₹10,000). Continue?')) {
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetchWithAuth(`${BACKEND_URL}/api/website-analytics/abandoned-carts/bulk-recovery?min_value=10000&max_emails=50`, {
        method: 'POST'
      });
      
      const data = await response.json();
      if (data.status === 'success') {
        alert(`Queued ${data.emails_queued} recovery emails!`);
        fetchAbandonedCarts(cartPage);
      }
    } catch (err) {
      console.error('Error sending bulk recovery:', err);
      alert('Failed to send bulk recovery emails');
    } finally {
      setLoading(false);
    }
  };

  // ======================= EFFECTS =======================
  
  useEffect(() => {
    if (activeTab === 'ai-chat') {
      fetchChatSummary();
      fetchChatSessions(chatPage);
    } else if (activeTab === 'consultations') {
      fetchConsultationSummary();
      fetchConsultations(consultationPage, consultationFilter);
    } else if (activeTab === 'abandoned-carts') {
      fetchCartSummary();
      fetchAbandonedCarts(cartPage);
    }
  }, [activeTab]);
  
  useEffect(() => {
    if (activeTab === 'ai-chat') {
      fetchChatSessions(chatPage);
    }
  }, [chatPage]);
  
  useEffect(() => {
    if (activeTab === 'consultations') {
      fetchConsultations(consultationPage, consultationFilter);
    }
  }, [consultationPage, consultationFilter]);
  
  useEffect(() => {
    if (activeTab === 'abandoned-carts') {
      fetchAbandonedCarts(cartPage);
    }
  }, [cartPage]);

  // ======================= HELPER COMPONENTS =======================
  
  const StatCard = ({ title, value, icon: Icon, color = 'blue', subtitle }) => (
    <Card className="bg-white">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500">{title}</p>
            <p className="text-2xl font-bold mt-1">{value}</p>
            {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
          </div>
          <div className={`p-3 rounded-full bg-${color}-100`}>
            <Icon className={`w-6 h-6 text-${color}-600`} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
  
  const SimpleBarChart = ({ data, title }) => {
    if (!data || data.length === 0) return null;
    const maxValue = Math.max(...data.map(d => d.count));
    
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {data.slice(-7).map((item, index) => (
              <div key={index} className="flex items-center gap-2">
                <span className="text-xs text-gray-500 w-20">{item.date?.slice(5) || item.appliance}</span>
                <div className="flex-1 bg-gray-100 rounded-full h-4">
                  <div 
                    className="bg-gradient-to-r from-indigo-500 to-purple-500 h-4 rounded-full transition-all duration-300"
                    style={{ width: `${(item.count / maxValue) * 100}%` }}
                  />
                </div>
                <span className="text-xs font-medium w-8">{item.count}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  };

  const Pagination = ({ currentPage, totalPages, onPageChange }) => (
    <div className="flex items-center justify-center gap-2 mt-4">
      <Button
        variant="outline"
        size="sm"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage <= 1}
      >
        Previous
      </Button>
      <span className="text-sm text-gray-600">
        Page {currentPage} of {totalPages}
      </span>
      <Button
        variant="outline"
        size="sm"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage >= totalPages}
      >
        Next
      </Button>
    </div>
  );

  // ======================= RENDER AI CHAT TAB =======================
  
  const renderAIChatTab = () => (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          title="Total Messages" 
          value={chatSummary?.summary?.total_messages || 0}
          icon={MessageSquare}
          color="blue"
          subtitle={`${chatSummary?.summary?.recent_messages || 0} in last 30 days`}
        />
        <StatCard 
          title="Total Sessions" 
          value={chatSummary?.summary?.total_sessions || 0}
          icon={Users}
          color="green"
          subtitle={`${chatSummary?.summary?.recent_sessions || 0} recent`}
        />
        <StatCard 
          title="Avg Messages/Session" 
          value={chatSummary?.summary?.avg_messages_per_session || 0}
          icon={TrendingUp}
          color="purple"
        />
        <StatCard 
          title="Max in Single Session" 
          value={chatSummary?.summary?.max_messages_in_session || 0}
          icon={BarChart3}
          color="orange"
        />
      </div>
      
      {/* Agent Breakdown */}
      {chatSummary?.agent_breakdown && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Bot className="w-5 h-5" />
              Agent Type Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              {Object.entries(chatSummary.agent_breakdown).map(([agent, count]) => (
                <div key={agent} className="flex items-center gap-2 bg-gray-50 px-4 py-2 rounded-lg">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    agent === 'sales' ? 'bg-blue-100 text-blue-700' :
                    agent === 'service' ? 'bg-green-100 text-green-700' :
                    agent === 'delivery' ? 'bg-orange-100 text-orange-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {agent?.charAt(0).toUpperCase() + agent?.slice(1)}
                  </span>
                  <span className="font-bold">{count}</span>
                  <span className="text-gray-500 text-sm">messages</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Daily Trend Chart */}
      {chatSummary?.daily_trend && (
        <SimpleBarChart data={chatSummary.daily_trend} title="Daily Message Trend (Last 7 Days)" />
      )}
      
      {/* Sessions List */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Recent Chat Sessions</CardTitle>
          <CardDescription>Click on a session to view the full conversation</CardDescription>
        </CardHeader>
        <CardContent>
          {selectedSession ? (
            <div className="space-y-4">
              <Button 
                variant="ghost" 
                onClick={() => { setSelectedSession(null); setSessionMessages([]); }}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="w-4 h-4" /> Back to Sessions
              </Button>
              
              <div className="border rounded-lg p-4 max-h-96 overflow-y-auto space-y-3">
                {sessionMessages.map((msg, index) => (
                  <div 
                    key={index}
                    className={`p-3 rounded-lg ${
                      msg.sender === 'user' 
                        ? 'bg-blue-50 ml-8' 
                        : 'bg-gray-50 mr-8'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`text-xs font-medium ${
                        msg.sender === 'user' ? 'text-blue-600' : 'text-gray-600'
                      }`}>
                        {msg.sender === 'user' ? 'Customer' : `AI (${msg.agent_type})`}
                      </span>
                      <span className="text-xs text-gray-400">
                        {new Date(msg.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-sm whitespace-pre-wrap">{msg.message}</p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              {chatSessions.map((session) => (
                <div 
                  key={session.session_id}
                  onClick={() => {
                    setSelectedSession(session);
                    fetchSessionDetail(session.session_id);
                  }}
                  className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        {session.agent_types?.map(type => (
                          <Badge key={type} variant="outline" className="text-xs">
                            {type}
                          </Badge>
                        ))}
                        <span className="text-xs text-gray-400">
                          {session.message_count} messages
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 truncate">
                        {session.preview || 'No preview available'}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        {session.last_message && new Date(session.last_message).toLocaleString()}
                      </p>
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-400" />
                  </div>
                </div>
              ))}
              
              <Pagination 
                currentPage={chatPage}
                totalPages={chatTotalPages}
                onPageChange={setChatPage}
              />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );

  // ======================= RENDER CONSULTATIONS TAB =======================
  
  const renderConsultationsTab = () => (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          title="Total Consultations" 
          value={consultationSummary?.summary?.total_consultations || 0}
          icon={Users}
          color="indigo"
          subtitle={`${consultationSummary?.summary?.recent_consultations || 0} in last 30 days`}
        />
        <StatCard 
          title="Pending" 
          value={consultationSummary?.summary?.pending || 0}
          icon={Clock}
          color="yellow"
        />
        <StatCard 
          title="Completed" 
          value={consultationSummary?.summary?.completed || 0}
          icon={CheckCircle}
          color="green"
        />
        <StatCard 
          title="Emails Sent" 
          value={consultationSummary?.summary?.emails_sent || 0}
          icon={Mail}
          color="blue"
        />
      </div>
      
      {/* Budget Stats */}
      {consultationSummary?.budget_stats && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <DollarSign className="w-5 h-5" />
              Budget Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500">Avg Min Budget</p>
                <p className="text-lg font-bold">₹{(consultationSummary.budget_stats.avg_budget_min / 1000).toFixed(0)}K</p>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500">Avg Max Budget</p>
                <p className="text-lg font-bold">₹{(consultationSummary.budget_stats.avg_budget_max / 1000).toFixed(0)}K</p>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500">Highest Budget</p>
                <p className="text-lg font-bold">₹{(consultationSummary.budget_stats.max_budget / 100000).toFixed(1)}L</p>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500">Lowest Budget</p>
                <p className="text-lg font-bold">₹{(consultationSummary.budget_stats.min_budget / 1000).toFixed(0)}K</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Top Appliance Interests */}
      {consultationSummary?.appliance_interests && consultationSummary.appliance_interests.length > 0 && (
        <SimpleBarChart 
          data={consultationSummary.appliance_interests.map(a => ({ 
            date: a.appliance?.charAt(0).toUpperCase() + a.appliance?.slice(1).replace('_', ' '),
            count: a.count 
          }))} 
          title="Top Appliance Interests" 
        />
      )}
      
      {/* Consultations List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg">Consultation Requests</CardTitle>
              <CardDescription>Manage customer consultation requests</CardDescription>
            </div>
            <div className="flex gap-2">
              <select
                value={consultationFilter}
                onChange={(e) => setConsultationFilter(e.target.value)}
                className="border rounded-md px-3 py-1.5 text-sm"
              >
                <option value="">All Status</option>
                <option value="pending">Pending</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {consultations.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Users className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No consultation requests found</p>
            </div>
          ) : (
            <div className="space-y-3">
              {consultations.map((consultation) => (
                <div 
                  key={consultation.id}
                  className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{consultation.customer_name}</span>
                        <Badge variant={consultation.status === 'completed' ? 'default' : 'outline'}>
                          {consultation.status}
                        </Badge>
                        {consultation.email_sent && (
                          <Badge variant="outline" className="text-green-600 border-green-600">
                            <Mail className="w-3 h-3 mr-1" /> Sent
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-gray-500">{consultation.email}</p>
                      {consultation.phone && (
                        <p className="text-sm text-gray-500 flex items-center gap-1">
                          <Phone className="w-3 h-3" /> {consultation.phone}
                        </p>
                      )}
                      {consultation.requirements && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {consultation.requirements.appliance_types?.slice(0, 3).map(type => (
                            <Badge key={type} variant="secondary" className="text-xs">
                              {type}
                            </Badge>
                          ))}
                          <Badge variant="outline" className="text-xs">
                            ₹{(consultation.requirements.budget_min / 1000).toFixed(0)}K - ₹{(consultation.requirements.budget_max / 1000).toFixed(0)}K
                          </Badge>
                        </div>
                      )}
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-400">
                        {new Date(consultation.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
              
              <Pagination 
                currentPage={consultationPage}
                totalPages={consultationTotalPages}
                onPageChange={setConsultationPage}
              />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );

  // ======================= RENDER ABANDONED CARTS TAB =======================
  
  const renderAbandonedCartsTab = () => (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          title="Total Carts" 
          value={cartSummary?.summary?.total_carts || 0}
          icon={ShoppingCart}
          color="orange"
          subtitle={`${cartSummary?.summary?.carts_with_items || 0} with items`}
        />
        <StatCard 
          title="Potential Value" 
          value={`₹${((cartSummary?.summary?.total_potential_value || 0) / 1000).toFixed(0)}K`}
          icon={DollarSign}
          color="green"
        />
        <StatCard 
          title="High Value Carts" 
          value={cartSummary?.summary?.high_value_carts || 0}
          icon={TrendingUp}
          color="purple"
          subtitle="> ₹50,000"
        />
        <StatCard 
          title="Unique Products" 
          value={cartSummary?.summary?.unique_products_in_carts || 0}
          icon={Package}
          color="blue"
        />
      </div>
      
      {/* Most Abandoned Products */}
      {cartSummary?.most_abandoned_products && cartSummary.most_abandoned_products.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Package className="w-5 h-5" />
              Most Abandoned Products
            </CardTitle>
            <CardDescription>Products frequently left in carts</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {cartSummary.most_abandoned_products.slice(0, 6).map((product, index) => (
                <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  {product.image && (
                    <img 
                      src={product.image} 
                      alt={product.name}
                      className="w-12 h-12 object-cover rounded"
                    />
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{product.name}</p>
                    <p className="text-xs text-gray-500">₹{product.price?.toLocaleString()}</p>
                    <p className="text-xs text-orange-600">{product.abandonment_count} abandoned</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Actions */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg">Recovery Actions</CardTitle>
              <CardDescription>Send recovery emails to bring customers back</CardDescription>
            </div>
            <Button 
              onClick={sendBulkRecoveryEmails}
              disabled={loading}
              className="bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600"
            >
              {loading ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Send className="w-4 h-4 mr-2" />
              )}
              Send Bulk Recovery
            </Button>
          </div>
        </CardHeader>
      </Card>
      
      {/* Abandoned Carts List */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Abandoned Carts</CardTitle>
          <CardDescription>Carts with items that were not checked out</CardDescription>
        </CardHeader>
        <CardContent>
          {abandonedCarts.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <ShoppingCart className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No abandoned carts found</p>
            </div>
          ) : (
            <div className="space-y-3">
              {abandonedCarts.map((cart, index) => (
                <div 
                  key={cart.session_id || index}
                  className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">
                          {cart.user_info?.name || cart.user_info?.email || 'Guest User'}
                        </span>
                        <Badge variant="outline" className="text-orange-600 border-orange-600">
                          ₹{cart.cart_value?.toLocaleString()}
                        </Badge>
                        {cart.recovery_email_sent && (
                          <Badge variant="outline" className="text-green-600 border-green-600">
                            <Mail className="w-3 h-3 mr-1" /> Recovery Sent
                          </Badge>
                        )}
                      </div>
                      
                      {cart.user_info?.email && (
                        <p className="text-sm text-gray-500">{cart.user_info.email}</p>
                      )}
                      
                      <div className="flex flex-wrap gap-2">
                        {cart.items?.slice(0, 3).map((item, idx) => (
                          <div key={idx} className="flex items-center gap-2 bg-gray-100 rounded px-2 py-1">
                            {item.image && (
                              <img src={item.image} alt="" className="w-6 h-6 object-cover rounded" />
                            )}
                            <span className="text-xs truncate max-w-32">{item.name}</span>
                            <span className="text-xs text-gray-500">x{item.quantity}</span>
                          </div>
                        ))}
                        {cart.items?.length > 3 && (
                          <span className="text-xs text-gray-500 flex items-center">
                            +{cart.items.length - 3} more
                          </span>
                        )}
                      </div>
                      
                      <p className="text-xs text-gray-400">
                        Last updated: {cart.updated_at ? new Date(cart.updated_at).toLocaleString() : 'N/A'}
                      </p>
                    </div>
                    
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setSelectedCart(cart);
                          setRecoveryEmail(cart.user_info?.email || '');
                          setShowRecoveryDialog(true);
                        }}
                        disabled={cart.recovery_email_sent}
                      >
                        <Mail className="w-4 h-4 mr-1" />
                        {cart.recovery_email_sent ? 'Sent' : 'Send Email'}
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
              
              <Pagination 
                currentPage={cartPage}
                totalPages={cartTotalPages}
                onPageChange={setCartPage}
              />
            </div>
          )}
        </CardContent>
      </Card>
      
      {/* Recovery Email Dialog */}
      <Dialog open={showRecoveryDialog} onOpenChange={setShowRecoveryDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Send Recovery Email</DialogTitle>
            <DialogDescription>
              Send a recovery email to bring the customer back to complete their purchase.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div>
              <label className="text-sm font-medium">Email Address</label>
              <Input
                type="email"
                value={recoveryEmail}
                onChange={(e) => setRecoveryEmail(e.target.value)}
                placeholder="customer@email.com"
                className="mt-1"
              />
            </div>
            
            <div>
              <label className="text-sm font-medium">Custom Message (Optional)</label>
              <textarea
                value={recoveryMessage}
                onChange={(e) => setRecoveryMessage(e.target.value)}
                placeholder="Add a personal touch to your recovery email..."
                className="w-full mt-1 p-2 border rounded-md text-sm"
                rows={3}
              />
            </div>
            
            {selectedCart && (
              <div className="bg-gray-50 p-3 rounded-lg">
                <p className="text-sm font-medium mb-2">Cart Summary:</p>
                <p className="text-sm text-gray-600">
                  {selectedCart.item_count} items worth ₹{selectedCart.cart_value?.toLocaleString()}
                </p>
              </div>
            )}
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowRecoveryDialog(false)}>
              Cancel
            </Button>
            <Button 
              onClick={sendRecoveryEmail}
              disabled={!recoveryEmail || sendingRecovery}
              className="bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600"
            >
              {sendingRecovery ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Send className="w-4 h-4 mr-2" />
              )}
              Send Recovery Email
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );

  // ======================= MAIN RENDER =======================
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/admin')}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                Back
              </Button>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Website Analytics</h1>
                <p className="text-sm text-gray-500">AI Chat, Consultations & Cart Recovery</p>
              </div>
            </div>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                if (activeTab === 'ai-chat') {
                  fetchChatSummary();
                  fetchChatSessions(chatPage);
                } else if (activeTab === 'consultations') {
                  fetchConsultationSummary();
                  fetchConsultations(consultationPage, consultationFilter);
                } else {
                  fetchCartSummary();
                  fetchAbandonedCarts(cartPage);
                }
              }}
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 lg:w-auto lg:inline-grid">
            <TabsTrigger value="ai-chat" className="flex items-center gap-2" data-testid="tab-ai-chat">
              <MessageSquare className="w-4 h-4" />
              <span className="hidden sm:inline">AI Chat</span>
            </TabsTrigger>
            <TabsTrigger value="consultations" className="flex items-center gap-2" data-testid="tab-consultations">
              <Users className="w-4 h-4" />
              <span className="hidden sm:inline">Consultations</span>
            </TabsTrigger>
            <TabsTrigger value="abandoned-carts" className="flex items-center gap-2" data-testid="tab-abandoned-carts">
              <ShoppingCart className="w-4 h-4" />
              <span className="hidden sm:inline">Abandoned Carts</span>
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="ai-chat" data-testid="content-ai-chat">
            {renderAIChatTab()}
          </TabsContent>
          
          <TabsContent value="consultations" data-testid="content-consultations">
            {renderConsultationsTab()}
          </TabsContent>
          
          <TabsContent value="abandoned-carts" data-testid="content-abandoned-carts">
            {renderAbandonedCartsTab()}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default WebsiteAnalytics;
