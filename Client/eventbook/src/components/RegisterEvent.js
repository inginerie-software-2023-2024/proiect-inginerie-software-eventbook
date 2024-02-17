import React, { useState } from "react";
import Select from "react-select";
import "../styles/RegisterEventForm.css"; 
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const tagsList = [
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
  "tech",
  "travel",
  "workshop",
  "theater",
  "party",
];

function RegisterEventForm() {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    location: "",
    tags: [],
    startTime: "",
    endTime: "",
    isPublic: true,
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleTagSelectChange = (selectedOptions) => {
    const selectedTags = selectedOptions.map((option) => option.value);
    setFormData({ ...formData, tags: selectedTags });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const token = localStorage.getItem("authToken");
      if (!token) {
        throw new Error("User not logged in");
      }

      const response = await fetch("http://localhost:8080/events/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...formData,
          tags: formData.tags.map((tag) => `#${tag}`), // Prefixing tags with #
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Error registering event");
      }

      toast.success("Event registered successfully");
    } catch (err) {
      toast.error(`Error: ${err.message}`);
    }
  };

  const tagOptions = tagsList.map((tag) => ({ value: tag, label: tag }));

  return (
    <div id="register-event-modal">
      <form className="register-event-form" onSubmit={handleSubmit}>
        <ToastContainer />

        <h1>Register Event</h1>

        <label>Title:</label>
        <input
          type="text"
          name="title"
          value={formData.title}
          onChange={handleInputChange}
        />

        <label>Description:</label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleInputChange}
        />

        <label>Location:</label>
        <input
          type="text"
          name="location"
          value={formData.location}
          onChange={handleInputChange}
        />

        <label>Tags:</label>
        <Select
          isMulti
          name="tags"
          options={tagOptions}
          value={tagOptions.filter((option) =>
            formData.tags.includes(option.value)
          )}
          onChange={handleTagSelectChange}
        />

        <label>Start Time:</label>
        <input
          type="datetime-local"
          name="startTime"
          value={formData.startTime}
          onChange={handleInputChange}
        />

        <label>End Time:</label>
        <input
          type="datetime-local"
          name="endTime"
          value={formData.endTime}
          onChange={handleInputChange}
        />

        <label>
          <input
            type="checkbox"
            name="isPublic"
            checked={formData.isPublic}
            onChange={() =>
              setFormData({ ...formData, isPublic: !formData.isPublic })
            }
          />
          Public Event
        </label>

        <button type="submit">Register Event</button>
      </form>
    </div>
  );
}

export default RegisterEventForm;
