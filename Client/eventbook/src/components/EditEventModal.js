import React, { useState } from "react";
import "../styles/EditEventModal.css";
import CloseIcon from "@mui/icons-material/Close";
import { useNavigate } from "react-router-dom";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { jwtDecode } from "jwt-decode";


function EditEventModal({ event, onClose, isEdit }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: event.title || "",
    tags: event.tags || [],
    description: event.description || "",
    start_time: event.start_time
      ? new Date(event.start_time * 1000).toISOString().slice(0, 16)
      : "",
    end_time: event.end_time
      ? new Date(event.end_time * 1000).toISOString().slice(0, 16)
      : "",
    location: event.location || "",
    public: event.public || false,
  });

  const availableTags = [
    "art",
    "bookclub",
    "business",
    "charity",
    "concert",
    "conference",
    "culture",
    "education",
    "family",
    "fashion",
    "festival",
    "fitness",
    "food",
    "gaming",
    "health",
    "movie",
    "music",
    "networking",
    "science",
    "sports",
    "travel",
    "workshop",
    "theather",
    "tech",
    "party",
    "meetup",
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    let finalValue = value;

    if (name === "public") {
      finalValue = value === "true";
    }

    setFormData((prev) => ({ ...prev, [name]: finalValue }));
  };

  const handleTagChange = (e) => {
    const selectedTags = Array.from(
      e.target.selectedOptions,
      (option) => option.value
    );
    setFormData((prev) => ({ ...prev, tags: selectedTags }));
  };

  const getUserIdFromToken = () => {
    const token = localStorage.getItem("authToken");
    if (token) {
      const decoded = jwtDecode(token);
      return decoded.id;
    }
    return null;
  };

  const sendEventCreateNotification = async () => {
    try {
      const updatedNotification = {
        content: "Registered successfully the event",
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
        throw new Error("Failed to send event register notification");
      }
    } catch (error) {
      console.error('Failed to send event register notification:', error);
    }
  };


  const sendEventUpdateNotification = async () => {
    try {
      const updatedNotification = {
        content: "Event has been updated.",
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
        throw new Error("Failed to send event update notification");
      }
    } catch (error) {
      console.error('Failed to send event update notification:', error);
    }
  };


  const handleSubmit = async (e) => {
    e.preventDefault();

    if (isEdit) {
      try {
        const payload = {
          title: formData.title,
          description: formData.description,
          location: formData.location,
          public: formData.public,
          ...(formData.start_time && {
            start_time: Math.floor(
              new Date(formData.start_time).getTime() / 1000
            ),
          }),
          ...(formData.end_time && {
            end_time: Math.floor(new Date(formData.end_time).getTime() / 1000),
          }),
          ...(formData.tags.length > 0 && { tags: formData.tags }),
        };
        const token = localStorage.getItem("authToken");
        const response = await fetch(
          `http://127.0.0.1:8080/events/${event.id}`,
          {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
              accept: "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(payload),
          }
        );
        const data = await response.json();
        if (!response.ok) {
          throw new Error(`${data.detail}`);
        }

        await sendEventUpdateNotification();

        toast.success("Event Edited Successfully", {
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
        toast.error("Error Editing Event", {
          position: "top-center",
          autoClose: 2000,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
        });
      }
    } else {
      try {
        const token = localStorage.getItem("authToken");

        const toUnixTimestamp = (dateString) => {
          const date = new Date(dateString);
          return isNaN(date.getTime())
            ? null
            : Math.floor(date.getTime() / 1000);
        };

        const params = {
          title: encodeURIComponent(formData.title),
          description: encodeURIComponent(formData.description),
          location: encodeURIComponent(formData.location),
          tags: formData.tags.map((tag) => encodeURIComponent("#" + tag)), // Prefix tags with '#'
          start_time: toUnixTimestamp(formData.start_time),
          end_time: toUnixTimestamp(formData.end_time),
          public: formData.public,
        };

        let queryString = `title=${params.title}&description=${params.description}&location=${params.location}`;
        params.tags.forEach((tag) => (queryString += `&tags=${tag}`));

        if (params.start_time)
          queryString += `&start_time=${params.start_time}`;
        if (params.end_time) queryString += `&end_time=${params.end_time}`;

        queryString += `&public=${params.public}`;

        const response = await fetch(
          `http://127.0.0.1:8080/events/register?${queryString}`,
          {
            method: "POST",
            headers: {
              accept: "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );

        const data = await response.json();
        if (!response.ok) {
          throw new Error(`${data.detail}`);
        }

        await sendEventCreateNotification();

        toast.success("Event Uploaded Successfully", {
          position: "top-center",
          autoClose: 2000,
          hideProgressBar: true,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
          progress: undefined,
        });

        setTimeout(() => {
          navigate("/refresh");
          setTimeout(() => {
            navigate(`/events/${data.id_event}`);
          }, 10);
        }, 2000);
      } catch (err) {
        console.error(err);
        toast.error(`Error Uploading Event: ${err.message}`, {});
      }
    }
  };

  const refreshPage = () => {
    navigate("/refresh");

    setTimeout(() => {
      navigate("/profile");
    }, 10);
  };

  return (
    <div className="edit-event-modal-container">
      <form className="edit-event-form" onSubmit={handleSubmit}>
        <ToastContainer />
        <button type="button" onClick={onClose} className="close-edit-event">
          <CloseIcon fontSize="large" />
        </button>
        <h2>{isEdit ? "Edit Event" : "Upload Event"}</h2>

        <label>Title:</label>
        <input
          type="text"
          name="title"
          value={formData.title}
          onChange={handleChange}
        />
        <label>Tags:</label>
        <select
          name="tags"
          onChange={handleTagChange}
          value={formData.tags}
          multiple
        >
          {availableTags.map((tag) => (
            <option key={tag} value={tag}>
              {tag}
            </option>
          ))}
        </select>
        <div className="selected-tags-container">
          {formData.tags.map((tag, index) => (
            <span key={index} className="selected-tag">
              {tag}
            </span>
          ))}
        </div>

        <label>Description:</label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
        ></textarea>

        <label>Start Time:</label>
        <input
          type="datetime-local"
          name="start_time"
          value={formData.start_time}
          onChange={handleChange}
        />

        <label>End Time:</label>
        <input
          type="datetime-local"
          name="end_time"
          value={formData.end_time}
          onChange={handleChange}
        />
        <label>Location:</label>
        <input
          type="text"
          name="location"
          value={formData.location}
          onChange={handleChange}
        />
        <div className="public-or-private">
          <label>Public:</label>
          <label>
            <input
              type="radio"
              name="public"
              value="true"
              checked={formData.public === true}
              onChange={handleChange}
            />
            Yes
          </label>
          <label>
            <input
              type="radio"
              name="public"
              value="false"
              checked={formData.public === false}
              onChange={handleChange}
            />
            No
          </label>
        </div>

        <button className="edit-form-submit" type="submit">
          Save Changes
        </button>
      </form>
    </div>
  );
}

export default EditEventModal;
