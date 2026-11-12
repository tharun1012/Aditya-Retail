import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, ExternalLink, Home } from 'lucide-react';

const AdminPageHeader = ({ 
  title, 
  description, 
  backPath = '/admin',
  showWebsiteLink = true 
}) => {
  const navigate = useNavigate();

  return (
    <div className="mb-6">
      {/* Navigation Bar */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b-2 border-gray-200">
        <button
          onClick={() => navigate(backPath)}
          className="flex items-center px-4 py-2 text-gray-700 bg-white hover:bg-gray-100 rounded-lg transition-all border border-gray-300 hover:border-gray-400 shadow-sm hover:shadow"
        >
          <ArrowLeft className="h-5 w-5 mr-2" />
          <span className="font-medium">Back to Dashboard</span>
        </button>
        
        {showWebsiteLink && (
          <a
            href="/#/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center px-4 py-2 text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-lg transition-all border border-blue-300 hover:border-blue-400 shadow-sm hover:shadow"
          >
            <Home className="h-5 w-5 mr-2" />
            <span className="font-medium">View Website</span>
            <ExternalLink className="h-4 w-4 ml-2" />
          </a>
        )}
      </div>

      {/* Title Section */}
      {title && (
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{title}</h1>
          {description && (
            <p className="text-gray-600">{description}</p>
          )}
        </div>
      )}
    </div>
  );
};

export default AdminPageHeader;
