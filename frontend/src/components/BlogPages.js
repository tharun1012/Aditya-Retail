import React, { useState, useEffect, useContext } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { BACKEND_URL } from '../config/api';
import { CartContext } from './CartContext';
import {
  Calendar, Tag, FolderOpen, Clock, ArrowLeft, Search,
  ChevronRight, Eye, Share2, Facebook, Twitter, Linkedin,
  BookOpen, User
} from 'lucide-react';
import Header from './Header';
import Footer from './Footer';
import Breadcrumbs, { generateBreadcrumbs } from './Breadcrumbs';

// Blog Listing Page
export const BlogListing = () => {
  const navigate = useNavigate();
  const cartContext = useContext(CartContext);
  const cartCount = cartContext?.getCartCount?.() || 0;
  const cartTotal = cartContext?.getCartTotal?.() || 0;
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchPosts();
    fetchCategories();
  }, [page, selectedCategory]);

  const fetchPosts = async () => {
    setLoading(true);
    try {
      let url = `${BACKEND_URL}/api/blog/posts?page=${page}&limit=9`;
      if (selectedCategory) url += `&category=${encodeURIComponent(selectedCategory)}`;
      if (searchQuery) url += `&search=${encodeURIComponent(searchQuery)}`;
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.status === 'success') {
        setPosts(data.posts);
        setTotalPages(data.pages);
      }
    } catch (error) {
      console.error('Error fetching posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/blog/categories`);
      const data = await response.json();
      if (data.status === 'success') {
        setCategories(data.categories);
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    fetchPosts();
  };

  return (
    <>
      <Helmet>
        <title>Blog - Kitchen Appliance Tips & Buying Guides | Aditya Retail</title>
        <meta name="description" content="Discover expert tips, buying guides, and the latest trends in kitchen appliances. Get insights on Bosch, Siemens, and Electrolux products from Aditya Retail." />
        <meta name="keywords" content="kitchen appliances blog, buying guides, product reviews, kitchen tips, Bosch, Siemens" />
        <link rel="canonical" href="https://adityaretail.com/blog" />
      </Helmet>

      <Header cartCount={cartCount} cartTotal={cartTotal} />

      <Breadcrumbs items={generateBreadcrumbs.blog()} />

      <main className="min-h-screen bg-gray-50">
        {/* Hero Section */}
        <section className="bg-gradient-to-r from-amber-700 to-amber-900 text-white py-16">
          <div className="max-w-7xl mx-auto px-4">
            <div className="text-center">
              <h1 className="text-4xl md:text-5xl font-bold mb-4">Aditya Retail Blog</h1>
              <p className="text-xl text-amber-100 max-w-2xl mx-auto">
                Expert tips, buying guides, and the latest trends in premium kitchen appliances
              </p>
              
              {/* Search */}
              <form onSubmit={handleSearch} className="mt-8 max-w-xl mx-auto">
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Search articles..."
                      className="w-full pl-10 pr-4 py-3 rounded-lg text-gray-900"
                    />
                  </div>
                  <button
                    type="submit"
                    className="px-6 py-3 bg-white text-amber-800 font-semibold rounded-lg hover:bg-amber-50 transition-colors"
                  >
                    Search
                  </button>
                </div>
              </form>
            </div>
          </div>
        </section>

        {/* Content */}
        <section className="py-12">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex flex-col lg:flex-row gap-8">
              {/* Main Content */}
              <div className="flex-1">
                {loading ? (
                  <div className="flex justify-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-4 border-amber-600 border-t-transparent"></div>
                  </div>
                ) : posts.length === 0 ? (
                  <div className="text-center py-12 bg-white rounded-xl">
                    <BookOpen className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                    <p className="text-gray-500 text-lg">No articles found</p>
                    <p className="text-gray-400">Check back soon for new content!</p>
                  </div>
                ) : (
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {posts.map((post) => (
                      <article
                        key={post.id}
                        className="bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-lg transition-shadow group"
                      >
                        <Link to={`/blog/${post.slug}`}>
                          {post.featured_image ? (
                            <img
                              src={post.featured_image}
                              alt={post.featured_image_alt || post.title}
                              loading="lazy"
                              className="w-full aspect-video object-cover group-hover:scale-105 transition-transform duration-300"
                            />
                          ) : (
                            <div className="w-full h-48 bg-gradient-to-br from-amber-100 to-amber-200 flex items-center justify-center">
                              <BookOpen className="w-16 h-16 text-amber-400" />
                            </div>
                          )}
                        </Link>
                        
                        <div className="p-5">
                          {post.category && (
                            <span className="inline-block px-3 py-1 bg-amber-100 text-amber-800 text-xs font-medium rounded-full mb-3">
                              {post.category}
                            </span>
                          )}
                          
                          <Link to={`/blog/${post.slug}`}>
                            <h2 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2 group-hover:text-amber-700 transition-colors">
                              {post.title}
                            </h2>
                          </Link>
                          
                          <p className="text-gray-600 text-sm line-clamp-3 mb-4">
                            {post.excerpt}
                          </p>
                          
                          <div className="flex items-center justify-between text-xs text-gray-500">
                            <span className="flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              {new Date(post.published_at || post.created_at).toLocaleDateString()}
                            </span>
                            <span className="flex items-center gap-1">
                              <Eye className="w-3 h-3" />
                              {post.views || 0} views
                            </span>
                          </div>
                        </div>
                      </article>
                    ))}
                  </div>
                )}

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex justify-center gap-2 mt-8">
                    <button
                      onClick={() => setPage(p => Math.max(1, p - 1))}
                      disabled={page === 1}
                      className="px-4 py-2 bg-white border rounded-lg disabled:opacity-50 hover:bg-gray-50"
                    >
                      Previous
                    </button>
                    <span className="px-4 py-2 bg-white border rounded-lg">
                      Page {page} of {totalPages}
                    </span>
                    <button
                      onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                      disabled={page === totalPages}
                      className="px-4 py-2 bg-white border rounded-lg disabled:opacity-50 hover:bg-gray-50"
                    >
                      Next
                    </button>
                  </div>
                )}
              </div>

              {/* Sidebar */}
              <aside className="lg:w-80 space-y-6">
                {/* CTA */}
                <div className="bg-gradient-to-br from-amber-600 to-amber-800 rounded-xl p-6 text-white">
                  <h3 className="font-bold text-lg mb-2">Need Expert Advice?</h3>
                  <p className="text-amber-100 text-sm mb-4">
                    Get personalized recommendations from our AI kitchen consultant.
                  </p>
                  <button
                    onClick={() => navigate('/')}
                    className="w-full py-2 bg-white text-amber-800 font-semibold rounded-lg hover:bg-amber-50 transition-colors"
                  >
                    Free Consultation
                  </button>
                </div>
              </aside>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </>
  );
};

