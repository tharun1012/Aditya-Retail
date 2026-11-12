import React from 'react';
import { Package, FileText, ShoppingBag, TrendingDown, CreditCard, Inbox, Search, AlertCircle } from 'lucide-react';

/**
 * Empty State Component
 * Displays friendly messages when no data is available
 */

const EmptyState = ({ 
  type = 'default',
  title,
  description,
  icon: CustomIcon,
  actionLabel,
  onAction,
  searchTerm
}) => {
  // Default icons and messages by type
  const defaultConfigs = {
    'products': {
      icon: Package,
      title: 'No Products Found',
      description: 'Start by adding your first product to the inventory'
    },
    'invoices': {
      icon: FileText,
      title: 'No Invoices Yet',
      description: 'Create your first invoice to get started with billing'
    },
    'purchases': {
      icon: ShoppingBag,
      title: 'No Purchase Orders',
      description: 'Add a purchase order to track your inventory purchases'
    },
    'expenses': {
      icon: TrendingDown,
      title: 'No Expenses Recorded',
      description: 'Start tracking your business expenses for better financial management'
    },
    'vouchers': {
      icon: CreditCard,
      title: 'No Vouchers Found',
      description: 'Create payment or receipt vouchers to manage transactions'
    },
    'search': {
      icon: Search,
      title: 'No Results Found',
      description: searchTerm ? `No items match "${searchTerm}"` : 'Try adjusting your search or filters'
    },
    'error': {
      icon: AlertCircle,
      title: 'Something Went Wrong',
      description: 'Unable to load data. Please try again later.'
    },
    'default': {
      icon: Inbox,
      title: 'No Data Available',
      description: 'There is nothing to display at the moment'
    }
  };

  const config = defaultConfigs[type] || defaultConfigs.default;
  const Icon = CustomIcon || config.icon;
  const displayTitle = title || config.title;
  const displayDescription = description || config.description;

  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
      {/* Icon */}
      <div className="mb-4 p-4 bg-gray-100 rounded-full">
        <Icon className="w-16 h-16 text-gray-400" />
      </div>

      {/* Title */}
      <h3 className="text-xl font-bold text-gray-900 mb-2">
        {displayTitle}
      </h3>

      {/* Description */}
      <p className="text-gray-600 max-w-md mb-6">
        {displayDescription}
      </p>

      {/* Action Button */}
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold shadow-lg"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
};

export default EmptyState;