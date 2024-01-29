import React from "react";

function StrangerEvent({ event }) {
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
    </div>
  );
}

export default StrangerEvent;
