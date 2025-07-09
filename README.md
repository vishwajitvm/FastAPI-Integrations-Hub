# 🚀 Zoho SSO Login PoC using Flask

This project demonstrates a simple Proof of Concept (PoC) for integrating **Zoho Single Sign-On (SSO)** using OAuth 2.0 and OpenID Connect (OIDC) with Python Flask.

---

## 💡 Features

- Login using Zoho SSO (OAuth 2.0 & OIDC)
- Fetch and decode `id_token` (JWT) to extract user profile info
- Maintain user session using Flask
- Simple login & logout flow
- Easily extendable to include User Info API and JWT signature verification

---

## 🗂️ Project Structure

├── app.py # Main Flask application\
├── .env # Environment variables (client ID, secret, etc.)\
├── requirements.txt # Python dependencies\
├── templates/\
│ └── login.html # Simple login page template\
└── README.md # Project documentation\

---

## ⚙️ Setup Instructions

### 1️⃣ Clone this repo

```bash
git clone https://github.com/vishwajitvm/Zoho-SSO-Login-with-Python--Flask-.git
```

## 2️⃣ Install dependencies
- python -m venv venv

- source venv/bin/activate  # On Windows: venv\Scripts\activate
- pip install -r requirements.txt


## 3️⃣ Run the app

```bash
 python app.py
```

---
## 💡 Features

- ✅ **Login with Zoho SSO (OAuth 2.0 + OpenID Connect)** — authenticate users securely using Zoho’s single sign-on flow.
- 🔑 **Fetch and decode `id_token` (JWT)** — extract user profile details (name, email, Zoho User ID) directly from the token.
- 🗂️ **Access personal WorkDrive folders** — list files and folders from the user's **My Folders** area in Zoho WorkDrive.
- 👥 **Access team folders** — view all team folders and their details in Zoho WorkDrive (supports listing folders inside each team).
- 💼 **Maintain user sessions** — keep users logged in using Flask sessions and easily manage logout.
- ⚡ **Extendable to other Zoho APIs** — can be expanded to interact with Zoho CRM, Mail, and other Zoho services.
- 🚪 **Simple login & logout flow** — intuitive and minimal setup to understand core authentication and file listing flow.
- 🧾 **Beautifully formatted JSON debugging** — prints raw Zoho API responses in a clean, indented format for easy inspection during development.

---

## ✉️ Contact

Created by **Vishwait VM** — [vishwajitmall0@gmail.com](mailto:vishwajitmall0@gmail.com)

Feel free to reach out for any questions, suggestions, or collaboration!

