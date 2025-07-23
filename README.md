# EmailAgent Web Application

## Introduction

EmailAgent is a sophisticated web application designed to streamline email management by integrating deeply with Gmail. Built using Django on the backend and JavaScript on the frontend, this application offers users a seamless experience to sync, view, send, reply, and categorize emails. Leveraging asynchronous processing and AI-powered agents, EmailAgent intelligently categorizes incoming emails and can generate suggested replies, enhancing productivity and email handling efficiency. The application features a clean, professional interface with multiple views for inbox management, individual email review, and agent-generated responses.

## 🎥 Demo Videos

- [📺 Demo Part 1 – Core Functionality (Inbox, Sync, Replies)](https://www.youtube.com/watch?v=3e_KJy-Ae0g)
- [📺 Demo Part 2 – AI Agent and Chat-Based Interface](https://www.youtube.com/watch?v=gzn7Ww1XwXw)

These videos walk through the key features of EmailAgent, including Gmail sync, secure login, AI-generated replies, and asynchronous background processing.

## Distinctiveness and Complexity

EmailAgent stands apart from typical course projects by focusing on advanced email management rather than social networking or e-commerce functionalities. Unlike prior projects, it integrates directly with the Gmail API to synchronize emails in real-time, maintaining a local database of contacts and messages with detailed metadata. The complexity of this project is evident in several key areas:

- **Gmail API Integration:** The application handles both initial and incremental synchronization of Gmail messages, managing message states, threading, and metadata with precision. A challenging aspect was managing and refreshing access tokens, which expire every hour. I implemented efficient functions to check token validity and refresh tokens as needed, ensuring seamless API access.

- **AI Agent Integration:** EmailAgent incorporates asynchronous AI agents that analyze email content to categorize messages and generate context-aware reply suggestions, a feature not commonly found in standard projects.

- **Asynchronous Processing:** The use of Django async views and background processing ensures responsive user interactions even during complex email processing tasks.

- **Comprehensive Email Management:** The system supports sending, replying, deleting, and reviewing emails, with detailed tracking of read, replied, and agent-reviewed statuses.

- **Security and User Management:** Leveraging Django’s authentication system, the app ensures secure access and user-specific data handling. I used django-allauth to set up Google authentication and populated my own database using RESTful API calls in the signals.py file. Styling the allauth login and social app pages was initially challenging, but after consulting documentation, I was able to customize the appearance to my satisfaction.

This combination of real-world API integration, AI-driven automation, and asynchronous design makes EmailAgent a uniquely challenging and feature-rich project that exceeds the complexity and distinctiveness requirements of the course.

## File Descriptions

- **emailagent/agentsworkflow/models.py:** Defines Django models for Gmail contacts, incoming emails with extensive metadata, and synchronization state tracking. Designing the IncomingEmails model was particularly challenging, as I initially separated incoming and outgoing emails but later realized emails can be both depending on the user’s perspective. This led to a unified model with an `is_outgoing` attribute. The GmailSyncState model was essential for efficient syncing.

- **emailagent/emailagent/views.py:** Contains Django views handling email synchronization, inbox display, individual email retrieval, sending and replying to emails, and AI agent interaction. Handling database queries in async environments was difficult, but I resolved this using `sync_to_async` and `async_to_sync` decorators.

- **emailagent/static/javascript/send_mails.js:** Frontend JavaScript managing user interactions for sending replies asynchronously via API calls. This script interacts with backend APIs to send emails and update the UI accordingly.

- **emailagent/static/css/**: Contains CSS files defining the application's visual layout and styling. The layout uses flexible box models for adaptable UI.

- **emailagent/emailagent/templates/**: HTML templates rendering the user interface for inbox, email details, agent responses, and other pages.

- **emailagent/agentsworkflow/utils.py:** Utility functions supporting email parsing, batching, and AI agent communication. This file contains core agent logic, including data parsing and context preparation.

- **emailagent/authentication/**: Django app managing user authentication, signals, and related utilities.

- **emailagent/manage.py:** Django project management script.

## How to Run

1. **Set up a Python virtual environment:**

   ```bash
   python -m venv venv
   source venv/Scripts/activate   # On Windows
   source venv/bin/activate       # On Unix or MacOS
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Apply database migrations:**

   ```bash
   python manage.py migrate
   ```

4. **Create a superuser (optional, for admin access):**

   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server:**

   ```bash
   python manage.py runserver
   ```

6. **Access the application:**

   Open your browser and navigate to `http://localhost:8000/`.

7. **Additional setup:**

   - Configure Gmail API credentials and OAuth for user authentication and email access.
   - Ensure environment variables or settings for Gmail API keys are properly set.

## Additional Information

- The project uses Django’s built-in authentication system to manage users securely.
- AI agents are integrated asynchronously to analyze and respond to emails, improving user productivity.
- The frontend uses JavaScript to provide interactive features such as sending replies without page reloads.
- While the CSS uses flexible layouts, further enhancements for mobile responsiveness can be added.
- The project requires Python packages listed in `requirements.txt`.
- The application is designed to be extensible, allowing future improvements such as enhanced UI responsiveness, additional AI capabilities, and expanded email management features.

---
