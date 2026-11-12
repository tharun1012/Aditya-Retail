import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import LeadManagement from './LeadManagement';

const StoreLeads = () => {
  const navigate = useNavigate();
  const hasToken = !!localStorage.getItem('storeToken');
  useEffect(() => { if (!hasToken) navigate('/login'); }, [hasToken, navigate]);
  return hasToken ? <LeadManagement storeMode /> : null;
};
export default StoreLeads;
