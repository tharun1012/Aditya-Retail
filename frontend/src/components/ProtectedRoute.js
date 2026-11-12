import React, { useEffect, useState } from 'react';
import { BACKEND_URL } from '../config/api';
import { Navigate } from 'react-router-dom';

// All roles that should have access to admin dashboard
const ADMIN_LEVEL_ROLES = [
  'super_admin',
  'admin', 
  'manager',
  'accountant',
  'marketing_head',
  'service_head',
  'hr_manager',
  'operations_manager'
];

// Returns true if the user has at least one granular permission configured.
// Granular perms are either:
//   - Dict[str, List[str]]: { orders: ['view',...], ... } (new shape)
//   - List[str]: ['orders', 'customers', ...] (legacy shape)
// Any admin created via Admin User Management has these, so we should let
// them into the admin dashboard regardless of whether their role is in
// the legacy ADMIN_LEVEL_ROLES whitelist.
const hasAnyAdminPermission = (userData) => {
  const p = userData?.permissions;
  if (!p) return false;
  if (Array.isArray(p)) return p.length > 0;
  if (typeof p === 'object') {
    return Object.values(p).some(v => Array.isArray(v) && v.length > 0);
  }
  return false;
};

const ProtectedRoute = ({ children, requiredRole = null, requiredPermission = null }) => {
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = () => {
    try {
      // Check for admin token in localStorage (check both key formats for backward compatibility)
      const token = localStorage.getItem('adminToken') || localStorage.getItem('admin_token');
      const userStr = localStorage.getItem('adminUser') || localStorage.getItem('admin_user');

      if (!token || !userStr) {
        setIsAuthenticated(false);
        setLoading(false);
        return;
      }

      // Parse user data
      const userData = JSON.parse(userStr);
      const userRole = userData.role;
      
      // super_admin has access to everything
      if (userRole === 'super_admin') {
        setUser(userData);
        setIsAuthenticated(true);
        setLoading(false);
        return;
      }
      
      // Check if user has an admin-level role (can access admin dashboard)
      // Accept either a legacy admin role OR any granular permissions
      // (any user created via Admin User Management has permissions configured).
      const isAdminLevel = ADMIN_LEVEL_ROLES.includes(userRole) || hasAnyAdminPermission(userData);
      if (!isAdminLevel) {
        console.log('Access denied: role', userRole, 'not in admin-level roles and no granular permissions set');
        setIsAuthenticated(false);
        setLoading(false);
        return;
      }
      
      // If specific roles are required, check them
      if (requiredRole) {
        if (Array.isArray(requiredRole)) {
          // If requiredRole is an array, check if user's role is in it OR if user has admin-level access
          if (!requiredRole.includes(userRole) && !ADMIN_LEVEL_ROLES.includes(userRole) && !hasAnyAdminPermission(userData)) {
            setIsAuthenticated(false);
            setLoading(false);
            return;
          }
        } else {
          // If requiredRole is a string, check exact match or admin-level access
          if (userRole !== requiredRole && !ADMIN_LEVEL_ROLES.includes(userRole) && !hasAnyAdminPermission(userData)) {
            setIsAuthenticated(false);
            setLoading(false);
            return;
          }
        }
      }

      // Optional: enforce a specific module-permission (e.g. 'products', 'orders').
      // super_admin bypasses; legacy whitelisted roles also bypass for backward compat.
      if (requiredPermission && userRole !== 'super_admin' && !ADMIN_LEVEL_ROLES.includes(userRole)) {
        const p = userData?.permissions;
        let hasPerm = false;
        if (Array.isArray(p)) {
          hasPerm = p.includes(requiredPermission) || p.includes('all');
        } else if (p && typeof p === 'object') {
          hasPerm = Array.isArray(p[requiredPermission]) && p[requiredPermission].includes('view');
        }
        if (!hasPerm) {
          setIsAuthenticated(false);
          setLoading(false);
          return;
        }
      }

      setUser(userData);
      setIsAuthenticated(true);
      setLoading(false);
    } catch (error) {
      console.error('Auth check error:', error);
      setIsAuthenticated(false);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Verifying access...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/admin/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
