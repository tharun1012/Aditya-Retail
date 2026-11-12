import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { BACKEND_URL } from '../config/api';
import {
  FileText, Plus, Edit, Trash2, Eye, Search, Filter,
  ArrowLeft, Save, X, Sparkles, RefreshCw, Calendar,
  Tag, FolderOpen, Globe, Clock, CheckCircle, AlertCircle,
  Wand2, FileEdit, List, Image
} from 'lucide-react';
import TiptapEditor from './TiptapEditor';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import BlogAutopilotPanel from "./BlogAutopilotPanel";

const BlogManagement = () => {
  const navigate = useNavigate();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Editor state
  const [showEditor, setShowEditor] = useState(false);
  const [editingPost, setEditingPost] = useState(null);
  const [saving, setSaving] = useState(false);
  
  // AI Generation state
  const [showAIDialog, setShowAIDialog] = useState(false);
  const [aiTopic, setAiTopic] = useState('');
  const [aiKeywords, setAiKeywords] = useState('');
  const [aiTone, setAiTone] = useState('professional');
  const [aiLength, setAiLength] = useState('medium');
  const [aiOutlineOnly, setAiOutlineOnly] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState(null);
  
  // Form state
  const [formData, setFormData] = useState({
    title: '',
    slug: '',
    content: '',
    excerpt: '',
    featured_image: '',
    featured_image_alt: '',
    category: '',
    tags: [],
    meta_title: '',
    meta_description: '',
    meta_keywords: [],
    status: 'draft',
    author: '',
    published_at: '',
    faqs: []
  });
  const [tagInput, setTagInput] = useState('');

  // Get auth token — try multiple keys for resilience (different login paths set different keys)
  const getAuthToken = () => (
    localStorage.getItem('adminToken') ||
    localStorage.getItem('authToken') ||
    localStorage.getItem('token') ||
    localStorage.getItem('userToken') ||
    ''
  );

  const fetchPosts = useCallback(async () => {
    setLoading(true);
    try {
      let url = `${BACKEND_URL}/api/blog/admin/posts?page=${page}&limit=15`;
      if (statusFilter) url += `&status=${statusFilter}`;
      
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${getAuthToken()}` }
      });
      
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
  }, [page, statusFilter]);

  useEffect(() => {
    fetchPosts();
  }, [fetchPosts]);

  const handleCreateNew = () => {
    setEditingPost(null);
    setFormData({
      title: '',
      slug: '',
      content: '',
      excerpt: '',
      featured_image: '',
      featured_image_alt: '',
      category: '',
      tags: [],
      meta_title: '',
      meta_description: '',
      meta_keywords: [],
      status: 'draft',
      author: '',
      published_at: '',
      faqs: []
    });
    setShowEditor(true);
  };

  const handleEdit = async (postId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/blog/admin/post/${postId}`, {
        headers: { 'Authorization': `Bearer ${getAuthToken()}` }
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        setEditingPost(data.post);
        setFormData({
          title: data.post.title || '',
          slug: data.post.slug || '',
          content: data.post.content || '',
          excerpt: data.post.excerpt || '',
          featured_image: data.post.featured_image || '',
          featured_image_alt: data.post.featured_image_alt || '',
          category: data.post.category || '',
          tags: data.post.tags || [],
          meta_title: data.post.meta_title || '',
          meta_description: data.post.meta_description || '',
          meta_keywords: data.post.meta_keywords || [],
          status: data.post.status || 'draft',
          author: data.post.author || '',
          published_at: data.post.published_at ? data.post.published_at.slice(0, 10) : '',
          faqs: data.post.faqs || []
        });
        setShowEditor(true);
      }
    } catch (error) {
      console.error('Error fetching post:', error);
    }
  };

  const handleSave = async (overrideStatus) => {
    const payload = typeof overrideStatus === 'string' ? { ...formData, status: overrideStatus } : formData;
    if (!formData.title || !formData.content) {
      alert('Title and content are required');
      return;
    }
    
    setSaving(true);
    try {
      const url = editingPost 
        ? `${BACKEND_URL}/api/blog/admin/posts/${editingPost.id}`
        : `${BACKEND_URL}/api/blog/admin/posts`;
      
      const method = editingPost ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        alert(editingPost ? 'Post updated!' : 'Post created!');
        setShowEditor(false);
        fetchPosts();
      } else {
        alert(data.detail || 'Failed to save post');
      }
    } catch (error) {
      console.error('Error saving post:', error);
      alert('Error saving post');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (postId) => {
    if (!window.confirm('Are you sure you want to delete this post?')) return;
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/blog/admin/posts/${postId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${getAuthToken()}` }
      });
      
      const data = await response.json();
      if (data.status === 'success') {
        fetchPosts();
      }
    } catch (error) {
      console.error('Error deleting post:', error);
    }
  };

  const handleBannerUpload = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (!file) return;
    const uploadData = new FormData();
    uploadData.append('file', file);
    try {
      const res = await fetch(`${BACKEND_URL}/api/upload/upload-image`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${getAuthToken()}` },
        body: uploadData
      });
      const data = await res.json();
      if (data.status === 'success' && data.image_url) {
        setFormData(prev => ({ ...prev, featured_image: data.image_url }));
      } else {
        alert('Banner upload failed');
      }
    } catch (err) {
      console.error('Banner upload error:', err);
      alert('Banner upload failed');
    }
  };

  const addFaq = () => {
    setFormData(prev => ({ ...prev, faqs: [...prev.faqs, { question: '', answer: '' }] }));
  };

  const updateFaq = (index, field, value) => {
    setFormData(prev => ({
      ...prev,
      faqs: prev.faqs.map((faq, i) => i === index ? { ...faq, [field]: value } : faq)
    }));
  };

  const removeFaq = (index) => {
    setFormData(prev => ({ ...prev, faqs: prev.faqs.filter((_, i) => i !== index) }));
  };

  const handleAIGenerate = async () => {
    if (!aiTopic.trim()) {
      alert('Please enter a topic');
      return;
    }
    
    setGenerating(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/blog/admin/generate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          topic: aiTopic,
          keywords: aiKeywords.split(',').map(k => k.trim()).filter(k => k),
          tone: aiTone,
          length: aiLength,
          include_product_links: true,
          outline_only: aiOutlineOnly
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setGeneratedContent(data.generated);
        
        // If we have parsed content, populate the form
        if (data.generated.parsed) {
          setFormData(prev => ({
            ...prev,
            title: data.generated.parsed.title || aiTopic,
            content: data.generated.parsed.content || data.generated.raw_content,
            meta_description: data.generated.parsed.meta_description || '',
            category: data.generated.parsed.category || '',
            tags: data.generated.parsed.tags || []
          }));
        }
      } else {
        alert(data.detail || 'AI generation failed');
      }
    } catch (error) {
      console.error('Error generating content:', error);
      alert('AI generation failed');
    } finally {
      setGenerating(false);
    }
  };

  const applyGeneratedContent = () => {
    if (generatedContent?.parsed) {
      setFormData(prev => ({
        ...prev,
        title: generatedContent.parsed.title || prev.title,
        content: generatedContent.parsed.content || generatedContent.raw_content,
        meta_description: generatedContent.parsed.meta_description || prev.meta_description,
        category: generatedContent.parsed.category || prev.category,
        tags: generatedContent.parsed.tags || prev.tags
      }));
    } else if (generatedContent?.raw_content) {
      setFormData(prev => ({
        ...prev,
        content: generatedContent.raw_content
      }));
    }
    setShowAIDialog(false);
    setShowEditor(true);
  };

  const addTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tagInput.trim()]
      }));
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  // Blog Editor Component
  const renderEditor = () => (
    <div className="fixed inset-0 bg-white z-50 overflow-y-auto">
      <div className="max-w-5xl mx-auto px-4 py-6">
        {/* Editor Header */}
        <div className="flex items-center justify-between mb-6 sticky top-0 bg-white py-4 border-b z-10">
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={() => setShowEditor(false)}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <h1 className="text-xl font-bold">
              {editingPost ? 'Edit Post' : 'Create New Post'}
            </h1>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={() => setShowAIDialog(true)}
            >
              <Wand2 className="w-4 h-4 mr-2" />
              AI Assist
            </Button>
            <Button
              variant="outline"
              onClick={() => handleSave('draft')}
              disabled={saving}
            >
              Save Draft
            </Button>
            <Button
              onClick={() => handleSave('published')}
              disabled={saving}
              className="bg-green-600 hover:bg-green-700"
            >
              {saving ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Globe className="w-4 h-4 mr-2" />}
              Publish
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Title *</label>
              <Input
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                placeholder="Enter post title..."
                className="text-lg"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Slug (URL)</label>
              <Input
                value={formData.slug}
                onChange={(e) => setFormData(prev => ({ ...prev, slug: e.target.value }))}
                placeholder="auto-generated-from-title"
              />
              <p className="text-xs text-gray-500 mt-1">Leave blank to auto-generate from title</p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Content *</label>
              <TiptapEditor
                key={editingPost?.id || 'new'}
                value={formData.content}
                onChange={(html) => setFormData(prev => ({ ...prev, content: html }))}
                backendUrl={BACKEND_URL}
                authToken={getAuthToken()}
                placeholder="Write your blog content here..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Excerpt</label>
              <textarea
                value={formData.excerpt}
                onChange={(e) => setFormData(prev => ({ ...prev, excerpt: e.target.value }))}
                placeholder="Brief summary for listing pages (auto-generated if left blank)"
                className="w-full h-24 p-3 border rounded-lg"
                maxLength={300}
              />
              <p className="text-xs text-gray-500 mt-1">{formData.excerpt?.length || 0}/300 characters</p>
            </div>

          <div className="border rounded-xl p-4">

            <h3 className="font-semibold mb-3">FAQs</h3>

            <div className="space-y-3">
              {formData.faqs.map((faq, i) => (
                <div key={i} className="border rounded-lg p-3 space-y-2 grid grid-cols-1 md:grid-cols-2 gap-2">
                  <div className="flex items-center justify-between md:col-span-2">
                    <span className="text-xs font-medium text-gray-500">FAQ {i + 1}</span>
                    <button type="button" onClick={() => removeFaq(i)} className="text-red-500 hover:text-red-700">
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  <Input
                    value={faq.question}
                    onChange={(e) => updateFaq(i, 'question', e.target.value)}
                    placeholder="Question"
                  />
                  <textarea
                    value={faq.answer}
                    onChange={(e) => updateFaq(i, 'answer', e.target.value)}
                    placeholder="Answer"
                    className="w-full p-2 border rounded text-sm"
                    rows={2}
                  />
                </div>
              ))}
              <Button type="button" variant="outline" size="sm" onClick={addFaq} className="w-full">
                <Plus className="w-4 h-4 mr-2" />
                Add FAQ
              </Button>
            </div>
          </div>

          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">Featured Image</CardTitle>
              </CardHeader>
              <CardContent>
                <input
                  id="bannerUploadInput"
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleBannerUpload}
                />
                <Button
                  type="button"
                  variant="outline"
                  className="w-full mb-2"
                  onClick={() => document.getElementById('bannerUploadInput').click()}
                >
                  <Image className="w-4 h-4 mr-2" />
                  Upload Banner Image
                </Button>
                <p className="text-xs text-gray-500 mb-2">Recommended size: 1200 x 630px (16:9), JPG/WebP, under 300KB</p>
                <Input
                  value={formData.featured_image}
                  onChange={(e) => setFormData(prev => ({ ...prev, featured_image: e.target.value }))}
                  placeholder="Or paste Image URL"
                />
                <Input
                  value={formData.featured_image_alt}
                  onChange={(e) => setFormData(prev => ({ ...prev, featured_image_alt: e.target.value }))}
                  placeholder="Alt text (for SEO & accessibility)"
                  className="mt-2"
                />
                {formData.featured_image && (
                  <img 
                    src={formData.featured_image} 
                    alt={formData.featured_image_alt || 'Preview'} 
                    className="mt-2 w-full h-32 object-cover rounded"
                  />
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">Category</CardTitle>
              </CardHeader>
              <CardContent>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                  className="w-full p-2 border rounded"
                >
                  <option value="">Select Category</option>
                  <option value="Buying Guide">Buying Guide</option>
                  <option value="Product Review">Product Review</option>
                  <option value="Tips & Tricks">Tips & Tricks</option>
                  <option value="Kitchen Design">Kitchen Design</option>
                  <option value="Maintenance">Maintenance</option>
                  <option value="News">News</option>
                  <option value="Recipes">Recipes</option>
                </select>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">Tags</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2 mb-2">
                  <Input
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    placeholder="Add tag"
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                  />
                  <Button variant="outline" size="sm" onClick={addTag}>Add</Button>
                </div>
                <div className="flex flex-wrap gap-1">
                  {formData.tags.map((tag, i) => (
                    <Badge key={i} variant="secondary" className="cursor-pointer" onClick={() => removeTag(tag)}>
                      {tag} <X className="w-3 h-3 ml-1" />
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm">Publishing</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Author</label>
                    <Input
                      value={formData.author}
                      onChange={(e) => setFormData(prev => ({ ...prev, author: e.target.value }))}
                      placeholder="Author name"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Published Date</label>
                    <Input
                      type="date"
                      value={formData.published_at}
                      onChange={(e) => setFormData(prev => ({ ...prev, published_at: e.target.value }))}
                    />
                    <p className="text-xs text-gray-400 mt-1">Leave blank to set automatically when published</p>
                  </div>
                  {editingPost?.updated_at && (
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Last Updated</label>
                      <p className="text-sm text-gray-700">{new Date(editingPost.updated_at).toLocaleString()}</p>
                    </div>
                  )}
                </CardContent>
              </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">SEO Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Meta Title</label>
                  <Input
                    value={formData.meta_title}
                    onChange={(e) => setFormData(prev => ({ ...prev, meta_title: e.target.value }))}
                    placeholder="SEO Title (defaults to post title)"
                    maxLength={60}
                  />
                  <p className="text-xs text-gray-400">{formData.meta_title?.length || 0}/60</p>
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Meta Description</label>
                  <textarea
                    value={formData.meta_description}
                    onChange={(e) => setFormData(prev => ({ ...prev, meta_description: e.target.value }))}
                    placeholder="SEO Description"
                    className="w-full p-2 border rounded text-sm"
                    rows={3}
                    maxLength={160}
                  />
                  <p className="text-xs text-gray-400">{formData.meta_description?.length || 0}/160</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">Status</CardTitle>
              </CardHeader>
              <CardContent>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value }))}
                  className="w-full p-2 border rounded"
                >
                  <option value="draft">Draft</option>
                  <option value="published">Published</option>
                </select>
              </CardContent>
            </Card>

            <Button onClick={handleSave} className="w-full" disabled={saving}>
              {saving ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
              {editingPost ? 'Update Post' : 'Save Post'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );

  // Main List View
  return (
    <div className="min-h-screen bg-gray-50">
      {showEditor && renderEditor()}
      
      {/* Header */}
      <div className="bg-white shadow-sm border-b sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={() => navigate('/admin')}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Blog Management</h1>
                <p className="text-sm text-gray-500">Create and manage SEO-optimized blog posts</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" onClick={() => setShowAIDialog(true)}>
                <Wand2 className="w-4 h-4 mr-2" />
                AI Generate
              </Button>
              <Button onClick={handleCreateNew} className="bg-gradient-to-r from-indigo-600 to-purple-600">
                <Plus className="w-4 h-4 mr-2" />
                New Post
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <BlogAutopilotPanel onDraftCreated={fetchPosts} />

        {/* Filters */}
        <div className="flex gap-4 mb-6">
          <div className="flex-1">
            <Input
              placeholder="Search posts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="max-w-sm"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border rounded-lg"
          >
            <option value="">All Status</option>
            <option value="draft">Draft</option>
            <option value="published">Published</option>
          </select>
          <Button variant="outline" onClick={fetchPosts}>
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>

        {/* Posts Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="w-8 h-8 animate-spin text-indigo-600" />
          </div>
        ) : posts.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <FileText className="w-12 h-12 mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500">No blog posts yet</p>
              <Button onClick={handleCreateNew} className="mt-4">
                <Plus className="w-4 h-4 mr-2" />
                Create Your First Post
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {posts.map((post) => (
              <Card key={post.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-start gap-4">
                    {post.featured_image && (
                      <img 
                        src={post.featured_image} 
                        alt={post.title}
                        className="w-24 h-24 object-cover rounded-lg flex-shrink-0"
                      />
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="font-semibold text-lg truncate">{post.title}</h3>
                          <p className="text-sm text-gray-500 mt-1 line-clamp-2">{post.excerpt}</p>
                        </div>
                        <div className="flex items-center gap-2 flex-shrink-0">
                          <Badge variant={post.status === 'published' ? 'default' : 'secondary'}>
                            {post.status === 'published' ? <CheckCircle className="w-3 h-3 mr-1" /> : <Clock className="w-3 h-3 mr-1" />}
                            {post.status}
                          </Badge>
                        </div>
                      </div>
                      <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                        {post.category && (
                          <span className="flex items-center gap-1">
                            <FolderOpen className="w-3 h-3" />
                            {post.category}
                          </span>
                        )}
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {new Date(post.created_at).toLocaleDateString()}
                        </span>
                        <span className="flex items-center gap-1">
                          <Eye className="w-3 h-3" />
                          {post.views || 0} views
                        </span>
                      </div>
                      {post.tags?.length > 0 && (
                        <div className="flex gap-1 mt-2">
                          {post.tags.slice(0, 4).map((tag, i) => (
                            <Badge key={i} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                          {post.tags.length > 4 && (
                            <Badge variant="outline" className="text-xs">+{post.tags.length - 4}</Badge>
                          )}
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {post.status === 'published' && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => window.open(`/blog/${post.slug}`, '_blank')}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                      )}
                      <Button variant="ghost" size="sm" onClick={() => handleEdit(post.id)}>
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => handleDelete(post.id)} className="text-red-600 hover:text-red-700">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-2 mt-6">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              Previous
            </Button>
            <span className="text-sm text-gray-600">
              Page {page} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
            >
              Next
            </Button>
          </div>
        )}
      </div>

      {/* AI Generation Dialog */}
      <Dialog open={showAIDialog} onOpenChange={setShowAIDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-purple-600" />
              AI Blog Generator
            </DialogTitle>
            <DialogDescription>
              Generate SEO-optimized blog content using AI
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div>
              <label className="block text-sm font-medium mb-1">Topic / Title *</label>
              <Input
                value={aiTopic}
                onChange={(e) => setAiTopic(e.target.value)}
                placeholder="e.g., How to Choose the Best Dishwasher for Your Kitchen"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Target Keywords (comma-separated)</label>
              <Input
                value={aiKeywords}
                onChange={(e) => setAiKeywords(e.target.value)}
                placeholder="e.g., best dishwasher, kitchen appliances, Bosch dishwasher"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Tone</label>
                <select
                  value={aiTone}
                  onChange={(e) => setAiTone(e.target.value)}
                  className="w-full p-2 border rounded"
                >
                  <option value="professional">Professional</option>
                  <option value="casual">Casual & Friendly</option>
                  <option value="informative">Informative & Educational</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Length</label>
                <select
                  value={aiLength}
                  onChange={(e) => setAiLength(e.target.value)}
                  className="w-full p-2 border rounded"
                >
                  <option value="short">Short (~500 words)</option>
                  <option value="medium">Medium (~1000 words)</option>
                  <option value="long">Long (~2000 words)</option>
                </select>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="outlineOnly"
                checked={aiOutlineOnly}
                onChange={(e) => setAiOutlineOnly(e.target.checked)}
                className="rounded"
              />
              <label htmlFor="outlineOnly" className="text-sm">
                Generate outline only (for manual expansion)
              </label>
            </div>

            {generatedContent && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg max-h-64 overflow-y-auto">
                <h4 className="font-medium mb-2">Generated Content Preview:</h4>
                <pre className="text-sm whitespace-pre-wrap">
                  {generatedContent.parsed?.title || generatedContent.raw_content?.substring(0, 500)}...
                </pre>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAIDialog(false)}>
              Cancel
            </Button>
            {generatedContent && (
              <Button variant="outline" onClick={applyGeneratedContent}>
                <FileEdit className="w-4 h-4 mr-2" />
                Use This Content
              </Button>
            )}
            <Button
              onClick={handleAIGenerate}
              disabled={generating || !aiTopic.trim()}
              className="bg-gradient-to-r from-purple-600 to-indigo-600"
            >
              {generating ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Sparkles className="w-4 h-4 mr-2" />
              )}
              {generating ? 'Generating...' : 'Generate'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default BlogManagement;