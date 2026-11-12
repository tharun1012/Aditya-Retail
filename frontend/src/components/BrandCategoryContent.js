import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import RichText from './RichText';

const BrandCategoryContent = ({ content }) => {
  const [expanded, setExpanded] = useState(false);

  if (!content) return null;

  return (
    <div className="max-w-7xl mx-auto px-4 py-12" data-testid="brand-category-content">
      <p className="text-gray-700 leading-relaxed">
        <RichText text={content.intro} />
      </p>

      <div
        className={`overflow-hidden transition-all duration-300 ease-in-out ${
          expanded ? 'max-h-[10000px] opacity-100 mt-8' : 'max-h-0 opacity-0'
        }`}
      >
        <h2 className="text-2xl font-bold text-gray-900 mb-4">{content.whyBuyHeading}</h2>
        <ul className="list-disc list-inside space-y-2 text-gray-700 mb-8">
          {content.whyBuy.map((item, i) => (
            <li key={i}><strong>{item.label}</strong> — <RichText text={item.text} /></li>
          ))}
        </ul>

        <h2 className="text-2xl font-bold text-gray-900 mb-4">{content.typesHeading}</h2>
        <p className="text-gray-700 mb-4"><RichText text={content.typesIntro} /></p>
        {content.types.map((type, i) => (
          <div key={i}>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">{type.h3}</h3>
            <p className="text-gray-700 mb-6"><RichText text={type.text} /></p>
          </div>
        ))}

        <h2 className="text-2xl font-bold text-gray-900 mb-4">{content.howToChooseHeading}</h2>
        <ul className="list-disc list-inside space-y-2 text-gray-700 mb-8">
          {content.howToChoose.map((item, i) => (
            <li key={i}><strong>{item.label}</strong> — <RichText text={item.text} /></li>
          ))}
        </ul>

        <p className="text-gray-700 mb-8"><RichText text={content.closingText} /></p>
      </div>

      <button
        onClick={() => setExpanded(!expanded)}
        className="mt-4 text-blue-600 font-semibold hover:text-blue-800"
      >
        {expanded ? 'Show Less' : 'Read More'}
      </button>

      <h2 className="text-2xl font-bold text-gray-900 mb-4 mt-8">{content.faqHeading}</h2>
      <div className="space-y-3 mb-8">
        {content.faqs.map((faq, i) => (
          <details key={i} className="bg-white rounded-lg shadow-sm group" data-testid={`brand-faq-${i}`}>
            <summary className="px-6 py-4 cursor-pointer font-semibold text-gray-900 hover:bg-gray-50 transition-colors list-none flex items-center justify-between">
              <h3 className="font-semibold text-gray-900 m-0">{faq.question}</h3>
              <ChevronDown className="w-5 h-5 text-gray-500 group-open:rotate-180 transition-transform flex-shrink-0 ml-2" />
            </summary>
            <div className="px-6 pb-4 text-gray-700 border-t border-gray-100">
              <p className="pt-3"><RichText text={faq.answer} /></p>
            </div>
          </details>
        ))}
      </div>
    </div>
  );
};

export default BrandCategoryContent;