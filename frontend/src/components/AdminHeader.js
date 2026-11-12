import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Home, ChevronRight, LogOut, User, ArrowLeft } from 'lucide-react';

const AdminHeader = ({ title, icon: Icon, breadcrumb = [] }) => {
  const navigate = useNavigate();
  
  const handleLogout = () => {
    localStorage.removeItem('adminToken');
    localStorage.removeItem('adminUser');
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    navigate('/admin/login');
  };

  const user = JSON.parse(localStorage.getItem('adminUser') || localStorage.getItem('user') || '{}');

  return (
    <div className="bg-white border-b shadow-sm mb-6">
      <div className="max-w-7xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Left side - Back Button, Breadcrumb and Title */}
          <div className="flex items-center gap-4">
            {/* Back button */}
            <button
              onClick={() => navigate('/admin')}
              className="flex items-center px-3 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              title="Back to Dashboard"
              data-testid="back-to-dashboard-btn"
            >
              <ArrowLeft className="w-4 h-4 mr-1" />
              <span className="text-sm font-medium">Back</span>
            </button>

            {/* Home button */}
            <button
              onClick={() => navigate('/')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Go to Main Website"
            >
              <Home className="w-5 h-5 text-gray-600" />
            </button>
            
            {/* Breadcrumb */}
            <div className="flex items-center text-sm text-gray-500">
              <span 
                onClick={() => navigate('/admin')} 
                className="cursor-pointer hover:text-gray-700"
              >
                Admin
              </span>
              {breadcrumb.map((item, index) => (
                <React.Fragment key={index}>
                  <ChevronRight className="w-4 h-4 mx-1" />
                  <span 
                    onClick={() => item.path && navigate(item.path)}
                    className={item.path ? 'cursor-pointer hover:text-gray-700' : 'text-gray-700 font-medium'}
                  >
                    {item.label}
                  </span>
                </React.Fragment>
              ))}
            </div>
          </div>

          {/* Right side - User info and logout */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm">
              <div className="p-2 bg-gray-100 rounded-full">
                <User className="w-4 h-4 text-gray-600" />
              </div>
              <span className="text-gray-700 font-medium hidden sm:block">
                {user.name || user.email || 'Admin'}
              </span>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 hover:bg-red-50 text-gray-500 hover:text-red-600 rounded-lg transition-colors"
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminHeader;
