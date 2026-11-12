import toast from 'react-hot-toast';

/**
 * Toast Notification Utilities
 * Simplified wrapper around react-hot-toast
 */

export const showToast = {
  success: (message, options = {}) => {
    toast.success(message, options);
  },

  error: (message, options = {}) => {
    toast.error(message, options);
  },

  loading: (message, options = {}) => {
    return toast.loading(message, options);
  },

  promise: (promise, messages) => {
    return toast.promise(promise, messages);
  },

  custom: (message, options = {}) => {
    toast(message, options);
  },

  dismiss: (toastId) => {
    if (toastId) {
      toast.dismiss(toastId);
    } else {
      toast.dismiss();
    }
  }
};

// Predefined success messages
export const successMessages = {
  created: (item) => `${item} created successfully!`,
  updated: (item) => `${item} updated successfully!`,
  deleted: (item) => `${item} deleted successfully!`,
  exported: (item) => `${item} exported successfully!`,
  saved: () => 'Changes saved successfully!',
  purchaseOrder: {
    create: (poNumber) => `Purchase Order ${poNumber} created successfully!`,
    update: (poNumber) => `Purchase Order ${poNumber} updated successfully!`,
    delete: (poNumber) => `Purchase Order ${poNumber} deleted successfully!`,
    approve: (poNumber) => `Purchase Order ${poNumber} approved successfully!`,
  },
};

// Predefined error messages
export const errorMessages = {
  failed: (action) => `Failed to ${action}. Please try again.`,
  network: () => 'Network error. Please check your connection.',
  notFound: (item) => `${item} not found.`,
  unauthorized: () => 'You are not authorized to perform this action.',
  validation: (field) => `Please check the ${field} field.`,
  purchaseOrder: {
    create: 'Failed to create purchase order. Please try again.',
    update: 'Failed to update purchase order. Please try again.',
    delete: 'Failed to delete purchase order. Please try again.',
    approve: 'Failed to approve purchase order. Please try again.',
  },
};

export default showToast;