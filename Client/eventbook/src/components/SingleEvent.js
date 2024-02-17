import image1 from "../assets/events_pictures/1.jpg";
import image2 from "../assets/events_pictures/2.jpg";
import image3 from "../assets/events_pictures/3.jpg";
import image4 from "../assets/events_pictures/4.jpg";
import image5 from "../assets/events_pictures/5.jpg";
import React, { useState, useEffect } from "react";
import { useParams} from "react-router-dom";
import "../styles/SingleEvent.css";
import AccessTimeIcon from "@mui/icons-material/AccessTime";
import LocationOnIcon from "@mui/icons-material/LocationOn";
import PersonIcon from "@mui/icons-material/Person";
import CloudIcon from "@mui/icons-material/Cloud";
import PlusOneIcon from "@mui/icons-material/AddCircle";
import FaceIcon from "@mui/icons-material/Face";
import ThermostatIcon from "@mui/icons-material/Thermostat";
import WaterIcon from "@mui/icons-material/Water";
import WindPowerIcon from "@mui/icons-material/WindPower";
import "react-toastify/dist/ReactToastify.css";
import { ToastContainer, toast } from "react-toastify";
import { jwtDecode } from "jwt-decode";
import SentInvitationModal from "./SentInvitationModal";

function SingleEvent() {
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [eventData, setEventData] = useState(null);
  const [error, setError] = useState(null);
  const [participants, setParticipants] = useState([]);
  const { id } = useParams();
  const [isParticipant, setIsParticipant] = useState(false);
  const notifySuccess = (message) => {
    toast.success(message, {
      position: "top-center",
      autoClose: 2000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      progress: undefined,
    });
  };

  const fetchParticipantDetails = async (participantId) => {
    try {
      const token = localStorage.getItem("authToken");
      if (!token) {
        throw new Error("Authorization token is missing");
      }

      const response = await fetch(`http://localhost:8080/users/${participantId}/v1`, {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }


      const data = await response.json();
      console.log(data);
      return data; // returnează detalii despre utilizator
    } catch (error) {
      console.error("Failed to fetch participant details:", error);
      return null;
    }
  };

   const fetchEventParticipants = async () => {
    try {
      const token = localStorage.getItem("authToken");
      if (!token) {
        throw new Error("Authorization token is missing");
      }

      const response = await fetch(`http://localhost:8080/events/${id}/participants`, {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const participantIds = await response.json();

      // Obține detalii despre fiecare participant
      const participantsData = await Promise.all(participantIds.map(async (participantId) => {
        return await fetchParticipantDetails(participantId);
      }));

      setParticipants(participantsData.filter(participant => participant !== null)); // filtrează participanții care nu au fost găsiți
    } catch (error) {
      console.error("Failed to fetch event participants:", error);
      setError("Failed to fetch event participants");
    }
  };


  useEffect(() => {
    fetchEventParticipants();
  }, [id]);

  const sendEventLeaveNotification = async () => {
    try {
      const updatedNotification = {
        content: `Left successfully the "${eventData.title}" event`,
        notification_type: "event_update",
      };

      const userId = getUserIdFromToken();
      if (!userId) {
        throw new Error("User ID not found in token");
      }

      const token = localStorage.getItem("authToken");
      const response = await fetch(`http://127.0.0.1:8080/notifications/${userId}/notify?notification_type=${updatedNotification.notification_type}&content=${updatedNotification.content}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(updatedNotification),
      });

      if (!response.ok) {
        throw new Error("Failed to send event leave notification");
      }
    } catch (error) {
      console.error('Failed to send event leave notification:', error);
    }
  };
  const handleLeaveEvent = async () => {
    try {
      const token = localStorage.getItem("authToken");
      if (!token) {
        throw new Error("Authorization token is missing");
      }

      const response = await fetch(`http://localhost:8080/events/${id}/leave`, {
        method: "DELETE",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      await sendEventLeaveNotification();

      console.log("Left event successfully");
      notifySuccess("You have successfully left the event!");
      setIsParticipant(false);
      fetchEventParticipants();
    } catch (error) {
      setError(error.message);
    }
  };

  const getUserIdFromToken = () => {
    const token = localStorage.getItem("authToken");
    if (token) {
      const decoded = jwtDecode(token);
      return decoded.id;
    }
    return null;
  };

  const sendEventUpdateNotification = async () => {
    try {
      const updatedNotification = {
        content: `Joined successfully to "${eventData.title}" event`,
        notification_type: "event_update",
      };

      const userId = getUserIdFromToken();
      if (!userId) {
        throw new Error("User ID not found in token");
      }

      const token = localStorage.getItem("authToken");
      const response = await fetch(`http://127.0.0.1:8080/notifications/${userId}/notify?notification_type=${updatedNotification.notification_type}&content=${updatedNotification.content}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(updatedNotification),
      });

      if (!response.ok) {
        throw new Error("Failed to send event join notification");
      }
    } catch (error) {
      console.error('Failed to send event join notification:', error);
    }
  };

  const handleOpenInviteModal = () => {
    setShowInviteModal(true);
  };

  const handleJoinEvent = async () => {
    if (isParticipant) {
      return;
    }

    try {
      const token = localStorage.getItem("authToken");
      if (!token) {
        throw new Error("Authorization token is missing");
      }

      const response = await fetch(`http://localhost:8080/events/${id}/join`, {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      await sendEventUpdateNotification();

      console.log("Sucessfully joined");
      notifySuccess("Successfully joined");
      setIsParticipant(true);
      fetchEventParticipants();
    } catch (error) {
      setError(error.message);
    }
  };

  function parseJwt(token) {
    try {
      const base64Url = token.split(".")[1];
      const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split("")
          .map(function (c) {
            return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
          })
          .join("")
      );

      return JSON.parse(jsonPayload);
    } catch (error) {
      return null;
    }
  }
  const images = [image1, image2, image3, image4, image5];
  const randomImage = images[Math.floor(Math.random() * images.length)];
  useEffect(() => {
    const fetchEventData = async () => {
      try {
        let token = localStorage.getItem("authToken");
        if (!token) {
          throw new Error("No authorization token found");
        }

        const response = await fetch(`http://localhost:8080/events/${id}`, {
          method: "GET",
          headers: {
            Accept: "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        setEventData(data);
      } catch (error) {
        setError(error.message);
      }
    };

    fetchEventData();
  }, [id]);

  useEffect(() => {
    if (eventData && eventData.participants) {
      const token = localStorage.getItem("authToken");
      if (token) {
        const decodedToken = parseJwt(token);
        const userId = decodedToken && decodedToken.id;
        setIsParticipant(eventData.participants.includes(userId));
      }
    }
  }, [eventData]);

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!eventData) {
    return <div>Loading...</div>;
  }
  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleString();
  };
  const firstWeatherDetail =
    eventData.weather && eventData.weather.length > 0
      ? eventData.weather[0].hourly_data[0]
      : null;

  return (
    <>
      <ToastContainer />
      <div className="single-card-event">
        <div className="single-event-header">
          {eventData.organizer_name && (
            <p className="icon-location-container">
              <PersonIcon />
              <span>{eventData.organizer_name}</span>
            </p>
          )}
          <h1>{eventData.title}</h1>
          {eventData.public !== null && (
            <p className="event-status">
              {eventData.public ? "Public" : "Private"}
            </p>
          )}
        </div>

        {eventData.tags && eventData.tags.length > 0 && (
          <div id="tag-list">
            {eventData.tags.map((tag, index) => (
              <span key={index} className="event-tag">
                {tag}
              </span>
            ))}
          </div>
        )}
        <img src={randomImage} alt="Event" className="event-image" />
        {eventData.description && <p>{eventData.description}</p>}
        {eventData.start_time && (
          <p className="time-container">
            <AccessTimeIcon />
            Starts: {formatDate(eventData.start_time)}
          </p>
        )}
        {eventData.end_time && (
          <p className="time-container">
            <AccessTimeIcon />
            Ends: {formatDate(eventData.end_time)}
          </p>
        )}
        {eventData.location && (
          <p className="icon-location-container">
            <LocationOnIcon />
            <span>{eventData.location}</span>
          </p>
        )}
        <button
          className="join-event-button"
          onClick={isParticipant ? handleLeaveEvent : handleJoinEvent}
        >
          <span className="join-text-button">
            {isParticipant ? "Leave" : "Join"}
          </span>
        </button>
      </div>

      {/* Participants list */}
      <div className="participants-continer">
        <h2>Participants</h2>
        <ul>
        { participants.map((participant, index) => (
          <div className="participants-list">
            <FaceIcon />
              <span>{participant.username}</span>
          </div>
        )) }
        </ul>
        <button
          className="add-participant-button"
          onClick= { isParticipant ? handleOpenInviteModal : handleJoinEvent }
        >
          <span className="join-text-button">
            <PlusOneIcon />
            {isParticipant ? "Add participant" : "Join us"}
          </span>
        </button>
      </div>

      {firstWeatherDetail && (
        <div className="weather-event-continer">
          <CloudIcon className="cloud-icon" />
          <div className="weather-details">
            <p><ThermostatIcon />Temperature: {firstWeatherDetail.temperature_2m}°C</p>
            <p><WaterIcon />Humidity: {firstWeatherDetail.relative_humidity_2m}%</p>
            <p><WindPowerIcon /> Wind Speed: {firstWeatherDetail.wind_speed_80m} km/h</p>
          </div>
        </div>
      )}

      {showInviteModal && (
        <SentInvitationModal
          event={eventData}
          onClose={() => setShowInviteModal(false)}
          participants = {participants}
        />
      )}
    </>
  );
}

export default SingleEvent;
