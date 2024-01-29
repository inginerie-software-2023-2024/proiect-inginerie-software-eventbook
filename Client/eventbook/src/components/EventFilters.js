import React, { useState } from "react";
import "../styles/FilterForm.css";

const tags = [
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

function EventFilter({ onFilter }) {
  const [title, setTitle] = useState("");
  const [location, setLocation] = useState("");
  const [selectedTags, setSelectedTags] = useState([]);

  const handleTagChange = (tag) => {
    if (selectedTags.includes(tag)) {
      setSelectedTags(selectedTags.filter((t) => t !== tag));
    } else {
      setSelectedTags([...selectedTags, tag]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onFilter({ title, location, tags: selectedTags });
  };

  return (
    <form className="filter-form" onSubmit={handleSubmit}>
      <input
        className="filter-input"
        type="text"
        placeholder="Search by title..."
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <input
        className="filter-input"
        type="text"
        placeholder="Search by location..."
        value={location}
        onChange={(e) => setLocation(e.target.value)}
      />
      <div className="tags-grid">
        {tags.map((tag) => (
          <label key={tag} className="tag-item">
            <input
              type="checkbox"
              checked={selectedTags.includes(tag)}
              onChange={() => handleTagChange(tag)}
              className="custom-checkbox"
            />
            <span className="checkbox-style"></span> {}
            {tag}
          </label>
        ))}
      </div>
      <button className="filter-button" type="submit">
        <span className="filter-button-text">Filter</span>
      </button>
    </form>
  );
}

export default EventFilter;