// Individual Blog Post Page
export const BlogPost = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const cartContext = useContext(CartContext);
  const cartCount = cartContext?.getCartCount?.() || 0;
  const cartTotal = cartContext?.getCartTotal?.() || 0;
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPost();
  }, [slug]);

  const fetchPost = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/blog/post/${slug}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setPost(data.post);
      } else {
        setError('Post not found');
      }
    } catch (error) {
      console.error('Error fetching post:', error);
      setError('Failed to load post');
    } finally {
      setLoading(false);
    }
  };

  const shareUrl = `https://adityaretail.com/blog/${slug}`;

  if (loading) {
    return (
      <>
        <Header cartCount={cartCount} cartTotal={cartTotal} />
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-amber-600 border-t-transparent"></div>
        </div>
      </>
    );
  }

  if (error || !post) {
    return (
      <>
        <Header cartCount={cartCount} cartTotal={cartTotal} />
        <div className="min-h-screen flex flex-col items-center justify-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Post Not Found</h1>
          <button
            onClick={() => navigate('/blog')}
            className="px-6 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700"
          >
            Back to Blog
          </button>
        </div>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Helmet>
        <title>{post.meta_title || post.title} | Aditya Retail Blog</title>
        <meta name="description" content={post.meta_description || post.excerpt} />
        {post.meta_keywords?.length > 0 && (
          <meta name="keywords" content={post.meta_keywords.join(', ')} />
        )}
        <link rel="canonical" href={shareUrl} />
        
        {/* Open Graph */}
        <meta property="og:title" content={post.title} />
        <meta property="og:description" content={post.excerpt} />
        <meta property="og:type" content="article" />
        <meta property="og:url" content={shareUrl} />
        {post.featured_image && <meta property="og:image" content={post.featured_image} />}
        
        {/* Twitter */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={post.title} />
        <meta name="twitter:description" content={post.excerpt} />
        
        {/* Article Schema */}
        <script type="application/ld+json">
          {JSON.stringify({
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": post.title,
            "description": post.excerpt,
            "image": post.featured_image,
            "datePublished": post.published_at,
            "dateModified": post.updated_at,
            "author": {
              "@type": "Organization",
              "name": "Aditya Retail"
            },
            "publisher": {
              "@type": "Organization",
              "name": "Aditya Retail",
              "logo": {
                "@type": "ImageObject",
                "url": "https://adityaretail.com/aditya-logo.png"
              }
            },
            "mainEntityOfPage": {
              "@type": "WebPage",
              "@id": shareUrl
            }
          })}
        </script>

        {/* FAQ Schema */}
        {post.faqs?.length > 0 && (
          <script type="application/ld+json">
            {JSON.stringify({
              "@context": "https://schema.org",
              "@type": "FAQPage",
              "mainEntity": post.faqs
                .filter((faq) => faq.question)
                .map((faq) => ({
                  "@type": "Question",
                  "name": faq.question,
                  "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq.answer
                  }
                }))
            })}
          </script>
        )}
      </Helmet>

      <Header cartCount={cartCount} cartTotal={cartTotal} />

      <Breadcrumbs items={generateBreadcrumbs.blogPost(post.title)} />

      <main className="min-h-screen bg-gray-50">
        <article className="max-w-4xl mx-auto px-4 py-8">
          {/* Header */}
          <header className="mb-8">
            {post.category && (
              <Link
                to={`/blog?category=${encodeURIComponent(post.category)}`}
                className="inline-block px-4 py-1 bg-amber-100 text-amber-800 text-sm font-medium rounded-full mb-4 hover:bg-amber-200 transition-colors"
              >
                {post.category}
              </Link>
            )}
            
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              {post.title}
            </h1>
            
            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
              <Link
                to={`/blog/author/${encodeURIComponent(post.author || 'Aditya Retail')}`}
                className="flex items-center gap-1 hover:text-amber-700 transition-colors"
              >
                <User className="w-4 h-4" />
                {post.author || 'Aditya Retail'}
              </Link>
              <span className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                {new Date(post.published_at || post.created_at).toLocaleDateString('en-IN', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </span>
              {post.updated_at && post.updated_at.slice(0, 10) !== (post.published_at || post.created_at || '').slice(0, 10) && (
                <span className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  Updated {new Date(post.updated_at).toLocaleDateString('en-IN', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </span>
              )}
              <span className="flex items-center gap-1">
                <Eye className="w-4 h-4" />
                {post.views || 0} views
              </span>
            </div>
          </header>

          {/* Featured Image */}
          {post.featured_image && (
            <div className="mb-8 rounded-xl overflow-hidden">
              <img
                src={post.featured_image}
                alt={post.featured_image_alt || post.title}
                className="w-full h-auto max-h-[420px] object-cover"
              />
            </div>
          )}

          {/* Content */}
          <div
            className="prose prose-lg max-w-none prose-p:my-3 prose-headings:mt-8 prose-headings:mb-4 prose-ul:my-2 prose-li:my-0 prose-headings:text-gray-900 prose-a:text-amber-600 prose-a:no-underline hover:prose-a:underline
              prose-p:my-4 prose-p:leading-relaxed prose-li:my-0 prose-img:rounded-lg
              [&_table]:border-collapse [&_table]:w-full [&_table]:my-6
              [&_th]:border [&_th]:border-gray-400 [&_th]:bg-gray-100 [&_th]:p-2 [&_th]:text-left
              [&_td]:border [&_td]:border-gray-400 [&_td]:p-2"
            dangerouslySetInnerHTML={{ __html: post.content }}
          />

          {/* Tags */}
          {post.tags?.length > 0 && (
            <div className="mt-8 pt-8 border-t">
              <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Tag className="w-4 h-4" />
                Tags
              </h3>
              <div className="flex flex-wrap gap-2">
                {post.tags.map((tag, i) => (
                  <Link
                    key={i}
                    to={`/blog?tag=${encodeURIComponent(tag)}`}
                    className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full hover:bg-gray-200 transition-colors"
                  >
                    {tag}
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* FAQs */}
          {post.faqs?.length > 0 && (
            <div className="mt-8 pt-8 border-t">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Frequently Asked Questions</h2>
              <div className="space-y-4">
                {post.faqs.map((faq, i) => (
                  faq.question && (
                    <div key={i} className="bg-white rounded-xl p-5 shadow-sm">
                      <h3 className="font-semibold text-gray-900 mb-2">{faq.question}</h3>
                      <p className="text-gray-600 text-sm leading-relaxed">{faq.answer}</p>
                    </div>
                  )
                ))}
              </div>
            </div>
          )}

          {/* Share */}
          <div className="mt-8 pt-8 border-t">
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <Share2 className="w-4 h-4" />
              Share this article
            </h3>
            <div className="flex gap-3">
              <a
                href={`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="p-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors"
              >
                <Facebook className="w-5 h-5" />
              </a>
              <a
                href={`https://twitter.com/intent/tweet?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(post.title)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="p-3 bg-sky-500 text-white rounded-full hover:bg-sky-600 transition-colors"
              >
                <Twitter className="w-5 h-5" />
              </a>
              <a
                href={`https://www.linkedin.com/shareArticle?mini=true&url=${encodeURIComponent(shareUrl)}&title=${encodeURIComponent(post.title)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="p-3 bg-blue-700 text-white rounded-full hover:bg-blue-800 transition-colors"
              >
                <Linkedin className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Related Posts */}
          {post.related_posts?.length > 0 && (
            <div className="mt-12 pt-8 border-t">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Related Articles</h3>
              <div className="grid md:grid-cols-3 gap-6">
                {post.related_posts.map((related) => (
                  <Link
                    key={related.id}
                    to={`/blog/${related.slug}`}
                    className="group"
                  >
                    <div className="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                      {related.featured_image ? (
                        <img
                          src={related.featured_image}
                          alt={related.title}
                          className="w-full aspect-video object-cover group-hover:scale-105 transition-transform duration-300"
                        />
                      ) : (
                        <div className="w-full h-32 bg-gradient-to-br from-amber-100 to-amber-200 flex items-center justify-center">
                          <BookOpen className="w-8 h-8 text-amber-400" />
                        </div>
                      )}
                      <div className="p-4">
                        <h4 className="font-semibold text-gray-900 line-clamp-2 group-hover:text-amber-600 transition-colors">
                          {related.title}
                        </h4>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </article>
      </main>

      <Footer />
    </>
  );
};

export default BlogListing;