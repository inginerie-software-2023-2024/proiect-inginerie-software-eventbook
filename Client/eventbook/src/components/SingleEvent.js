import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import "../styles/SingleEvent.css";
import AccessTimeIcon from "@mui/icons-material/AccessTime";

function SingleEvent() {
  const [eventData, setEventData] = useState(null);
  const [error, setError] = useState(null);
  const { id } = useParams();

  useEffect(() => {
    const fetchEventData = async () => {
      try {
        const token = localStorage.getItem("authToken");

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

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!eventData) {
    return <div>Loading...</div>;
  }
  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleString(); // Converts to milliseconds and formats
  };

  return (
    <div className="single-event-card">
      <div className="single-event-header">
        {eventData.organizer_name && <p>By: {eventData.organizer_name}</p>}
        <h1>{eventData.title}</h1>
        {eventData.public !== null && (
          <p>{eventData.public ? "Public" : "Private"}</p>
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
      {eventData.location && <p>Location: {eventData.location}</p>}
      {/* Add other fields as needed */}
    </div>
  );
}

export default SingleEvent;
