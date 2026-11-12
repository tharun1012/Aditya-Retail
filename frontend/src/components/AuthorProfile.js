import React, { useState, useEffect, useContext } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { BACKEND_URL } from '../config/api';
import { CartContext } from './CartContext';
import { Calendar, Eye, BookOpen, User } from 'lucide-react';
import Header from './Header';
import Footer from './Footer';
import Breadcrumbs from './Breadcrumbs';

// Author Profile Page — /blog/author/:authorName
// NOTE: This currently filters client-side because the blog API has no
// dedicated "list posts by author" endpoint yet. If the blog has many
// authors/posts, ask the backend team to add `?author=` support to
// GET /api/blog/posts and swap the fetch below to use it directly.
const AuthorProfile = () => {
  const { authorName } = useParams();
  const cartContext = useContext(CartContext);
  const cartCount = cartContext?.getCartCount?.() || 0;
  const cartTotal = cartContext?.getCartTotal?.() || 0;

  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const decodedAuthor = decodeURIComponent(authorName || '');

  useEffect(() => {
    const fetchAuthorPosts = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${BACKEND_URL}/api/blog/posts?page=1&limit=100`);
        const data = await response.json();
        if (data.status === 'success') {
          const filtered = (data.posts || []).filter(
            (p) => (p.author || 'Aditya Retail').toLowerCase() === decodedAuthor.toLowerCase()
          );
          setPosts(filtered);
        }
      } catch (error) {
        console.error('Error fetching author posts:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchAuthorPosts();
  }, [decodedAuthor]);

  return (
    <>
      <Helmet>
        <title>{decodedAuthor} - Author Profile | Aditya Retail Blog</title>
        <meta name="description" content={`Articles written by ${decodedAuthor} on the Aditya Retail blog.`} />
        <link rel="canonical" href={`https://adityaretail.com/blog/author/${encodeURIComponent(decodedAuthor)}`} />
      </Helmet>

      <Header cartCount={cartCount} cartTotal={cartTotal} />

      <Breadcrumbs
        items={[
          { label: 'Home', href: '/' },
          { label: 'Blog', href: '/blog' },
          { label: decodedAuthor, href: `/blog/author/${encodeURIComponent(decodedAuthor)}` }
        ]}
      />

      <main className="min-h-screen bg-gray-50">
        <section className="bg-gradient-to-r from-amber-700 to-amber-900 text-white py-12">
          <div className="max-w-7xl mx-auto px-4 flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center">
              <User className="w-8 h-8" />
            </div>
            <div>
              <p className="text-amber-100 text-sm">Author</p>
              <h1 className="text-3xl font-bold">{decodedAuthor}</h1>
            </div>
          </div>
        </section>

        <section className="py-12">
          <div className="max-w-7xl mx-auto px-4">
            {loading ? (
              <div className="flex justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-amber-600 border-t-transparent"></div>
              </div>
            ) : posts.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-xl">
                <BookOpen className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                <p className="text-gray-500 text-lg">No articles found for this author yet</p>
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
                          className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                        />
                      ) : (
                        <div className="w-full h-48 bg-gradient-to-br from-amber-100 to-amber-200 flex items-center justify-center">
                          <BookOpen className="w-16 h-16 text-amber-400" />
                        </div>
                      )}
                    </Link>
                    <div className="p-5">
                      <Link to={`/blog/${post.slug}`}>
                        <h2 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2 group-hover:text-amber-700 transition-colors">
                          {post.title}
                        </h2>
                      </Link>
                      <p className="text-gray-600 text-sm line-clamp-3 mb-4">{post.excerpt}</p>
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
          </div>
        </section>
      </main>

      <Footer />
    </>
  );
};

export default AuthorProfile;