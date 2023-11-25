## Eventplanner

### Content
- [Introduction](#introduction)
- [Product statement-vision](#product-statement-and-vision)
- [Product features-functionalities](#product-features-and-functionalities)
- [Non-Functional requirements](#non-functional-requirements)
- [Product backlog](#product-backlog)
- [Project Roadmap](#project-roadmap)
- [Activity overview](#activity-overview)
- [User journey](#user-journey)
- [User story](#user-stories)
- [User persona](#user-persona)

#### Introduction

   The main purpose of this document is to provide a high level overview on the Eventplanner project, it's features and
it's main objective. 
   This project aims to provide the user with a comprehensive solution which simplifies the process of creating and 
attending to different events. The application integrates personalize features such as event creation, invitation, 
personal preferences, weather updates/situation and a personalized calendar.
   
The main objectives of the application are:
- Enhanced Collaboration for Organizers
     - Facilitate seamless collaboration among event organizers by providing features that enable easy sharing of event details and coordination.
     - Offer collaborative tools for multiple organizers to contribute to event planning, ensuring a unified and well-coordinated approach.
 - Efficient Communication Channels
     - Implement efficient communication channels within the application to foster better interaction between event organizers and attendees.
     - Provide real-time updates and messaging features to enhance communication regarding event details, changes, and important announcements.
 - Smart Resource Management
     - Assist organizers in optimizing resource allocation for events, including venue selection, budgeting, and logistics.
     - Integrate smart resource management tools to help organizers make informed decisions, maximizing the impact of their events.
- Seamless Integration with External Platforms
     - Ensure seamless integration with popular external platforms, such as social media and calendar applications.
     - Allow users to share events on social platforms effortlessly and sync event schedules with their existing calendars for a cohesive experience.
 - Accessibility and Inclusivity
     - Prioritize accessibility features to make the application inclusive for users with diverse needs and abilities.
     - Implement design and functionality considerations that cater to a wide range of users, promoting inclusivity in event participation.

#### Product statement and vision
   Eventplanner as an application came out as a solution due to multiple problems. Some of them would be fragmentation
of event planning and information across many individuals, a decentralized place for common information regarding event
discovery, lack of personalization in user experience and difficulties in event management.
   Our solution aims to solve these problems by creating a comprehensive, user-centric, centralized event management
application. The application will serve as main point in event management and planning.

#### Product features and functionalities
   As an all-in-one event planner and management solution, out application propose a large set of features and 
functionalities in order to provide a seamless and intuitive platform which caters to the large range of needs
of event organisers and attendees.
- Performance
  - Response Time
    - The application should achieve an average response time of less than 2 seconds for key user interactions, such as event creation, invitation sending, and RSVP tracking.
    - Specific actions, like loading event details or updating preferences, should have response times within milliseconds to ensure a snappy user experience.

  - Scalability
    - The system should maintain the specified response time even under a 50% increase in concurrent user traffic.
    - Performance testing will be conducted regularly to identify and address potential bottlenecks as user load grows.

- Database Scalability
  - The database architecture should scale horizontally to accommodate a growing volume of event data without compromising query response times.
  - The database system should efficiently handle CRUD operations, ensuring optimal performance for Create, Read, Update, and Delete actions.

- Usability
  - User Satisfaction (SLI)
    - Conduct regular usability surveys to gauge user satisfaction, aiming for a score of at least 85%.
    - Actively gather user feedback and implement iterative improvements to enhance overall usability.

  - Accessibility (SLO)
    - Maintain compliance with Web Content Accessibility Guidelines (WCAG), ensuring accessibility for users with diverse needs.
    - Conduct quarterly accessibility testing to verify ongoing adherence to standards.

- Scalability
  - User Traffic Increase (SLO)
    - The system should efficiently handle a 50% increase in user traffic without a proportional decrease in performance.
    - Employ load balancing, caching strategies, and horizontal scaling to distribute the increased load effectively.

- Compliance and Standards
  - GDPR Compliance (SLO)
    - Ensure full compliance with the General Data Protection Regulation (GDPR) standards.
    - Implement robust data protection measures, including user consent mechanisms, data encryption, and the right to erasure.
    - Conduct annual GDPR compliance audits to verify ongoing adherence.

- Database Operations
  - CRUD Functionality
    - The database system should support CRUD operations (Create, Read, Update, Delete) for efficient management of event-related data.
    - Data integrity and consistency should be maintained throughout all database transactions.

- Compatibility
  -  Operating System Compatibility (SLO)
    - Ensure seamless compatibility with the Windows operating system, optimizing the application for Windows-based devices and browsers.
    - Conduct bi-annual compatibility testing to address any potential issues related to Windows updates or changes.

#### Product backlog
   In order to have a clear overview of feature, task and requirement, based on importance and impact to project 
   success, a backlog list is necessary.
- User Account Management 
   - Registration and login functionality
   - Profile creation and editing
   - Password recovery
   - Event Creation and Management
   
- Interface for creating new events
   - Options to edit and delete events
   - Calendar integration for event scheduling
   - Venue Selection
   
- Database of venues with filters (location, capacity, etc.)
   - Venue booking functionality
   - Integration with maps for venue location
   - Invitations and Guest Management
   
- Sending electronic invitations
   - Tracking RSVPs
   - Managing guest lists

- Notification System 
   - Email and in-app notifications for event updates
   - Reminders for important dates and tasks
#### Project Roadmap
   In order to outline the key stages and have a milestone planning a project roadmap
diagram is recommended.

![project_roadmap.png](diagrams/project_roadmap.png)
#### Activity overview
   In order to have a better understanding of the flow an activity diagram is provided.The Activity Diagram provides 
   a visual representation of the workflow associated with the event management process within our application

   ![activity_diagram.png](diagrams/activity_diagram.png)

#### User Journey
   In order to provide a better image about user's journey, a user journey map diagram is essential. The User Journey 
   Map is a graphical illustration that captures the complete experience of a user, from initial contact with the 
   application through various stages of interaction to the final goal achievement.
  
 ![user_journey.svg](diagrams/user_journey.svg)

#### User-Stories
 - As an event organizer, I want to easily create events, so that I can share them with potential attendees.
 - As a user, I want to invite friends and colleagues to my events, so that I can organize gatherings efficiently.
 - As an invitee, I want to receive event invitations and respond to them, so that I can manage my attendance.
 - As a user, I want to set my personal preferences for events, so that the app can recommend events that interest me.
 - As a user, I want to view a list of upcoming events tailored to my interests,
so that I can decide which events to attend
 - As an event attendee, I want to receive weather updates for the events I plan to attend, 
so that I can prepare accordingly.
 - As a user, I want to synchronize my personal calendar with the app, so that I can manage my schedule effectively.
 - As a user, I want to receive customized notifications about events, so that I stay informed about any 
changes or updates.
 - As an event organizer, I want to receive feedback on my events, so that I can improve future events.

#### User Persona

To effectively design and develop the Event Management Application, it's crucial to have a clear understanding
of the typical users. Below is a detailed user persona that represents a segment of the
application's target audience:

   Persona: Emily Nguyen 
- Demographics:
  - Age: 29
  - Occupation: Marketing Manager
  - Location: Urban City
  - Education: Bachelor's degree in Marketing
  - Marital Status: Single

- Psychographics:
  - Lifestyle: Active social life, enjoys attending and organizing events.
  - Personality: Outgoing, organized, tech-savvy.
  - Values: Efficiency, connectivity, work-life balance.
  - Hobbies: Networking, traveling, music festivals.

- Technology Usage: 
  - Comfortable with technology and frequently uses mobile apps for social and professional purposes.
  - Prefers applications that are intuitive and save time.

- Goals and Motivations: 
  - To efficiently organize and manage professional and personal events.
  - To discover new events that align with her interests.
  - To maintain a balanced and organized schedule.
- Pain Points: 
  - Difficulty in finding events that match her interests.
  - Managing invitations and RSVPs across multiple platforms.
  - Keeping track of various events in her busy schedule.

- Interaction with the App: 
  - Uses the app to create and manage both professional networking events and personal gatherings.
  - Relies on the app for discovering new events, especially those related to her professional growth and personal interests.
  - Appreciates the personalized event recommendations and weather updates.
  - Values the integration with her personal calendar for better schedule management.

- How the App Helps Emily:
  - Event Creation and Management: Emily can easily create and manage her events, streamlining her planning process.
  - Personalized Recommendations: The app suggests events based on her preferences, helping her discover relevant professional and social gatherings.
  - Integrated Calendar: With the app syncing with her personal calendar, Emily can efficiently manage her schedule without conflicts.
  - Weather Updates: She can plan her event attire and logistics according to the weather forecasts provided by the app.

[//]: #(https://showme.redstarplugin.com/s/s:tkwtNwO8)