import { useState, useEffect, useCallback, useContext, createContext } from 'react';
import { BACKEND_URL } from '../config/api';
import { cartAPI } from '../services/api';

// Cart Context for global state management
export const CartContext = createContext();

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState([]);
  const [cartItems, setCartItems] = useState([]);
  const [cartTotal, setCartTotal] = useState(0);
  const [cartCount, setCartCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load cart from localStorage on mount
  useEffect(() => {
    const savedCart = localStorage.getItem('shopping_cart');
    if (savedCart) {
      try {
        const parsedCart = JSON.parse(savedCart);
        setCartItems(parsedCart);
        updateCartStats(parsedCart);
      } catch (error) {
        console.error('Error loading cart:', error);
      }
    }
  }, []);

  // Reload when combo code writes the cart directly
  useEffect(() => {
    const reload = () => {
      try { setCartItems(JSON.parse(localStorage.getItem('shopping_cart') || '[]')); } catch (e) { /* ignore */ }
    };
    window.addEventListener('cartUpdated', reload);
    return () => window.removeEventListener('cartUpdated', reload);
  }, []);

  // Update cart statistics
  const updateCartStats = (items) => {
    const total = items.reduce((sum, item) => {
      const product = item.product || item;
      return sum + (product.price * item.quantity);
    }, 0);
    const count = items.reduce((sum, item) => sum + item.quantity, 0);
    
    setCartTotal(total);
    setCartCount(count);
  };

  // Save cart to localStorage whenever it changes
  useEffect(() => {
    if (cartItems.length > 0) {
      localStorage.setItem('shopping_cart', JSON.stringify(cartItems));
      updateCartStats(cartItems);
    } else {
      localStorage.removeItem('shopping_cart');
      setCartTotal(0);
      setCartCount(0);
    }
  }, [cartItems]);

  const addToCart = useCallback(async (productId, quantity = 1) => {
    setLoading(true);
    setError(null);
    
    try {
      // For now, we need to fetch the product details
      // In a real app, you'd pass the full product object or fetch from API
      const response = await fetch(`${BACKEND_URL}/api/products/${productId}`);
      if (!response.ok) {
        throw new Error('Product not found');
      }
      const productData = await response.json();
      const product = productData.product || productData;
      
      setCartItems(prevItems => {
        const existingItem = prevItems.find(item => {
          const itemProduct = item.product || item;
          return itemProduct.id === productId && !item.combo_id;
        });
        
        if (existingItem) {
          // Update quantity if item exists
          return prevItems.map(item => {
            const itemProduct = item.product || item;
            return itemProduct.id === productId && !item.combo_id
              ? { ...item, quantity: item.quantity + quantity }
              : item;
          });
        } else {
          // Add new item
          return [...prevItems, { product, quantity }];
        }
      });
      
      return true;
    } catch (err) {
      setError(err.message || 'Failed to add item to cart');
      console.error('Add to cart error:', err);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateQuantity = useCallback(async (productId, newQuantity) => {
    if (newQuantity <= 0) {
      return removeFromCart(productId);
    }

    setCartItems(prevItems =>
      prevItems.map(item => {
        const itemProduct = item.product || item;
        return itemProduct.id === productId
          ? { ...item, quantity: newQuantity }
          : item;
      })
    );
    
    return true;
  }, []);

  const removeFromCart = useCallback(async (productId) => {
    setCartItems(prevItems => {
      const hit = prevItems.find(i => (i.product || i).id === productId);
      if (hit && hit.combo_id) return prevItems.filter(i => i.combo_id !== hit.combo_id);
      return prevItems.filter(i => (i.product || i).id !== productId);
    });
    return true;
  }, []);

  const clearCart = useCallback(async () => {
    setCartItems([]);
    setCartTotal(0);
    setCartCount(0);
    localStorage.removeItem('shopping_cart');
    return true;
  }, []);

  const fetchCart = useCallback(async () => {
    // For localStorage-based cart, just reload from storage
    const savedCart = localStorage.getItem('shopping_cart');
    if (savedCart) {
      try {
        const parsedCart = JSON.parse(savedCart);
        setCartItems(parsedCart);
        updateCartStats(parsedCart);
      } catch (error) {
        console.error('Error loading cart:', error);
      }
    }
  }, []);

  const value = {
    cart,
    cartItems,
    cartTotal,
    cartCount,
    loading,
    error,
    addToCart,
    updateQuantity,
    removeFromCart,
    clearCart,
    refreshCart: fetchCart,
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

// Standalone hook for components that don't need global cart state
export const useCartActions = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const addToCart = useCallback(async (productId, quantity = 1) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await cartAPI.addToCart(productId, quantity);
      return response;
    } catch (err) {
      setError(err.message || 'Failed to add item to cart');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getCart = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await cartAPI.getCart();
      return response;
    } catch (err) {
      setError(err.message || 'Failed to fetch cart');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    addToCart,
    getCart,
    loading,
    error,
  };
};