import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = () => {
      try {
        const storedUser = localStorage.getItem('user') || localStorage.getItem('userData');
        const storedToken = localStorage.getItem('token') || localStorage.getItem('userToken');
        
        if (storedUser && storedToken) {
          setUser(JSON.parse(storedUser));
          setToken(storedToken);
        }
      } catch (e) {
        console.error('[AuthContext] Error initializing auth:', e);
        // Clear corrupted data
        clearAuth();
      } finally {
        setLoading(false);
      }
    };

    initAuth();

    // Listen for storage changes from other tabs
    const handleStorageChange = (e) => {
      if (e.key === 'user' || e.key === 'userData' || e.key === 'token' || e.key === 'userToken') {
        initAuth();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const login = useCallback((userData, accessToken) => {
    console.log('[AuthContext] Login:', userData?.email);
    
    // Store in state
    setUser(userData);
    setToken(accessToken);
    
    // Store in localStorage (both keys for compatibility)
    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('userData', JSON.stringify(userData));
    if (accessToken) {
      localStorage.setItem('token', accessToken);
      localStorage.setItem('userToken', accessToken);
    }
    
    // Dispatch custom event for components that don't use context
    window.dispatchEvent(new CustomEvent('auth-change', { detail: { user: userData, token: accessToken } }));
  }, []);

  const logout = useCallback(() => {
    console.log('[AuthContext] Logout');
    
    // Clear state
    setUser(null);
    setToken(null);
    
    // Clear localStorage
    localStorage.removeItem('user');
    localStorage.removeItem('userData');
    localStorage.removeItem('token');
    localStorage.removeItem('userToken');
    
    // Dispatch custom event
    window.dispatchEvent(new CustomEvent('auth-change', { detail: { user: null, token: null } }));
  }, []);

  const clearAuth = useCallback(() => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('user');
    localStorage.removeItem('userData');
    localStorage.removeItem('token');
    localStorage.removeItem('userToken');
  }, []);

  const updateUser = useCallback((updatedData) => {
    const newUser = { ...user, ...updatedData };
    setUser(newUser);
    localStorage.setItem('user', JSON.stringify(newUser));
    localStorage.setItem('userData', JSON.stringify(newUser));
  }, [user]);

  const isAuthenticated = !!user;

  const value = {
    user,
    token,
    loading,
    isAuthenticated,
    login,
    logout,
    clearAuth,
    updateUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
