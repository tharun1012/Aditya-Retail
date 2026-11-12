import React from 'react';
import { isFestive, decorFor } from '../utils/festive';

// Light garland hanging under the header; renders nothing on non-festival days
const FestiveDecor = ({ theme }) => {
  if (!isFestive(theme)) return null;
  const items = decorFor(theme);
  if (!items.length) return null;
  const row = Array.from({ length: 24 }, (_, i) => items[i % items.length]);
  return (
    <div
      aria-hidden="true"
      className="absolute left-0 right-0 top-full h-6 overflow-hidden pointer-events-none select-none flex justify-between px-2 text-base leading-none opacity-90"
    >
      {row.map((e, i) => (
        <span key={i} style={{ marginTop: i % 2 ? 3 : 0 }}>{e}</span>
      ))}
    </div>
  );
};

export default FestiveDecor;
