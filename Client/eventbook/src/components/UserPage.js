import { Link, useParams } from "react-router-dom";
import React, { useState, useEffect } from "react";
import profile from "../assets/profile.png";
import EmailIcon from "@mui/icons-material/Email";
import BadgeIcon from "@mui/icons-material/Badge";
import "../styles/UserPage.css";
import StrangerEvent from "./StrangerEvent";

function UserPage() {
  let { username } = useParams();
  const [userData, setUserData] = useState(null);
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const token = localStorage.getItem("authToken");
        const response = await fetch(
          `http://127.0.0.1:8080/users/${username}`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setUserData(data);

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
        console.error("Failed to fetch user data:", error);
      }
    };

    fetchUserData();
  }, [username]);

  return (
    <>
      <div id="user-page">
        <div id="profile-card-container">
          <div id="profile-card">
            <div className="profile-details-container">
              <img src={profile} className="image" alt="profile" />
              <div id="details-container">
                {userData ? (
                  <>
                    <div className="username-container">
                      <BadgeIcon />
                      <p id="username">{userData.username}</p>
                    </div>
                    <div className="email-container">
                      <EmailIcon />
                      <p id="email">{userData.email}</p>
                    </div>
                  </>
                ) : (
                  <p>Loading user data...</p>
                )}
              </div>
            </div>
          </div>
        </div>
        <div id="my-events-list">
          <h1 id="events-header">My Events</h1>
          {events.length === 0 ? (
            <p>User has no events</p>
          ) : (
            events.map((event) => (
              <Link to={`/events/${event.id}`}>
                <StrangerEvent key={event.id} event={event} />
              </Link>
            ))
          )}
        </div>
      </div>
    </>
  );
}

export default UserPage;
