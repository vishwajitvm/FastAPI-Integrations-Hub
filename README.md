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

├── app.py # Main Flask application
├── .env # Environment variables (client ID, secret, etc.)
├── requirements.txt # Python dependencies
├── templates/
│ └── login.html # Simple login page template
└── README.md # Project documentation

---

## ⚙️ Setup Instructions

### 1️⃣ Clone this repo

```bash
git clone https://github.com/vishwajitvm/Zoho-SSO-Login-with-Python--Flask-.git
cd zoho-flask-sso-poc

## 2️⃣ Install dependencies

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt


3️⃣ Run the app

python app.py

