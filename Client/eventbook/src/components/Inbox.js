import React, { useState, useEffect } from 'react';
import "../styles/Inbox.css";
import { jwtDecode } from "jwt-decode";
import { ToastContainer, toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

function Inbox() {
  const [notifications, setNotifications] = useState([]);
  const [currentUser, setCurrentUser] = useState(null); 

    useEffect(() => {
        const token = localStorage.getItem("authToken");
        if (token) {
            const decodedToken = jwtDecode(token);
            setCurrentUser(decodedToken); 
        }
    }, []);

  const navigate = useNavigate();
  const refreshPage = () => {
    navigate("/refresh");

    setTimeout(() => {
      navigate("/inbox");
    }, 10);
  };

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const token = localStorage.getItem("authToken");
        if (!token) {
          throw new Error("Token not found");
        }

        const userId = getUserIdFromToken();

        if (!userId) {
          throw new Error("User ID not found in token");
        }

        const response = await fetch(`http://127.0.0.1:8080/notifications/${userId}`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch notifications');
        }

        const data = await response.json();
        setNotifications(data);

        console.log("Notificări primite de la server:", data);
      } catch (error) {
        console.error('Failed to fetch notifications:', error);
      }
    };

    fetchNotifications();
  }, []);


  const getUserIdFromToken = () => {
    const token = localStorage.getItem("authToken");
    if (token) {
      const decoded = jwtDecode(token);
      return decoded.id;
    }
    return null;
  };



  const handleAcceptInvitation = async (notification) => {
    try {
      const token = localStorage.getItem("authToken");
      if (!token) {
        throw new Error("Authorization token is missing");
      }
      
      const response = await fetch(`http://localhost:8080/events/${notification.event_id}/join`, {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      console.log("Sucessfully joined");
      console.log(notification.id);
    } catch (error) {
      toast.error(error.message);
    }
  };
  


  const handleDeleteNotification = async (notify_id, notification=null) => {
    try {
      const token = localStorage.getItem("authToken");
      if (!token) {
        throw new Error("Token not found");
      }

      const userId = getUserIdFromToken();

      if (!userId) {
        throw new Error("User ID not found in token");
      }
      const event_id = notifications.event_id;
      
      const response = await fetch(`http://127.0.0.1:8080/notifications/${userId}/${notify_id}`, {
        method: 'DELETE',
        headers: {
          accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to delete notification, status: ${response.status}`);
      }
      if(event_id)
        navigate(`http://127.0.0.1:8080/events/${event_id}`);

      setTimeout(() => {
          refreshPage();
        }, 1);

      toast.success("Notification Deleted", {
        position: "top-center",
        autoClose: 2000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });

    } catch (error) {
      console.error('Failed to delete notification:', error);
    }
  };


  return (
    <div className="inbox-container">
      <h1 className="inbox-header">Inbox</h1>
      {notifications["notification_id"] && notifications["notification_id"].length > 0 ? (
        <div className="notifications-list">
          {notifications["notification_id"].map(notification => (
            <div className="notification-item" key={notification["id"]}>
              <h3 className="notification-title">{notification.message}</h3>
              <p className="notification-content">Type: {notification.notification_type}</p>
              {notification.notification_type == "invitation" && (
              <button className = "action-button" onClick={() =>  handleAcceptInvitation(notification) && handleDeleteNotification(notification.id,notification)}>Accept</button>
            )}
              <button className = "action-button" onClick={() => handleDeleteNotification(notification["id"])}>Delete</button>
            </div>
          ))}
        </div>
      ) : (
        <p className="no-notifications">No notifications found</p>
      )}
    </div>
  );
}

export default Inbox;
