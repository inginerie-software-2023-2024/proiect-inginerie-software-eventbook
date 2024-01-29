import React, { useState, useEffect } from "react";
import "../styles/EditProfile.css";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { useNavigate } from "react-router-dom";
import "../styles/EditProfile.css";
import CloseIcon from "@mui/icons-material/Close";

function EditProfile({ show, onClose, userDetails }) {
  const navigate = useNavigate();
  const [email, setEmail] = useState(userDetails.email);
  const [password, setPassword] = useState("");
  const [editForm, setEditForm] = useState({
    username: userDetails.username || "",
    email: userDetails.email || "",
    password: "",
  });

  const [isFormChanged, setIsFormChanged] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    setEditForm({
      username: userDetails.username || "",
      email: userDetails.email || "",
      password: "",
    });
    setEmail(userDetails.email || "");
  }, [userDetails]);

  useEffect(() => {
    const isChanged =
      editForm.username !== userDetails.username ||
      editForm.email !== userDetails.email ||
      editForm.password !== "";
    setIsFormChanged(isChanged);
  }, [editForm, userDetails]);

  if (!show) {
    return null;
  }

  const refreshPage = () => {
    navigate("/refresh");

    setTimeout(() => {
      navigate(-1);
    }, 10);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setEditForm({ ...editForm, [name]: value });
  };

  const isPasswordValid = (password) => {
    if (password === "") {
      return true;
    }
    let errors = [];
    if (!/(?=.*[a-z])/.test(password)) {
      errors.push("Password must contain at least one lowercase letter.");
    }
    if (!/(?=.*[A-Z])/.test(password)) {
      errors.push("Password must contain at least one uppercase letter.");
    }
    if (!/(?=.*\d)/.test(password)) {
      errors.push("Password must contain at least one digit.");
    }
    if (errors.length > 0) {
      setError(errors.join("\n"));
      return false;
    }
    return true;
  };

  const isEmailValid = (email) => {
    setError("");

    const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(email)) {
      setError("Please enter a valid email address.");
      return false;
    }

    return true;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    let errorMessages = [];

    // Validate email
    const emailError = isEmailValid(email);
    if (!emailError) {
      errorMessages.push(emailError);
    }

    // Validate password
    if (editForm.password !== "") {
      const passwordErrors = isPasswordValid(editForm.password);
      errorMessages = errorMessages.concat(passwordErrors);
    }

    if (errorMessages.length > 0) {
      console.log(errorMessages.join("\n"));
      setError(errorMessages.join("\n"));
    } else {
      setError("");
      UpdateUserDetails();
    }
  };

  const UpdateUserDetails = async () => {
    const token = localStorage.getItem("authToken");
    try {
      const password = editForm.password ?? "";
      if (!token) {
        throw new Error("User not logged in");
      }

      const response = await fetch("http://127.0.0.1:8080/users/update", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          username: editForm.username,
          email: email,
          password: password,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(`${data.detail}`);
      }
      toast.success("Updated successfully", {
        position: "top-center",
        autoClose: 2000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
      setTimeout(() => {
        refreshPage();
      }, 2000);
    } catch (err) {
      setError(err.message);
    }
  };

  const isButtonDisabled =
    !isFormChanged ||
    (!editForm.username && !editForm.email && !editForm.password);

  return (
    <div id="edit-profile-modal">
      <form className="edit-profile-form" onSubmit={handleSubmit}>
        <ToastContainer />
        <button id="close" onClick={onClose}>
          <CloseIcon fontSize="large" />
        </button>

        <h1 id="update-header">Update Details</h1>
        <div id="errors">
          {error.split("\n").map((line, index) => (
            <p key={index}>{line}</p>
          ))}
        </div>
        <label>Username:</label>
        <input
          type="text"
          name="username"
          value={editForm.username}
          onChange={handleInputChange}
        />
        <label>Email:</label>
        <input
          type="email"
          name="email"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            handleInputChange(e);
          }}
          onBlur={() => isEmailValid(email)}
        />
        <label>Password:</label>
        <input
          type="password"
          name="password"
          value={editForm.password}
          onChange={(e) => {
            setPassword(e.target.value);
            handleInputChange(e);
          }}
          onBlur={() => isPasswordValid(password)}
        />
        <button id="update-button" type="submit" disabled={isButtonDisabled}>
          Update Details
        </button>
      </form>
    </div>
  );
}

export default EditProfile;
