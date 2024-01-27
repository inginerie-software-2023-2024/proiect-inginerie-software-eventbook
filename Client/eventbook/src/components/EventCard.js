import React from "react";
import EditIcon from "@mui/icons-material/Edit";
import ClearIcon from "@mui/icons-material/Clear";

function EventCard({ event }) {
  return (
    <div className="event-card">
      <div className="event-details-container">
        <h3 id="event-title">{event.title}</h3>
        <p id="event-description">{event.description}</p>
        <div id="tag-list">
          {event.tags.map((tag, index) => (
            <span key={index} className="event-tag">
              {tag}
            </span>
          ))}
        </div>
      </div>

      <div className="card-action-buttons">
        <button className="button edit card-buttons">
          <EditIcon />
          <span className="button-name">Edit</span>
        </button>
        <button className="button delete card-buttons">
          <ClearIcon />
          <span className="button-name">Delete</span>
        </button>
      </div>
    </div>
  );
}

export default EventCard;
