# 🚀 Zoho SSO Login PoC using Flask 

This project demonstrates a scalable Proof of Concept (PoC) for integrating **Zoho Single Sign-On (SSO)** using OAuth 2.0 and OpenID Connect (OIDC) with Python Flask.

> ✅ Refactored using Flask Blueprints for clean, maintainable, and scalable code!

---

## 💡 Features

- ✅ Login with Zoho SSO (OAuth 2.0 + OpenID Connect)
- 🔑 Decode `id_token` (JWT) to extract user profile details (name, email, Zoho User ID)
- 🗂️ Access personal WorkDrive folders (My Folders)
- 👥 Access team folders (Team Folders)
- 💼 Maintain user sessions using Flask
- 🚪 Simple login & logout flow
- 🧩 Clean modular structure with Blueprints, easy to extend

---

## 🗂️ Project Structure

```
your_project/
├── app.py               # Main Flask app entry point
├── config.py            # Configuration (env vars, API base URLs)
├── .env                 # Environment variables (client ID, secret, etc.)
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation (this file)
├── templates/
│   ├── login.html
│   └── home.html (optional)
├── blueprints/
│   ├── __init__.py
│   ├── auth.py         # Auth routes (login, callback, logout)
│   └── folders.py      # Routes for My Folders and Team Folders
└── utils/
    ├── __init__.py
    └── zoho_client.py  # Helper functions for Zoho API
```

---

## 💡 How it works (flow)

1️⃣ User clicks **Login with Zoho** button.  
2️⃣ Redirects to Zoho OAuth authorization page.  
3️⃣ User logs in and consents.  
4️⃣ Zoho redirects back with a code.  
5️⃣ App exchanges code for access token and `id_token`.  
6️⃣ `id_token` is decoded to get user profile (name, email, Zoho user ID).  
7️⃣ User session is created, allowing access to:
   - ✅ My Folders
   - ✅ Team folders
8️⃣ User can logout anytime to clear session.

---

## ✨ Extending further

- 🔒 Add JWT signature verification (for production).
- 💬 Fetch detailed WorkDrive file metadata or preview links.
- 📁 Add upload, move, or delete operations on WorkDrive.
- 🧑‍💼 Add roles & user management logic.

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone https://github.com/vishwajitvm/Zoho-SSO-Login-with-Python--Flask-.git
cd Zoho-SSO-Login-with-Python--Flask-
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

> ⚠️ Make sure your redirect URI matches exactly what you configured in your Zoho app.

---

### 4️⃣ Run the app

```bash
python app.py
```

Then open [http://localhost:8000/](http://localhost:8000/) in your browser.

---

## 🟢 Quick Bash Summary

```bash
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env and paste:
# FLASK_SECRET_KEY=your_secret_key_here
# ZOHO_CLIENT_ID=your_zoho_client_id_here
# ZOHO_CLIENT_SECRET=your_zoho_client_secret_here
# ZOHO_REDIRECT_URI=http://localhost:8000/callback

python app.py
```

---

## ✉️ Contact

Created by **Vishwait VM** — [vishwajitmall0@gmail.com](mailto:vishwajitmall0@gmail.com)

Feel free to reach out for questions, suggestions, or collaboration! 🚀

---
