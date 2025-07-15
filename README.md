# 🚀 FastAPI-Integrations-Hub: Zoho APIs, SSO, WorkDrive, RAG & Chatbot

This project demonstrates a scalable, modular integration hub using **Python FastAPI**, designed to seamlessly incorporate multiple advanced features like **Zoho Single Sign-On (SSO)** (OAuth 2.0 & OpenID Connect), Zoho WorkDrive APIs, RAG (Retrieval-Augmented Generation), chatbot integrations, and future enterprise APIs — all under one unified architecture.

> ✅ Refactored using FastAPI routers for clean, maintainable, and scalable code — perfect for continuously evolving multi-feature use cases!

---

## 💡 Features

- ✅ Login with Zoho SSO (OAuth 2.0 + OpenID Connect)
- 🔑 Decode `id_token` (JWT) to extract user profile info (name, email, Zoho User ID)
- 🗂️ Access personal WorkDrive folders (My Folders)
- 👥 Access team folders (Team Folders)
- 🧠 Future support for RAG (retrieval-augmented generation) modules
- 🤖 Extendable chatbot integrations (LLMs, agent-based bots, etc.)
- 💼 Maintain user sessions with FastAPI (in-memory or future scalable storage)
- 🧩 Highly modular router-based structure for adding any number of APIs cleanly

---

## 🗂️ Project Structure

```
your_project/
├── main.py               # Main FastAPI app entry point
├── config.py            # Central configuration (env vars, API base URLs)
├── .env                 # Environment variables (client ID, secret, etc.)
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation (this file)
├── templates/
│   ├── login.html       # Login page template
├── routers/
│   ├── __init__.py
│   ├── zoho/
│   │   ├── __init__.py
│   │   ├── auth.py     # Auth routes (login, callback, logout)
│   │   ├── folders.py  # WorkDrive folder routes
│   │   └── zoho_client.py  # Zoho API helpers
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── rag_routes.py  # Retrieval-augmented generation logic
│   │   └── rag_utils.py
│   ├── chatbot/
│   │   ├── __init__.py
│   │   ├── chatbot_routes.py  # Chatbot endpoints
│   │   └── chatbot_utils.py
│   └── otherapi/
│       ├── __init__.py
│       ├── routes.py
│       └── utils.py
├── constants/
│   ├── __init__.py
│   ├── response_messages.py  # Centralized response messages
│   └── status_codes.py       # HTTP status codes
└── utils/
    ├── __init__.py
    └── shared.py     # Shared helpers
    └── zoho_folder_helpers.py     # Zoho api file itration common function
    
```

### 📁 Folder usage

- **routers/zoho/** — Zoho SSO and WorkDrive logic.
- **routers/rag/** — RAG-based modules (e.g., vector DB queries, knowledge retrieval).
- **routers/chatbot/** — AI chatbot integrations and agent logic.
- **routers/otherapi/** — additional APIs (placeholder for future integrations).
- **constants/** — central definitions for response messages and status codes.
- **utils/** — shared helpers and utilities across modules.

---

## 💡 How it works

1️⃣ User clicks **Login with Zoho** button.  
2️⃣ Redirected to Zoho OAuth page.  
3️⃣ User authenticates and grants consent.  
4️⃣ App exchanges code for tokens (`access_token`, `id_token`).  
5️⃣ `id_token` is decoded to get user profile.  
6️⃣ Session stored (initially in-memory, can be upgraded later).  
7️⃣ User gains access to features like:
   - ✅ My Folders
   - ✅ Team folders
   - 💬 Future: RAG-powered knowledge queries
   - 🤖 Future: Chatbot interactions
8️⃣ User can logout anytime.

---

## ✨ Future directions

- 🔒 JWT signature validation for production.
- 🗂️ Expand WorkDrive to include file upload and management.
- 🤖 Integrate advanced AI agent workflows.
- 🔎 Add RAG for contextual enterprise Q&A.
- 🌐 Integrate more SaaS or internal business APIs.

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone https://github.com/vishwajitvm/FastAPI-Integrations-Hub.git
cd FastAPI-Integrations-Hub
```

---

### 2️⃣ Create virtual environment & install dependencies

```bash
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

### 3️⃣ Add environment variables

Create a `.env` file in the root directory and paste:

```env
FLASK_SECRET_KEY=your_secret_key_here
ZOHO_CLIENT_ID=your_zoho_client_id_here
ZOHO_CLIENT_SECRET=your_zoho_client_secret_here
ZOHO_REDIRECT_URI=http://localhost:8000/callback
```

> ⚠️ Match your Zoho app redirect URI exactly.

---

### 4️⃣ Run the app

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Then open [http://localhost:8000/](http://localhost:8000/) in your browser.

---

## 🟢 Quick Bash Summary

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env and paste credentials

uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

---

.

## 📄 API Documentation
FastAPI automatically provides interactive and static API documentation out of the box!

### 1️⃣ Swagger UI URL
```bash
 http://localhost:8000/docs
 ```

- Interactive interface to explore and test your endpoints directly.

- Supports authentication flows, parameters, and request bodies.

- Ideal for developers and API testers.

### 2️⃣ ReDocURL
```bash
 http://localhost:8000/redoc
```
- Clean, well-structured static documentation view.

- Great for sharing with business or non-technical stakeholders to explain available APIs.

- Provides easy navigation and human-readable endpoint summaries.

.



> ### ⚡️ Additional Notes
No extra setup is needed — both docs are auto-generated from your FastAPI routers and docstrings.

> You can customize descriptions, summaries, and request/response schemas directly in your router files using standard FastAPI annotations.



---
## ✉️ Contact

Created by **Vishwait VM** — [vishwajitmall0@gmail.com](mailto:vishwajitmall0@gmail.com)

Feel free to reach out for questions, suggestions, or collaborations! 🚀

---

