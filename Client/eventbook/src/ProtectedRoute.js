import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "./contexts/AuthContext";

const ProtectedRoute = ({ children }) => {
  const { isLoggedIn } = useAuth();

  if (!isLoggedIn) {
    setTimeout(() => {
      return <Navigate to="/authentication/login" replace />;
    }, 100);
  }

  return children;
};

export default ProtectedRoute;
