import React from 'react';
import { Toaster } from 'react-hot-toast';

/**
 * Toast Notification Provider
 * Wrap your app with this component to enable toast notifications
 */

const ToastProvider = ({ children }) => {
  return (
    <>
      {children}
      <Toaster
        position="top-right"
        reverseOrder={false}
        gutter={8}
        toastOptions={{
          // Default options
          duration: 4000,
          style: {
            background: '#fff',
            color: '#363636',
            padding: '16px',
            borderRadius: '8px',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
          },
          // Success
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#10B981',
              secondary: '#fff',
            },
            style: {
              background: '#ECFDF5',
              color: '#065F46',
              border: '1px solid #10B981',
            },
          },
          // Error
          error: {
            duration: 5000,
            iconTheme: {
              primary: '#EF4444',
              secondary: '#fff',
            },
            style: {
              background: '#FEF2F2',
              color: '#991B1B',
              border: '1px solid #EF4444',
            },
          },
          // Loading
          loading: {
            style: {
              background: '#EFF6FF',
              color: '#1E40AF',
              border: '1px solid #3B82F6',
            },
          },
        }}
      />
    </>
  );
};

export default ToastProvider;