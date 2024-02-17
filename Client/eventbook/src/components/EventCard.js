import React, { useState, useEffect } from "react";
import EditIcon from "@mui/icons-material/Edit";
import ClearIcon from "@mui/icons-material/Clear";
import CancelIcon from "@mui/icons-material/Cancel";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { jwtDecode } from "jwt-decode";
import CloseIcon from "@mui/icons-material/Close";

function EventCard({ event, onEventDeleted, onEditClicked }) {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showApprovalPopup, setShowApprovalPopup] = useState(false);
  const [currentUser, setCurrentUser] = useState(null); 
    useEffect(() => {
        const token = localStorage.getItem("authToken");
        if (token) {
            const decodedToken = jwtDecode(token);
            setCurrentUser(decodedToken); 
        }
    }, []);

  const handleEditClick = () => {
    onEditClicked(event);
  };

  const getUserIdFromToken = () => {
    const token = localStorage.getItem("authToken");
    if (token) {
      const decoded = jwtDecode(token);
      return decoded.id;
    }
    return null;
  };

  const handleApprovalClick = async (invitationId) => {
    try {
      const userId = getUserIdFromToken();
      if (!userId) {
        throw new Error("User ID not found in token");
      }

      const response = await fetch(
        `http://localhost:8080/events/${event.id}/approve_request?invitation_id=${invitationId}`,
        {
          method: "POST",
          headers: {
            accept: "application/json",
            Authorization: `Bearer ${localStorage.getItem("authToken")}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      setShowApprovalPopup(false);
      toast.success("Request Approved", {
        position: "top-center",
        autoClose: 2000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
      // Refresh event data or update UI
    } catch (error) {
      console.error("Failed to approve request:", error);
    }
  };
  const ApprovalPopup = () => (
    <div className="approval-popup-container">
      <div id="approval-popup">
        {event.requests_to_join.map((request, index) => (
          <div key={index} className="request-item">
            <span id="approve">Approve invitation</span>
            <button
              onClick={() => handleApprovalClick(request.id)}
              className="approve-button"
            >
              Approve
            </button>
          </div>
        ))}
        <button
          onClick={() => setShowApprovalPopup(false)}
          className="cancel-button"
        >
          <CloseIcon fontSize="large" />
        </button>
      </div>
    </div>
  );

    const sendEventUpdateNotification = async () => {
    try {
      const updatedNotification = {
        content: `Event "${event.title}" has been deleted.`,
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
        throw new Error("Failed to send event delete notification");
      }
    } catch (error) {
      console.error('Failed to send event delete notification:', error);
    }
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

      await sendEventUpdateNotification();

      toast.success("Event Deleted", {
        position: "top-center",
        autoClose: 2000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
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
            <CancelIcon />
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <a className="event-card">
      <ToastContainer />
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
      {currentUser!=null && event.admins.includes(currentUser.id) && (
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
        {event.requests_to_join && event.requests_to_join.length > 0 && (
          <button
            className="view-join card-buttons button"
            onClick={() => setShowApprovalPopup(true)}
          >
            View Join Requests
          </button>
        )}
        {showApprovalPopup && <ApprovalPopup />}
      </div>
      )}
    </a>
  );
}

export default EventCard;
