import { useState, useEffect, useCallback, useMemo } from 'react';
import { productAPI } from '../services/api';

export const useProducts = (initialFilters = {}) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState(initialFilters);

  // Memoize the filters to prevent unnecessary re-renders
  const memoizedFilters = useMemo(() => filters, [filters]);

  const fetchProducts = useCallback(async (filterParams = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await productAPI.getProducts(filterParams);
      setProducts(response.products || []);
    } catch (err) {
      setError(err.message || 'Failed to fetch products');
      console.error('Products fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []); // No dependencies needed here since we pass params directly

  useEffect(() => {
    fetchProducts(memoizedFilters);
  }, [memoizedFilters, fetchProducts]);

  const updateFilters = useCallback((newFilters) => {
    setFilters(prevFilters => {
      // Only update if there are actual changes
      const updatedFilters = { ...prevFilters, ...newFilters };
      
      // Check if filters actually changed to prevent unnecessary updates
      const hasChanged = Object.keys(updatedFilters).some(
        key => updatedFilters[key] !== prevFilters[key]
      );
      
      return hasChanged ? updatedFilters : prevFilters;
    });
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({});
  }, []);

  const refresh = useCallback(() => {
    fetchProducts(memoizedFilters);
  }, [fetchProducts, memoizedFilters]);

  return {
    products,
    loading,
    error,
    filters,
    updateFilters,
    clearFilters,
    refresh,
  };
};

export const useProduct = (productId) => {
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!productId) {
      setLoading(false);
      return;
    }

    const fetchProduct = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await productAPI.getProduct(productId);
        setProduct(response.product);
      } catch (err) {
        setError(err.message || 'Failed to fetch product');
        console.error('Product fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [productId]);

  return { product, loading, error };
};

export const useCategories = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await productAPI.getCategories();
        setCategories(response.categories || []);
      } catch (err) {
        setError(err.message || 'Failed to fetch categories');
        console.error('Categories fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, []);

  return { categories, loading, error };
};

export const useBrands = () => {
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchBrands = async () => {
      try {
        const response = await productAPI.getBrands();
        setBrands(response.brands || []);
      } catch (err) {
        setError(err.message || 'Failed to fetch brands');
        console.error('Brands fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchBrands();
  }, []);

  return { brands, loading, error };
};