import React, { useState, useEffect } from "react";
import "../styles/Discover.css";
import UserCard from "./UserCard";

function Discover() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    const fetchUsers = async () => {
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

    fetchUsers();
  }, []);
  return (
    <div className="discover-container">
      <h1 className="discover-header">Discover Users</h1>
      {users.length > 0 ? (
        <div className="users-grid">
          {users.map((user, index) => (
            <UserCard key={index} user={user} />
          ))}
        </div>
      ) : (
        <p>No other users</p>
      )}
    </div>
  );
}

export default Discover;
