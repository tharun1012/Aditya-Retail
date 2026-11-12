import React from 'react';
import {
  Store,
  BadgePercent,
  Wrench,
  ShieldCheck,
  Lock,
  Truck,
} from 'lucide-react';

const ITEMS = [
  { icon: Store, label: 'Authorised Brand', sublabel: 'Store Partner' },
  { icon: BadgePercent, label: 'Best Cashback', sublabel: 'Offers' },
  { icon: Wrench, label: 'Best After', sublabel: 'Sales Service' },
  { icon: ShieldCheck, label: 'Assured', sublabel: 'Quality' },
  { icon: Lock, label: 'Secure', sublabel: 'Payment' },
  { icon: Truck, label: 'Timely', sublabel: 'Delivery' },
];

/**
 * Amazon-style feature strip showing Aditya Retail advantages.
 * Props:
 *   variant: 'default' | 'compact' | 'inline'
 *   title:   custom heading (optional)
 */
const WhyBuyStrip = ({ variant = 'default', title }) => {
  const showTitle = variant !== 'inline';
  const isCompact = variant === 'compact';

  return (
    <div
      data-testid="why-buy-strip"
      className={`w-full ${isCompact ? 'py-2' : 'py-2 md:py-4'} bg-gradient-to-br from-amber-50 via-white to-orange-50 border border-amber-100 rounded-xl`}
    >
      {showTitle && (
        <div className="px-4 mb-3">
          <h3 className="text-sm md:text-base font-semibold text-gray-800">
            {title || 'Why buy from Aditya Retail?'}
          </h3>
        </div>
      )}
      <div
        className={`grid grid-cols-3 md:grid-cols-6 ${isCompact ? 'gap-2 px-2' : 'gap-2 md:gap-4 px-2 md:px-4'}`}
      >
        {ITEMS.map(({ icon: Icon, label, sublabel }) => (
          <div
            key={label}
            data-testid={`why-buy-item-${label.toLowerCase().replace(/\s+/g, '-')}`}
            className="flex flex-col items-center text-center"
          >
            <div
              className={`${isCompact ? 'w-9 h-9' : 'w-9 h-9 md:w-12 md:h-12'} rounded-full bg-white border border-amber-200 flex items-center justify-center shadow-sm mb-1`}
            >
              <Icon className={`${isCompact ? 'w-4 h-4' : 'w-4 h-4 md:w-6 md:h-6'} text-amber-600`} strokeWidth={1.75} />
            </div>
            <div className={`${isCompact ? 'text-[10px]' : 'text-[10px] md:text-xs'} text-gray-700 leading-tight font-medium`}>
              <div>{label}</div>
              <div className="text-gray-500 font-normal">{sublabel}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WhyBuyStrip;
