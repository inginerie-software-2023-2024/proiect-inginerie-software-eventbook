import React, { useState, useEffect } from "react";
import profile from "../assets/profile.png";
import BadgeIcon from "@mui/icons-material/Badge";
import "../styles/Profile.css";
import EmailIcon from "@mui/icons-material/Email";
import EditIcon from "@mui/icons-material/Edit";
import ClearIcon from "@mui/icons-material/Clear";
import EventCard from "./EventCard";
import EditProfile from "./EditProfile";
import { useNavigate } from "react-router-dom";
import { ToastContainer, toast } from "react-toastify";
import EditEventModal from "./EditEventModal";

function Profile() {
  const navigate = useNavigate();
  const [userDetails, setUserDetails] = useState("");
  const [events, setEvents] = useState([]);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editingEvent, setEditingEvent] = useState(null);

  const openEdit = () => setIsEditOpen(true);
  const closeEdit = () => setIsEditOpen(false);

  const openEditModal = (event) => {
    setEditingEvent(event);
  };

  const closeEditModal = () => {
    setEditingEvent(null);
  };

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

  const deleteUser = async () => {
    const isConfirmed = window.confirm(
      "Are you sure you want to delete your account? This cannot be undone."
    );
    if (!isConfirmed) {
      return;
    }

    const token = localStorage.getItem("authToken");
    try {
      const response = await fetch("http://127.0.0.1:8080/users/delete", {
        method: "DELETE",
        headers: {
          accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      toast.success("User Deleted", {
        position: "bottom-center",
        autoClose: 2000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
      setTimeout(() => {
        navigate("/authentication/login");
      }, 2000);
    } catch (error) {
      console.error("Failed to delete user:", error);
    }
  };

  const handleEventDeleted = (deletedEventId) => {
    const updatedEvents = events.filter((event) => event.id !== deletedEventId);
    setEvents(updatedEvents);
  };

  return (
    <>
      <ToastContainer />
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
                  <button className="button edit" onClick={openEdit}>
                    <EditIcon />
                    <span className="button-name">Edit</span>
                  </button>
                  <button className="button delete">
                    <ClearIcon />
                    <span className="button-name" onClick={deleteUser}>
                      Delete
                    </span>
                  </button>
                </div>
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
              <EventCard
                key={event.id}
                event={event}
                onEventDeleted={handleEventDeleted}
                onEditClicked={() => openEditModal(event)}
              />
            ))
          )}
          {editingEvent && (
            <EditEventModal
              event={editingEvent}
              onClose={closeEditModal}
              isEdit={true}
            />
          )}
        </div>

        <EditProfile
          show={isEditOpen}
          onClose={closeEdit}
          userDetails={userDetails}
        ></EditProfile>
      </div>
    </>
  );
}

export default Profile;
