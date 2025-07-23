# EmailAgent Web Application

## Introduction

EmailAgent is a sophisticated web application designed to streamline email management by integrating deeply with Gmail. Built using Django on the backend and JavaScript on the frontend, this application offers users a seamless experience to sync, view, send, reply, and categorize emails. Leveraging asynchronous processing and AI-powered agents, EmailAgent intelligently categorizes incoming emails and can generate suggested replies, enhancing productivity and email handling efficiency. The application features a clean, professional interface with multiple views for inbox management, individual email review, and agent-generated responses.

## 🎥 Demo Videos

- [📺 Demo Part 1 – Core Functionality (Inbox, Sync, Replies)](https://www.youtube.com/watch?v=3e_KJy-Ae0g)
- [📺 Demo Part 2 – AI Agent and Chat-Based Interface](https://www.youtube.com/watch?v=gzn7Ww1XwXw)

These videos walk through the key features of EmailAgent, including Gmail sync, secure login, AI-generated replies, and asynchronous background processing.


## Distinctiveness and Complexity

EmailAgent stands apart from typical course projects by focusing on advanced email management rather than social networking or e-commerce functionalities. Unlike prior projects, it integrates directly with the Gmail API to synchronize emails in real-time, maintaining a local database of contacts and messages with detailed metadata. The complexity of this project is evident in several key areas:

- **Gmail API Integration:** The application handles both initial and incremental synchronization of Gmail messages, managing message states, threading, and metadata with precision.
- **AI Agent Integration:** EmailAgent incorporates asynchronous AI agents that analyze email content to categorize messages and generate context-aware reply suggestions, a feature not commonly found in standard projects.
- **Asynchronous Processing:** The use of Django async views and background processing ensures responsive user interactions even during complex email processing tasks.
- **Comprehensive Email Management:** The system supports sending, replying, deleting, and reviewing emails, with detailed tracking of read, replied, and agent-reviewed statuses.
- **Security and User Management:** Leveraging Django’s authentication system, the app ensures secure access and user-specific data handling.

This combination of real-world API integration, AI-driven automation, and asynchronous design makes EmailAgent a uniquely challenging and feature-rich project that exceeds the complexity and distinctiveness requirements of the course.

## File Descriptions

- **emailagent/agentsworkflow/models.py:** Defines Django models for Gmail contacts, incoming emails with extensive metadata, and synchronization state tracking.
- **emailagent/emailagent/views.py:** Contains Django views handling email synchronization, inbox display, individual email retrieval, sending and replying to emails, and AI agent interaction.
- **emailagent/static/javascript/send_mails.js:** Frontend JavaScript managing user interactions for sending replies asynchronously via API calls.
- **emailagent/static/css/**: Contains CSS files defining the application's visual layout and styling. While explicit media queries are limited, the layout uses flexible box models for adaptable UI.
- **emailagent/emailagent/templates/**: HTML templates rendering the user interface for inbox, email details, agent responses, and other pages.
- **emailagent/agentsworkflow/utils.py:** Utility functions supporting email parsing, batching, and AI agent communication.
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
- The project requires Python packages.
- The application is designed to be extensible, allowing future improvements such as enhanced UI responsiveness, additional AI capabilities, and expanded email management features.

---

This README provides a comprehensive overview of EmailAgent, demonstrating its distinctiveness and complexity relative to other course projects. It documents the project structure, setup instructions, and key features to assist users and staff in understanding and evaluating the application.
