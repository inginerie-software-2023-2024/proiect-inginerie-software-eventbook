import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ProtectedRoute from "./ProtectedRoute";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import Authentication from "./components/Authentication";
import Profile from "./components/Profile";
import Discover from "./components/Discover";
import { AuthProvider } from "./contexts/AuthContext";
import UserPage from "./components/UserPage";
import EventsFeed from "./components/EventsFeed";
import SingleEvent from "./components/SingleEvent";

function App() {
  return (
    <AuthProvider>
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<Hero />} />
          <Route path="/authentication/*" element={<Authentication />} />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />
          <Route path="/user/:username" element={<UserPage />} />
          <Route
            path="/discover"
            element={
              <ProtectedRoute>
                <Discover />
              </ProtectedRoute>
            }
          />
          <Route path="/events" element={<EventsFeed />} />
          <Route
            path="/events/:id"
            element={
              <ProtectedRoute>
                <SingleEvent />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
