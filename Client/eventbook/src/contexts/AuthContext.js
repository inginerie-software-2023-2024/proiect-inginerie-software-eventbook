import React, { createContext, useState, useContext, useEffect } from "react";

export const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("authToken");

    if (token) {
      setIsLoggedIn(true);
    }
  }, []);

  const loginUser = (token) => {
    localStorage.setItem("authToken", token);
    setIsLoggedIn(true);
  };
  const logout = () => {
    setIsLoggedIn(false);
    localStorage.removeItem("authToken");
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, loginUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
