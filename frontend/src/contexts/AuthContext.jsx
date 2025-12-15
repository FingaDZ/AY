import React, { createContext, useContext, useState, useEffect } from 'react';
import utilisateursService from '../services/utilisateurs';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth doit être utilisé dans un AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Vérifier si un utilisateur est déjà connecté
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await utilisateursService.login(email, password);
      // Le backend retourne { user: {...}, message: "..." }
      const userData = response.user;
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      return userData;
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  const isAdmin = () => {
    return user && user.role === 'Admin';
  };

  const isGestionnaire = () => {
    return user && (user.role === 'Admin' || user.role === 'Gestionnaire');
  };

  const isUtilisateur = () => {
    return user && user.role === 'Utilisateur';
  };

  const value = {
    user,
    login,
    logout,
    isAdmin,
    isGestionnaire,
    isUtilisateur,
    loading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
