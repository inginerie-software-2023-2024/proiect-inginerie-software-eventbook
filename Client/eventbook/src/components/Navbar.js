import React from "react";
import { Link } from "react-router-dom";
import "../styles/Navbar.css";
import logo from "../assets/images.png";
import EventIcon from "@mui/icons-material/Event";
import GroupIcon from "@mui/icons-material/Group";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import NotificationsIcon from "@mui/icons-material/Notifications";
import LoginIcon from "@mui/icons-material/Login";
import LogoutIcon from "@mui/icons-material/Logout";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";

function Navbar() {
  const { isLoggedIn, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    navigate("/authentication/login");
    logout();
  };
  return (
    <div id="application-header" className="scrolled">
      <Link to="/" className="logo-container no-underline-link">
        <span className="app-name">EventBook</span>
        <div id="logo-img-container">
          <img src={logo} alt="Explorify Logo" className="logo" />
        </div>
      </Link>
      <nav className="navigation-bar">
        <ul className="navigation-list">
          <Link to="/events" className="no-underline-link">
            <li>
              <EventIcon />
              Events
            </li>
          </Link>
          <Link to="/discover" className="no-underline-link">
            <li>
              <GroupIcon />
              Discover
            </li>
          </Link>
          <Link to="/profile" className="no-underline-link">
            <li>
              <AccountCircleIcon />
              Profile
            </li>
          </Link>
          <li>
            <NotificationsIcon />
            Notifications
          </li>
        </ul>
      </nav>
      {isLoggedIn ? (
        <button onClick={handleLogout} className="login-button">
          <span className="login-register-text">Logout</span>
          <LogoutIcon className="login-icon" />
        </button>
      ) : (
        <Link to="/authentication/login" className="no-underline-link">
          <div className="login-register-buttons">
            <button className="login-button">
              <span className="login-register-text">Login</span>
              <LoginIcon className="login-icon" />
            </button>
          </div>
        </Link>
      )}
    </div>
  );
}

export default Navbar;
