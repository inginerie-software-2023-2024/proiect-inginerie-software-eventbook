import React, { useState, useEffect } from "react";
import EventSnippet from "./EventSnippet";
import "../styles/EventsFeed.css";
import EventFilter from "./EventFilters";

function EventsFeed() {
  const [events, setEvents] = useState([]);

  const fetchEvents = (filters) => {
    let queryParams = [];

    if (filters.title) {
      queryParams.push(`title=${encodeURIComponent(filters.title)}`);
    }
    if (filters.location) {
      queryParams.push(`location=${encodeURIComponent(filters.location)}`);
    }
    filters.tags.forEach((tag) => {
      if (tag) {
        queryParams.push(`tags=%23${encodeURIComponent(tag)}`);
      }
    });

    const queryString =
      queryParams.length > 0 ? `?${queryParams.join("&")}` : "";
    const url = `http://localhost:8080/events${queryString}`;

    fetch(url, {
      headers: { accept: "application/json" },
    })
      .then((response) => response.json())
      .then((data) => setEvents(data))
      .catch((error) => console.error("Error fetching data: ", error));
  };

  useEffect(() => {
    fetchEvents({ title: "", location: "", tags: [] });
  }, []);

  return (
    <>
      <div className="host-event-container">
        <p className="host-event-text">Host your event!</p>
        <button className="add-event-button">
          <span className="host-text-button">Host </span>
        </button>
      </div>
      <EventFilter onFilter={fetchEvents} />
      <div id="events-feed-container">
        {events.map((event) => (
          <EventSnippet key={event.id} event={event} />
        ))}
      </div>
    </>
  );
}

export default EventsFeed;
