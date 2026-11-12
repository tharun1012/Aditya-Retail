import React from 'react';
import { Wrench } from 'lucide-react';
import { isLargeAppliance } from '../utils/largeAppliance';

/**
 * Displays a "Brand Installation Available" badge for large appliances.
 * Silent for non-large-appliance products.
 */
const InstallationBadge = ({ product, compact = false }) => {
  if (!isLargeAppliance(product)) return null;

  return (
    <div
      data-testid="installation-badge"
      className={`flex items-center gap-2 rounded-lg border border-blue-200 bg-blue-50 ${compact ? 'px-3 py-2' : 'px-4 py-3'}`}
    >
      <div className="w-8 h-8 rounded-full bg-white border border-blue-200 flex items-center justify-center flex-shrink-0">
        <Wrench className="w-4 h-4 text-blue-600" strokeWidth={2} />
      </div>
      <div className="flex-1">
        <div className={`font-semibold text-blue-900 ${compact ? 'text-xs' : 'text-sm'}`}>
          Brand Installation Available
        </div>
        <div className={`text-blue-700 ${compact ? 'text-[10px]' : 'text-xs'}`}>
          Free installation by the manufacturer&apos;s certified technician
        </div>
      </div>
    </div>
  );
};

export default InstallationBadge;
