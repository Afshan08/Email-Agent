# 📬 EmailAgent

**EmailAgent** is a secure, AI-powered web application that helps users manage and reply to their emails intelligently. It integrates with Gmail using OAuth2 and lets users interact with their inbox through a smart, chat-based interface powered by OpenAI's Agent SDK.

The core goal is to **classify emails**, **identify important messages**, and **generate meaningful, personalized replies** that match the user’s writing style — all while keeping **user privacy and security** at the center.

---

## 🚀 Features

- 🔐 **Secure Gmail Authentication** via OAuth2 using Django Allauth
- 🤖 **OpenAI Agent SDK** integration to generate intelligent replies
- 📊 **Email Classification** using persona categories (e.g., Professional, Personal, Newsletters, etc.)
- 💬 **Chat Interface** to converse with your inbox
- 🔐 **No raw content stored** — only encrypted metadata is stored
- 🧠 **Context-aware replies** trained from your sent email writing patterns
- 🧪 **Token refresh mechanism** to handle expired access
- 🔄 Built-in **reply generator**, **send mail** function, and **watch history**

---

## 🧠 Tech Stack

| Layer         | Technologies Used                                      |
|---------------|--------------------------------------------------------|
| 💻 Backend     | Python, Django (with Django Allauth), SQLite          |
| ⚙️ Async Engine | `asyncio`, `asgiref`, Django async views              |
| 🧠 AI Layer     | OpenAI Agent SDK (Runner, Tool, Guardrails)          |
| 🔐 Security     | Gmail OAuth2, Token Refresh, Email Encryption (Fernet) |
| 🌐 Frontend    | HTML, Tailwind CSS, Vanilla JS, Chat UI (Custom)      |
| 🧪 Testing      | Custom scripts and prompt testing                     |
| 🐳 DevOps       | Docker (planned), Git for version control             |

---


---

## 🛡️ Privacy-first Approach

- ✅ User emails are **not stored** in the raw format
- ✅ Only **essential encrypted metadata** is saved
- ✅ Users **own their API access**; app avoids centralizing sensitive scopes

---

## 🏗️ Upcoming Plans

- [ ] Outlook integration
- [ ] Fully containerized setup with Docker
- [ ] Admin dashboard to manage access tokens and analytics
- [ ] More advanced email analysis tools (e.g., tone detection, summarization)

---

## 📣 How to Use

1. Clone the repo:
   ```bash
   git clone https://github.com/Afshan08/EmailAgent.git
   cd EmailAgent

👩‍💻 Built with ❤️ by Afshan Afridi
