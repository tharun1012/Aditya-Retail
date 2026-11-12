import React, { useState, useEffect } from 'react';
import { BACKEND_URL } from '../config/api';
import { 
  Wrench, Clock, CheckCircle, AlertCircle, Mail, Phone, 
  Calendar, Package, FileText, ChevronDown, ChevronUp 
} from 'lucide-react';


const MyServiceTickets = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedTicket, setExpandedTicket] = useState(null);
  const [userEmail, setUserEmail] = useState('');

  useEffect(() => {
    // Get user email from localStorage (assuming user is logged in)
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    if (user.email) {
      setUserEmail(user.email);
      fetchMyTickets(user.email);
    } else {
      // If not logged in, show empty state
      setLoading(false);
    }
  }, []);

  const fetchMyTickets = async (email) => {
    try {
      setLoading(true);
      const response = await fetch(
        `${BACKEND_URL}/api/service-tickets/?customer_email=${encodeURIComponent(email)}`
      );
      const data = await response.json();
      
      if (data.status === 'success') {
        setTickets(data.tickets || []);
      }
    } catch (error) {
      console.error('Error fetching tickets:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusInfo = (status) => {
    const statusMap = {
      'open': {
        label: 'Open',
        color: 'bg-blue-100 text-blue-800 border-blue-300',
        icon: <AlertCircle className="w-5 h-5" />,
        description: 'Your ticket has been created and logged'
      },
      'awaiting_brand_response': {
        label: 'Pending',
        color: 'bg-yellow-100 text-yellow-800 border-yellow-300',
        icon: <Clock className="w-5 h-5" />,
        description: 'Forwarded to brand service team'
      },
      'brand_ticket_created': {
        label: 'Assigned',
        color: 'bg-purple-100 text-purple-800 border-purple-300',
        icon: <FileText className="w-5 h-5" />,
        description: 'Brand has created complaint number'
      },
      'in_progress': {
        label: 'In Progress',
        color: 'bg-orange-100 text-orange-800 border-orange-300',
        icon: <Wrench className="w-5 h-5" />,
        description: 'Technician working on your issue'
      },
      'resolved': {
        label: 'Resolved',
        color: 'bg-green-100 text-green-800 border-green-300',
        icon: <CheckCircle className="w-5 h-5" />,
        description: 'Issue has been resolved'
      },
      'closed': {
        label: 'Closed',
        color: 'bg-gray-100 text-gray-800 border-gray-300',
        icon: <CheckCircle className="w-5 h-5" />,
        description: 'Ticket closed successfully'
      }
    };
    return statusMap[status] || statusMap['open'];
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', { 
      day: '2-digit', 
      month: 'short', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading your service tickets...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!userEmail) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Please Log In</h2>
            <p className="text-gray-600 mb-6">You need to be logged in to view your service tickets.</p>
            <a
              href="/login"
              className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Go to Login
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">My Service Tickets</h1>
          <p className="text-gray-600">Track your product service requests and support tickets</p>
        </div>

        {/* Tickets List */}
        {tickets.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <Wrench className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-900 mb-2">No Service Tickets Yet</h2>
            <p className="text-gray-600 mb-6">
              You haven't created any service requests. Need help with a product?
            </p>
            <button
              onClick={() => window.location.href = '/'}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Get Support
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {tickets.map((ticket) => {
              const statusInfo = getStatusInfo(ticket.status);
              const isExpanded = expandedTicket === ticket.ticket_id;

              return (
                <div key={ticket.ticket_id} className="bg-white rounded-lg shadow-md overflow-hidden">
                  {/* Ticket Header */}
                  <div 
                    className="p-6 cursor-pointer hover:bg-gray-50"
                    onClick={() => setExpandedTicket(isExpanded ? null : ticket.ticket_id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className={`px-3 py-1 rounded-full text-sm font-medium border ${statusInfo.color} flex items-center gap-2`}>
                            {statusInfo.icon}
                            {statusInfo.label}
                          </span>
                          <span className="text-sm text-gray-500">
                            Ticket #{ticket.ticket_id}
                          </span>
                        </div>
                        
                        <h3 className="text-lg font-bold text-gray-900 mb-1">
                          {ticket.product_details?.product_name || 'Service Request'}
                        </h3>
                        
                        <p className="text-sm text-gray-600 mb-3">
                          {ticket.product_details?.brand} - {ticket.product_details?.model_number || 'N/A'}
                        </p>
                        
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          <span className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            {formatDate(ticket.created_at)}
                          </span>
                          {ticket.brand_complaint_number && (
                            <span className="flex items-center gap-1 text-green-600 font-medium">
                              <FileText className="w-4 h-4" />
                              Brand Ticket: {ticket.brand_complaint_number}
                            </span>
                          )}
                        </div>
                      </div>

                      <button className="ml-4">
                        {isExpanded ? (
                          <ChevronUp className="w-6 h-6 text-gray-400" />
                        ) : (
                          <ChevronDown className="w-6 h-6 text-gray-400" />
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {isExpanded && (
                    <div className="border-t border-gray-200 p-6 bg-gray-50">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Issue Details */}
                        <div>
                          <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                            <AlertCircle className="w-5 h-5 text-blue-600" />
                            Issue Description
                          </h4>
                          <p className="text-gray-700 bg-white p-4 rounded-lg">
                            {ticket.issue_description}
                          </p>

                          {ticket.troubleshooting_attempted && (
                            <div className="mt-4">
                              <h5 className="font-medium text-gray-700 mb-2">Troubleshooting Attempted:</h5>
                              <p className="text-sm text-gray-600 bg-white p-3 rounded">
                                {ticket.troubleshooting_attempted}
                              </p>
                            </div>
                          )}
                        </div>

                        {/* Status & Timeline */}
                        <div>
                          <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                            <Clock className="w-5 h-5 text-blue-600" />
                            Status Timeline
                          </h4>
                          
                          <div className="space-y-3">
                            <div className="bg-white p-4 rounded-lg">
                              <div className="flex items-center gap-2 mb-2">
                                {statusInfo.icon}
                                <span className="font-medium text-gray-900">{statusInfo.label}</span>
                              </div>
                              <p className="text-sm text-gray-600">{statusInfo.description}</p>
                            </div>

                            {ticket.brand_complaint_number && (
                              <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                                <p className="text-sm font-medium text-green-900 mb-1">
                                  Brand Complaint Number
                                </p>
                                <p className="text-lg font-bold text-green-700">
                                  {ticket.brand_complaint_number}
                                </p>
                                {ticket.brand_response_date && (
                                  <p className="text-xs text-green-600 mt-1">
                                    Received: {formatDate(ticket.brand_response_date)}
                                  </p>
                                )}
                              </div>
                            )}

                            {ticket.technician_assigned && (
                              <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                                <p className="text-sm font-medium text-blue-900">
                                  Technician Assigned
                                </p>
                                <p className="text-blue-700">{ticket.technician_assigned}</p>
                              </div>
                            )}

                            {ticket.resolution_notes && (
                              <div className="bg-purple-50 border border-purple-200 p-4 rounded-lg">
                                <p className="text-sm font-medium text-purple-900 mb-1">
                                  Resolution Notes
                                </p>
                                <p className="text-sm text-purple-700">{ticket.resolution_notes}</p>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Follow-ups */}
                      {ticket.follow_ups && ticket.follow_ups.length > 0 && (
                        <div className="mt-6 pt-6 border-t border-gray-200">
                          <h4 className="font-semibold text-gray-900 mb-3">Follow-up History</h4>
                          <div className="space-y-2">
                            {ticket.follow_ups.map((followup, idx) => (
                              <div key={idx} className="bg-white p-3 rounded border border-gray-200">
                                <div className="flex items-center justify-between">
                                  <span className="text-sm font-medium text-gray-700">
                                    {followup.type || 'Update'}
                                  </span>
                                  <span className="text-xs text-gray-500">
                                    {formatDate(followup.timestamp)}
                                  </span>
                                </div>
                                <p className="text-sm text-gray-600 mt-1">{followup.note}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Contact Support */}
                      <div className="mt-6 pt-6 border-t border-gray-200">
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                          <p className="text-sm text-blue-900 mb-2 font-medium">Need help with this ticket?</p>
                          <div className="flex flex-wrap gap-4 text-sm">
                            <a 
                              href={`mailto:service.adityaretail@gmail.com?subject=Ticket ${ticket.ticket_id}`}
                              className="flex items-center gap-2 text-blue-700 hover:text-blue-900"
                            >
                              <Mail className="w-4 h-4" />
                              Email Support
                            </a>
                            <a 
                              href="tel:+919844577440"
                              className="flex items-center gap-2 text-blue-700 hover:text-blue-900"
                            >
                              <Phone className="w-4 h-4" />
                              Call Support
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default MyServiceTickets;
