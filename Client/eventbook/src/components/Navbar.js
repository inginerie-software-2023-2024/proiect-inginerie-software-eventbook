import React from "react";
import { Link } from "react-router-dom";
import "../styles/Navbar.css";
import logo from "../assets/images.png";
import EventIcon from "@mui/icons-material/Event";
import GroupIcon from "@mui/icons-material/Group";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import NotificationsIcon from "@mui/icons-material/Notifications";
import LoginIcon from "@mui/icons-material/Login";

function Navbar() {
  return (
    <div id="application-header" className="scrolled">
      <div className="logo-container">
        <span className="app-name">EventBook</span>
        <div id="logo-img-container">
          <img src={logo} alt="Explorify Logo" className="logo" />
        </div>
      </div>
      <nav className="navigation-bar">
        <ul className="navigation-list">
          <li>
            <EventIcon />
            Events
          </li>
          <li>
            <GroupIcon />
            Friends
          </li>
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
      <Link to="/authentication" className="no-underline-link">
        <div className="login-register-buttons">
          <button className="login-button">
            <span className="login-register-text">Login</span>
            <LoginIcon className="login-icon" />
          </button>
        </div>
      </Link>
    </div>
  );
}

export default Navbar;
