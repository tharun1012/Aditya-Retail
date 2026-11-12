import React from 'react';
import { Download, Trash2, Printer, X } from 'lucide-react';

const BulkActionToolbar = ({ 
  selectedCount, 
  onExportExcel, 
  onDelete, 
  onPrint,
  onClear,
  showPrint = true,
  customActions = []
}) => {
  if (selectedCount === 0) return null;

  return (
    <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-4 rounded-lg flex items-center justify-between animate-fadeIn">
      <div className="flex items-center gap-3">
        <div className="bg-blue-500 text-white px-3 py-1 rounded-full font-semibold text-sm">
          {selectedCount} selected
        </div>
        <span className="text-gray-700 text-sm">Bulk Actions:</span>
      </div>

      <div className="flex items-center gap-2">
        {/* Export to Excel */}
        {onExportExcel && (
          <button
            onClick={onExportExcel}
            className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors text-sm font-semibold"
          >
            <Download className="w-4 h-4" />
            Export to Excel
          </button>
        )}

        {/* Print */}
        {showPrint && onPrint && (
          <button
            onClick={onPrint}
            className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors text-sm font-semibold"
          >
            <Printer className="w-4 h-4" />
            Print Selected
          </button>
        )}

        {/* Custom Actions */}
        {customActions.map((action, index) => (
          <button
            key={index}
            onClick={action.onClick}
            className={`flex items-center gap-2 ${action.className || 'bg-gray-600 text-white'} px-4 py-2 rounded-lg hover:opacity-90 transition-opacity text-sm font-semibold`}
          >
            {action.icon}
            {action.label}
          </button>
        ))}

        {/* Delete */}
        {onDelete && (
          <button
            onClick={onDelete}
            className="flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm font-semibold"
          >
            <Trash2 className="w-4 h-4" />
            Delete Selected
          </button>
        )}

        {/* Clear Selection */}
        <button
          onClick={onClear}
          className="flex items-center gap-2 bg-gray-200 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-300 transition-colors text-sm"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default BulkActionToolbar;
