import { useState, useEffect, useCallback } from 'react';
import { BACKEND_URL } from '../config/api';

/**
 * Hook to check if current user can edit a specific document type
 * @param {string} documentType - The type of document (vouchers, invoices, orders, etc.)
 * @returns {object} - { canEdit, loading, error, checkPermission }
 */
export const useEditPermission = (documentType) => {
  const [canEdit, setCanEdit] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reason, setReason] = useState('');

  const checkPermission = useCallback(async () => {
    if (!documentType) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const token = localStorage.getItem('adminToken');
      
      if (!token) {
        setCanEdit(false);
        setReason('Not authenticated');
        setLoading(false);
        return;
      }

      const response = await fetch(`${BACKEND_URL}/api/admin/can-edit/${documentType}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setCanEdit(data.can_edit);
        setReason(data.reason);
      } else {
        setCanEdit(false);
        setReason('Permission check failed');
      }
    } catch (err) {
      setError(err.message);
      setCanEdit(false);
      setReason('Error checking permissions');
    } finally {
      setLoading(false);
    }
  }, [documentType]);

  useEffect(() => {
    checkPermission();
  }, [checkPermission]);

  return { canEdit, loading, error, reason, checkPermission };
};

/**
 * Utility function to check edit permission (for use outside React components)
 * @param {string} documentType - The type of document
 * @returns {Promise<{canEdit: boolean, reason: string}>}
 */
export const checkEditPermission = async (documentType) => {
  try {
    const token = localStorage.getItem('adminToken');
    
    if (!token) {
      return { canEdit: false, reason: 'Not authenticated' };
    }

    const response = await fetch(`${BACKEND_URL}/api/admin/can-edit/${documentType}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (response.ok) {
      const data = await response.json();
      return { canEdit: data.can_edit, reason: data.reason };
    }
    
    return { canEdit: false, reason: 'Permission check failed' };
  } catch (err) {
    return { canEdit: false, reason: err.message };
  }
};

export default useEditPermission;
