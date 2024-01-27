import React from "react";
import "../styles/Hero.css";
import WavingHandIcon from "@mui/icons-material/WavingHand";
function Hero() {
  return (
    <div className="hero-page-container">
      <p className="title">Crafting Memorable Moments!</p>
      <div className="card-container">
        <p className="title-decription">
          Welcome!
          <WavingHandIcon />
        </p>
        <p className="text-description">
          Your go-to app for creating, discovering, and enjoying events. Whether
          you're looking to organize a local meetup, a corporate conference, or
          the wedding of your dreams, EventBook simplifies it all. Connect with
          friends, manage your events, and make every gathering unforgettable
        </p>
      </div>
    </div>
  );
}

export default Hero;
