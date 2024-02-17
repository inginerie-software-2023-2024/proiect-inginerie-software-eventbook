import React, { useState, useEffect } from "react";
import CloseIcon from "@mui/icons-material/Close";
import { useNavigate } from "react-router-dom";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { jwtDecode } from "jwt-decode";
import "../styles/SentInvitationModal.css";
import FaceIcon from "@mui/icons-material/Face";


function SentInvitationModal({ event, onClose , participants}) {
    const [users, setUsers] = useState([]);
    const [selectedUser, setSelectedUser] = useState([]);
    const [currentUser, setCurrentUser] = useState(null); 

    useEffect(() => {
        const token = localStorage.getItem("authToken");
        if (token) {
            const decodedToken = jwtDecode(token);
            setCurrentUser(decodedToken); 
        }
    }, []);

    const sendInvitation = async (user) => {
        try {

            const token = localStorage.getItem("authToken");
            const response = await fetch("http://localhost:8080/invitations", {
                method: "POST",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`,
                },
                body: JSON.stringify({
                    end_user: user.id,
                    start_user: currentUser.id,
                    type: "event",
                    event_id: event.id,
                }),
            });

    
            if (!response.ok) {
                throw new Error("Failed to send invitation");
            }
    
            const data = await response.json();
            await sendInvitationNotification(user);
            console.log("Invitation sent successfully:", data);
            toast.success("Invitation sent successfully");
        } catch (error) {
            console.error("Failed to send invitation:", error);
            toast.error("Failed to send invitation");
        }
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
          return data; 
        } catch (error) {
          console.error("Failed to fetch participant details:", error);
          return null;
        }
      };

      const loadUsers = async () => {
        try {
            const token = localStorage.getItem("authToken");
            const response = await fetch("http://127.0.0.1:8080/users/all", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
              },
            });
    
            if (!response.ok) {
              throw new Error(`Error: ${response.statusText}`);
            }
    
            const data = await response.json();
            setUsers(data);
          } catch (error) {
            console.error("Failed to fetch users:", error);
          }
      };

      
    useEffect(() => {
        loadUsers();
    }, []);

    const getUserIdFromToken = () => {
        const token = localStorage.getItem("authToken");
        if (token) {
          const decoded = jwtDecode(token);
          return decoded.id;
        }
        return null;
      };
      
    const sendInvitationNotification = async (user) => {
        
        try {
          const updatedNotification = {
            content: `Someone invited you to participate at "${event.title}" event`,
            notification_type: "invitation",
            event_id: event.id,
          };
          console.log(event.id);
    
          const token = localStorage.getItem("authToken");
          const response = await fetch(`http://127.0.0.1:8080/notifications/${user.id}/notify?notification_type=${updatedNotification.notification_type}&content=${updatedNotification.content}&event_id=${updatedNotification.event_id}`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(updatedNotification),
          });
    
          if (!response.ok) {
            throw new Error("Failed to send invitation notification");
          }
        } catch (error) {
          console.error('Failed to send invitation notification:', error);
        }
      };
    return (
        <div className="edit-event-modal-container">
          <div className="modal-content">
            <span className="close" onClick={onClose}><CloseIcon /></span>
            <h2>Send Invitation</h2>
            <ul>
            {users.map(user => (
                <li key={user.id}>
                    <div className="user-info">
                    <FaceIcon />
                    <span>{user.username}</span>
                    {(!participants.map(p => p.id).includes(user.id)) && (
                        <button className="send-invite" onClick={()=> sendInvitation(user) && console.log(user)} >
                            Send
                        </button>
                    )} 
                    {(participants.map(p => p.id).includes(user.id)) && (
                        <button className="send-invite">
                            Already member
                        </button>
                    )}
                    </div>
                </li>
                ))}
            </ul>
          </div>
        </div>
      );
      
}

export default SentInvitationModal;
