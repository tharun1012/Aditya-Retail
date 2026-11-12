import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { HelpCircle, ChevronDown, ChevronUp } from 'lucide-react';
import SEOHead from './SEOHead';
import Breadcrumbs, { generateBreadcrumbs } from './Breadcrumbs';
import { generateFAQSchema } from './SEOSchemas';

const FAQPage = () => {
  const navigate = useNavigate();
  const [openIndex, setOpenIndex] = useState(null);

  const faqs = [
    {
      category: "Orders & Payment",
      questions: [
        {
          q: "What payment methods do you accept?",
          a: "We accept PhonePe, UPI, and Cash on Delivery (COD). All online payments are processed securely through certified payment gateways."
        },
        {
          q: "How do I track my order?",
          a: "You can track your order by visiting our Order Tracking page and entering your order number and email address. You'll also receive tracking updates via email and SMS."
        },
        {
          q: "Can I cancel my order?",
          a: "Yes, you can cancel your order before it's shipped. Once shipped, you'll need to refuse delivery or initiate a return after receiving the product."
        },
        {
          q: "What is your refund policy?",
          a: "Refunds are processed within 7-10 business days after we receive and inspect the returned product. The amount will be credited to your original payment method."
        }
      ]
    },
    {
      category: "Shipping & Delivery",
      questions: [
        {
          q: "How long does delivery take?",
          a: "Standard delivery takes 3-7 business days depending on your location. Express delivery (1-2 days) is available for select pincodes at additional cost."
        },
        {
          q: "Do you deliver nationwide?",
          a: "Yes, we deliver to most pincodes across India. Please check serviceability by entering your pincode on the product page."
        },
        {
          q: "What if I'm not home during delivery?",
          a: "Our delivery partner will attempt delivery 2-3 times. If unsuccessful, the product will be returned, and you can reschedule delivery or request a refund."
        },
        {
          q: "Is installation included?",
          a: "Basic installation guidance is provided. Professional installation services are available at additional cost for select products."
        }
      ]
    },
    {
      category: "Products & Warranty",
      questions: [
        {
          q: "Are your products genuine?",
          a: "Yes, we are authorized dealers of Bosch and Siemens. All products come with original manufacturer warranty and genuine parts."
        },
        {
          q: "What warranty is provided?",
          a: "All products come with manufacturer's warranty (typically 1-5 years depending on the product). Extended warranty options may be available."
        },
        {
          q: "How do I claim warranty?",
          a: "Contact our Service AI agent or call our support number. We'll create a service request and arrange technician visit if needed."
        },
        {
          q: "Can I return a product if I don't like it?",
          a: "Yes, we have a 7-day return policy. The product must be unused, in original packaging, with all accessories and tags intact."
        }
      ]
    },
    {
      category: "AI Assistance",
      questions: [
        {
          q: "What is AI Sales Agent?",
          a: "Our AI Sales Agent is a smart chatbot powered by advanced AI that helps you find the perfect products, compare options, and get personalized recommendations 24/7."
        },
        {
          q: "Can AI help with technical issues?",
          a: "Yes! Our AI Service Agent can help troubleshoot common issues, provide step-by-step fixes, and create service requests for professional assistance."
        },
        {
          q: "Is AI chat free to use?",
          a: "Absolutely! All our AI agents are free to use and available 24/7 to assist you with sales, service, and delivery queries."
        }
      ]
    }
  ];

  const toggleFAQ = (categoryIndex, questionIndex) => {
    const index = `${categoryIndex}-${questionIndex}`;
    setOpenIndex(openIndex === index ? null : index);
  };

  // Flatten all FAQ items for schema
  const faqSchemaItems = useMemo(() => {
    const items = [];
    faqs.forEach(cat => {
      cat.questions.forEach(q => {
        items.push({ question: q.q, answer: q.a });
      });
    });
    return items;
  }, []);

  const faqSchema = useMemo(() => generateFAQSchema(faqSchemaItems), [faqSchemaItems]);

  return (
    <div className="min-h-screen bg-gray-50">
      <SEOHead 
        title="Frequently Asked Questions | Aditya Retail"
        description="Find answers to common questions about orders, payment, shipping, delivery, products, warranty, and AI assistance at Aditya Retail."
        keywords="Aditya Retail FAQ, help, support, orders, shipping, warranty, returns"
        canonical="/faq"
        schemas={faqSchema ? [faqSchema] : []}
      />

      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <button onClick={() => navigate('/')} className="text-blue-600 hover:text-blue-700 font-medium">
            &larr; Back to Store
          </button>
        </div>
      </div>

      {/* Breadcrumbs */}
      <Breadcrumbs items={generateBreadcrumbs.faq()} />

      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-16">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <HelpCircle className="w-16 h-16 mx-auto mb-4" />
          <h1 className="text-4xl font-bold mb-4">Frequently Asked Questions</h1>
          <p className="text-blue-100">Find answers to common questions about our products and services</p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-16">
        {faqs.map((category, catIndex) => (
          <div key={catIndex} className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">{category.category}</h2>
            <div className="space-y-3">
              {category.questions.map((faq, qIndex) => {
                const index = `${catIndex}-${qIndex}`;
                const isOpen = openIndex === index;

                return (
                  <div key={qIndex} className="bg-white rounded-lg shadow-md overflow-hidden">
                    <button
                      onClick={() => toggleFAQ(catIndex, qIndex)}
                      className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
                    >
                      <span className="font-semibold text-gray-900 pr-4">{faq.q}</span>
                      {isOpen ? (
                        <ChevronUp className="w-5 h-5 text-gray-500 flex-shrink-0" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-gray-500 flex-shrink-0" />
                      )}
                    </button>
                    {isOpen && (
                      <div className="px-6 pb-4 text-gray-700 border-t border-gray-100">
                        <p className="pt-3">{faq.a}</p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}

        {/* Still Have Questions */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-lg p-8 text-white text-center mt-12">
          <h2 className="text-2xl font-bold mb-4">Still Have Questions?</h2>
          <p className="text-blue-100 mb-6">Our customer support team is here to help</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate('/contact')}
              className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
            >
              Contact Support
            </button>
            <button className="bg-transparent border-2 border-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors">
              Chat with AI
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FAQPage;