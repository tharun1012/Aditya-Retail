import React, { useState } from 'react';
import { BACKEND_URL } from '../config/api';
import { Printer, Download, Mail, MessageCircle, X } from 'lucide-react';


const DocumentActions = ({ document, documentType }) => {
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [emailForm, setEmailForm] = useState({
    email: document?.customer?.email || '',
    name: document?.customer?.name || ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Document types that only have an HTML view on the backend (no dedicated PDF
  // generator). For these, "Print"/"Download PDF" open the printable HTML view
  // and trigger the browser print dialog, which lets the user Save as PDF.
  const HTML_ONLY_TYPES = ['purchase-order', 'delivery-challan', 'voucher', 'expense', 'note', 'grn'];

  const openHtmlAndPrint = () => {
    const htmlUrl = `${BACKEND_URL}/api/documents/${documentType}/${document.id}/html`;
    const printWindow = window.open(htmlUrl, '_blank');
    if (printWindow) {
      printWindow.onload = () => {
        setTimeout(() => {
          printWindow.print();
        }, 500);
      };
    }
  };

  const handlePrint = async () => {
    if (HTML_ONLY_TYPES.includes(documentType)) {
      openHtmlAndPrint();
      return;
    }

    // Download PDF and open in print dialog
    const printUrl = `${BACKEND_URL}/api/invoices/${document.id || document.invoice_number}/pdf`;
    
    try {
      const response = await fetch(printUrl);
      if (response.ok) {
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);
        
        // Open PDF in new window and trigger print
        const printWindow = window.open(blobUrl, '_blank');
        if (printWindow) {
          printWindow.onload = () => {
            setTimeout(() => {
              printWindow.print();
            }, 500);
          };
        }
      } else {
        // Fallback: open PDF URL directly
        window.open(printUrl, '_blank');
      }
    } catch (error) {
      console.error('Print error:', error);
      window.open(printUrl, '_blank');
    }
  };

  const handleDownload = async () => {
    if (HTML_ONLY_TYPES.includes(documentType)) {
      // No dedicated PDF generator for this document type yet - open the
      // printable HTML view and let the user Save as PDF via the print dialog.
      openHtmlAndPrint();
      return;
    }

    // Download PDF invoice
    const downloadUrl = `${BACKEND_URL}/api/invoice-pdf/offline/${document.id || document.invoice_number}`;
    
    try {
      const response = await fetch(downloadUrl);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = window.document.createElement('a');
        a.href = url;
        a.download = `Invoice_${document.invoice_number || document.id}.pdf`;
        window.document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        window.document.body.removeChild(a);
      } else {
        // Fallback to HTML view
        window.open(`${BACKEND_URL}/api/documents/${documentType}/${document.id}/html`, '_blank');
      }
    } catch (error) {
      console.error('Download error:', error);
      // Fallback to HTML view
      window.open(`${BACKEND_URL}/api/documents/${documentType}/${document.id}/html`, '_blank');
    }
  };

  const handleEmail = async () => {
    if (!emailForm.email) {
      setMessage({ type: 'error', text: 'Please enter email address' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await fetch(`${BACKEND_URL}/api/documents/email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_id: document.id,
          document_type: documentType,
          recipient_email: emailForm.email,
          recipient_name: emailForm.name
        })
      });

      const data = await response.json();

      if (data.status === 'success') {
        setMessage({ type: 'success', text: `Email sent successfully to ${emailForm.email}` });
        setTimeout(() => {
          setShowEmailModal(false);
          setMessage({ type: '', text: '' });
        }, 2000);
      } else {
        setMessage({ type: 'error', text: 'Failed to send email' });
      }
    } catch (error) {
      console.error('Email error:', error);
      setMessage({ type: 'error', text: 'Failed to send email' });
    } finally {
      setLoading(false);
    }
  };

  const handleWhatsApp = async () => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/documents/whatsapp-share/${document.id}?document_type=${documentType}`
      );
      const data = await response.json();

      if (data.status === 'success' && data.whatsapp_url) {
        // Open WhatsApp in new window
        window.open(data.whatsapp_url, '_blank');
      } else {
        alert('Failed to generate WhatsApp link. Please ensure customer phone number is valid.');
      }
    } catch (error) {
      console.error('WhatsApp error:', error);
      alert('Failed to share via WhatsApp');
    }
  };

  return (
    <div className="flex flex-wrap gap-2">
      {/* Print Button */}
      <button
        onClick={handlePrint}
        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center gap-2 transition-colors"
        title="Print Document"
      >
        <Printer size={18} />
        Print
      </button>

      {/* Download PDF Button */}
      <button
        onClick={handleDownload}
        className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 flex items-center gap-2 transition-colors"
        title="Download as PDF"
      >
        <Download size={18} />
        Download PDF
      </button>

      {/* Email Button */}
      <button
        onClick={() => setShowEmailModal(true)}
        className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 flex items-center gap-2 transition-colors"
        title="Email Document"
      >
        <Mail size={18} />
        Email
      </button>

      {/* WhatsApp Button */}
      <button
        onClick={handleWhatsApp}
        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2 transition-colors"
        title="Share via WhatsApp"
      >
        <MessageCircle size={18} />
        WhatsApp
      </button>

      {/* Email Modal */}
      {showEmailModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-xl font-bold">Email Document</h3>
              <button
                onClick={() => {
                  setShowEmailModal(false);
                  setMessage({ type: '', text: '' });
                }}
                className="text-gray-500 hover:text-gray-700"
              >
                <X size={24} />
              </button>
            </div>
            <div className="p-6">
              {message.text && (
                <div
                  className={`mb-4 p-3 rounded-lg ${
                    message.type === 'success'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {message.text}
                </div>
              )}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Recipient Name
                  </label>
                  <input
                    type="text"
                    value={emailForm.name}
                    onChange={(e) => setEmailForm({ ...emailForm, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    placeholder="Customer name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email Address *
                  </label>
                  <input
                    type="email"
                    value={emailForm.email}
                    onChange={(e) => setEmailForm({ ...emailForm, email: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    placeholder="customer@example.com"
                    required
                  />
                </div>
              </div>
            </div>
            <div className="p-6 border-t border-gray-200 flex justify-end gap-2">
              <button
                onClick={() => {
                  setShowEmailModal(false);
                  setMessage({ type: '', text: '' });
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                onClick={handleEmail}
                disabled={loading}
                className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50 flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Sending...
                  </>
                ) : (
                  <>
                    <Mail size={18} />
                    Send Email
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentActions;
