import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogIn } from 'lucide-react';
import { BACKEND_URL } from '../config/api';

const AdminLoginPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    console.log('🔐 Admin login attempt:', formData.email);
    console.log('📡 Backend URL:', BACKEND_URL);

    try {
      // Use unified-login endpoint which checks all user collections including company admins
      const response = await fetch(`${BACKEND_URL}/api/auth/unified-login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      console.log('📥 Response status:', response.status);
      const data = await response.json();
      console.log('📦 Response data:', data);

      if (response.ok) {
        // Check if user has admin-level role
        const adminRoles = ['admin', 'super_admin', 'accountant', 'marketing_head', 'service_head', 'hr_manager', 'operations_manager'];
        const userRole = data.user?.role || '';
        const userType = data.user_type || '';
        
        if (adminRoles.includes(userRole) || userType === 'admin' || userType === 'company_admin') {
          // Backend may return token under either key — accept both
          const tokenValue = data.access_token || data.token;
          if (!tokenValue) {
            console.error('❌ No token in login response:', data);
            setError('Login succeeded but no token returned. Please try again.');
            return;
          }
          // Store token and user info (use consistent key names)
          localStorage.setItem('adminToken', tokenValue);
          localStorage.setItem('adminUser', JSON.stringify(data.user));
          
          console.log('✅ Login successful! Navigating to /admin');
          console.log('👤 User:', data.user);
          
          // Redirect to admin dashboard using React Router
          navigate('/admin');
        } else {
          console.error('❌ Access denied - not an admin role:', userRole);
          setError('Access denied. Admin privileges required.');
        }
      } else {
        console.error('❌ Login failed:', data);
        setError(data.detail || 'Invalid email or password');
      }
    } catch (error) {
      console.error('💥 Login error:', error);
      setError('Network error. Please try again. Check console for details.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-purple-700 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8">
        {/* Logo/Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-4">
            <LogIn className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Admin Login</h1>
          <p className="text-gray-600 mt-2">Aditya Retail - Admin Panel</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              placeholder="admin@example.com"
              required
              autoComplete="email"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              placeholder="••••••••"
              required
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700 focus:ring-4 focus:ring-blue-200 transition-all disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? 'Logging in...' : 'Login to Admin Panel'}
          </button>
        </form>

        {/* Other Login Options */}
        <div className="mt-8 pt-6 border-t border-gray-200 space-y-4">
          <div className="text-center">
            <p className="text-sm text-gray-500 mb-3">Other portals</p>
            <div className="flex flex-col gap-2">
              <button
                onClick={() => navigate('/delivery-login')}
                className="text-indigo-600 hover:text-indigo-700 text-sm font-medium flex items-center justify-center gap-2"
              >
                🚚 Delivery Person Login
              </button>
              <button
                onClick={() => navigate('/store/login')}
                className="text-green-600 hover:text-green-700 text-sm font-medium flex items-center justify-center gap-2"
              >
                🏪 Store / Warehouse Login
              </button>
            </div>
          </div>
          <div className="text-center pt-2">
            <button
              onClick={() => navigate('/')}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              ← Back to Store
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminLoginPage;
