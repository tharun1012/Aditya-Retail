import React from 'react';
import { Link } from 'react-router-dom';

// Renders plain text that may contain markdown-style links: [anchor text](url)
// Internal paths (starting with / or ?) use client-side <Link> navigation.
// External http(s) links open in a new tab.
const RichText = ({ text, className = '' }) => {
  if (!text) return null;

  const linkPattern = /\[([^\]]+)\]\(([^)]+)\)/g;
  const parts = [];
  let lastIndex = 0;
  let match;
  let key = 0;

  while ((match = linkPattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }
    const [, label, url] = match;
    if (/^https?:\/\//i.test(url)) {
      parts.push(
        
        <a
          key={key++}
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-amber-700 underline hover:text-amber-800"
        >
          {label}
        </a>
      );
    } else {
      parts.push(
        <Link
          key={key++}
          to={url}
          className="text-amber-700 underline hover:text-amber-800"
        >
          {label}
        </Link>
      );
    }
    lastIndex = linkPattern.lastIndex;
  }
  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return <span className={className}>{parts}</span>;
};

export default RichText;
