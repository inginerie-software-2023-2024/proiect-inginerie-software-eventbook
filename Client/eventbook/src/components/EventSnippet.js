import image1 from "../assets/events_pictures/1.jpg";
import image2 from "../assets/events_pictures/2.jpg";
import image3 from "../assets/events_pictures/3.jpg";
import image4 from "../assets/events_pictures/4.jpg";
import image5 from "../assets/events_pictures/5.jpg";
import LocationOnIcon from "@mui/icons-material/LocationOn";
import "../styles/EventSnippet.css";
import { Link } from "react-router-dom";

function EventSnippet({ event }) {
  const images = [image1, image2, image3, image4, image5];
  const randomImage = images[Math.floor(Math.random() * images.length)];

  return (
    <Link to={`/events/${event.id}`} className="event-link">
      <div className="event-card feed-card">
        <div className="event-details-container contents">
          <img src={randomImage} alt="Event" className="event-image" />
          <div className="details-container">
            <h3 id="event-title">{event.title}</h3>
            <div className="event-details-subcontainer">
              <p id="event-description">{event.description}</p>
              <p id="event-date">{event.date}</p>
              <div className="location-container">
                <LocationOnIcon className="location-icon" />
                <p id="event-location">{event.location}</p>
              </div>
              <div id="tag-list">
                {event.tags.map((tag, index) => (
                  <span key={index} className="event-tag">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}

export default EventSnippet;
