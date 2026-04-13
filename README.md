# 🦉 HootsChallenge  (Math & Nature Science)

An interactive web application designed to help children practice basic math and nature science concepts through progressive difficulty levels.

The app includes user authentication, progress tracking, and dynamically generated quiz questions using an external Trivia API.

---

##  Live Demo
  https://hootschallenge.onrender.com
<img width="976" height="539" alt="Screenshot 2026-04-13 at 11 39 45" src="https://github.com/user-attachments/assets/9adf23a5-dcba-4f18-ae6b-e3bca37ba8e2" />
<img width="1351" height="655" alt="Screenshot 2026-04-13 at 11 39 32" src="https://github.com/user-attachments/assets/0a42aedc-e0f8-49b5-8024-7107ecdb98d4" />
<img width="1346" height="646" alt="Screenshot 2026-04-13 at 11 39 11" src="https://github.com/user-attachments/assets/8bacfacc-2dee-432c-a1a4-0e7499ebf828" />
<img width="964" height="649" alt="Screenshot 2026-04-13 at 11 38 10" src="https://github.com/user-attachments/assets/1892301f-78aa-4126-85a8-19a982c1218f" />

 
---

## ✨ Features

-  Practice basic math skills  
-  Learn nature science concepts through quiz questions  
-  User authentication (login system)  
-  Progress tracking stored in a database  
-  Difficulty levels (currently 3 levels)  
-  Dynamic questions fetched from an external Trivia API   

---

##  Tech Stack

- **Backend:** Flask (Python)  
- **Database:** PostgreSQL  
- **ORM:** Flask-SQLAlchemy  
- **Authentication:** Werkzeug  
- **API Integration:** External Trivia API (via `requests`)  

---

##  Architecture

Client (Browser) → Flask Backend → PostgreSQL Database  
                              ↘ External Trivia API  

---

##  Requirements

All dependencies are listed in `requirements.txt`.

Install them with:

```bash
pip install -r requirements.txt
