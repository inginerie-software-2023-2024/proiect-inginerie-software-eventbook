import React, { useState, useEffect } from "react";
import EventSnippet from "./EventSnippet";
import "../styles/EventsFeed.css";
import EventFilter from "./EventFilters";
import EditEventModal from "./EditEventModal";

function EventsFeed() {
  const [events, setEvents] = useState([]);
  const [uploadingEvent, setUploadEvent] = useState(null);

  const openEditModal = (event) => {
    setUploadEvent(event);
  };

  const closeEditModal = () => {
    setUploadEvent(null);
  };

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
        <button className="add-event-button" onClick={openEditModal}>
          <span className="host-text-button">Host </span>
        </button>
      </div>
      <EventFilter onFilter={fetchEvents} />
      <div id="events-feed-container">
        {events.length > 0 ? (
          events.map((event) => <EventSnippet key={event.id} event={event} />)
        ) : (
          <p className="no-events-message">
            No events found. Try adjusting your filters!
          </p>
        )}
      </div>
      {uploadingEvent && (
        <EditEventModal
          event={uploadingEvent}
          onClose={closeEditModal}
          isEdit={false}
        />
      )}
    </>
  );
}

export default EventsFeed;
