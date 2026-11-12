import React, { useEffect, useState } from 'react';

// "Ends in 6d 4h" - renders nothing when the theme has no end time
const FestiveCountdown = ({ endsAt }) => {
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 60000);
    return () => clearInterval(t);
  }, []);
  const end = endsAt ? Date.parse(endsAt) : NaN;
  if (isNaN(end) || end <= now) return null;
  const mins = Math.floor((end - now) / 60000);
  const d = Math.floor(mins / 1440), h = Math.floor((mins % 1440) / 60), m = mins % 60;
  return (
    <span className="hidden sm:inline whitespace-nowrap font-semibold text-gray-700">
      ⏳ Ends in {d > 0 ? `${d}d ${h}h` : `${h}h ${m}m`}
    </span>
  );
};

export default FestiveCountdown;
