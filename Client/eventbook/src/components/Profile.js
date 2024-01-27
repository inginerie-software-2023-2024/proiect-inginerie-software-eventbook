import React, { useState, useEffect } from "react";
import profile from "../assets/profile.png";
import BadgeIcon from "@mui/icons-material/Badge";
import "../styles/Profile.css";
import EmailIcon from "@mui/icons-material/Email";
import EditIcon from "@mui/icons-material/Edit";
import ClearIcon from "@mui/icons-material/Clear";
import EventCard from "./EventCard";

function Profile() {
  const [userDetails, setUserDetails] = useState("");
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const fetchUserDetails = async () => {
      const token = localStorage.getItem("authToken");
      try {
        const response = await fetch("http://127.0.0.1:8080/users/me", {
          method: "GET",
          headers: {
            accept: "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setUserDetails(data);

        const eventsResponse = await fetch(
          `http://127.0.0.1:8080/events?organizer_name=${data.username}`,
          {
            method: "GET",
            headers: {
              accept: "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!eventsResponse.ok) {
          throw new Error(`HTTP error! status: ${eventsResponse.status}`);
        }
        const eventsData = await eventsResponse.json();
        setEvents(eventsData);
      } catch (error) {
        console.error("Fetching user details failed:", error);
      }
    };

    fetchUserDetails();
  }, []);
  return (
    <div id="main-container">
      <div id="profile-card-container">
        <div id="profile-card">
          <div className="profile-details-container">
            <img src={profile} className="image" alt="profile" />
            <div id="details-container">
              <div className="username-container">
                <BadgeIcon />
                <p id="username">{userDetails.username}</p>
              </div>
              <div className="email-container">
                <EmailIcon />
                <p id="email">{userDetails.email}</p>
              </div>
              <div id="buttons-container">
                <button className="button edit">
                  <EditIcon />
                  <span className="button-name">Edit</span>
                </button>
                <button className="button delete">
                  <ClearIcon />
                  <span className="button-name">Delete</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div id="my-events-list">
        <h1 id="events-header">My Events</h1>
        {events.map((event) => (
          <EventCard key={event.id} event={event} />
        ))}
      </div>
    </div>
  );
}

export default Profile;
