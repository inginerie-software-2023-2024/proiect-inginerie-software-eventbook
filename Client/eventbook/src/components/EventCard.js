import React, { useState } from "react";
import EditIcon from "@mui/icons-material/Edit";
import ClearIcon from "@mui/icons-material/Clear";

function EventCard({ event, onEventDeleted, onEditClicked }) {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleEditClick = () => {
    onEditClicked(event);
  };

  const deleteEvent = async () => {
    try {
      const token = localStorage.getItem("authToken");
      const response = await fetch(`http://127.0.0.1:8080/events/${event.id}`, {
        method: "DELETE",
        headers: {
          accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      onEventDeleted(event.id);
    } catch (error) {
      console.error("Failed to delete event:", error);
    }
  };

  const ConfirmationModal = () => (
    <div className="confirmation-modal-container">
      <div id="confirmation-modal">
        <p className="confirm-text">
          Are you sure you want to delete this event?
        </p>
        <div className="modal-buttons">
          <button
            onClick={() => {
              deleteEvent();
              setShowDeleteConfirm(false);
            }}
            className="delete-button modal-button"
          >
            Confirm
          </button>
          <button
            className="cancel-button modal-button"
            onClick={() => setShowDeleteConfirm(false)}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );

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
        <button className="button edit card-buttons" onClick={handleEditClick}>
          <EditIcon />
          <span className="button-name">Edit</span>
        </button>
        <button
          className="button delete card-buttons"
          onClick={() => setShowDeleteConfirm(true)}
        >
          <ClearIcon />
          <span className="button-name">Delete</span>
        </button>
        {showDeleteConfirm && <ConfirmationModal />}
      </div>
    </div>
  );
}

export default EventCard;
