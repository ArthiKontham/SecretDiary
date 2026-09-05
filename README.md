
# Secret Diary

A secure digital diary application that allows users to create, edit and organize personal diary entries.

## Preview

![Secret Diary](sd.jpg)

# Secret Diary

A Flask-based personal diary web application that allows users to securely create accounts, log in, select personalized seasonal themes, choose a year, month and day, write diary entries, save reminders, and perform calculations. The application uses Supabase for cloud database storage and can be deployed on Vercel.

---

## 1. Project Overview

Secret Diary is a web-based digital diary designed to provide users with a private and organized space to record their daily thoughts and activities.

The application combines diary management with useful features such as:

- User registration and login
- Password protection
- Seasonal diary themes
- Year, month and day selection
- Daily diary entries
- Previous entry viewing
- Reminder management
- Quick calculations
- Account viewing
- Cloud database storage using Supabase
- Vercel deployment support
- Local development support

The application follows a simple navigation flow so that users can select their preferred theme and date before writing a diary entry.

---

## 2. Main Objective

The main objective of Secret Diary is to provide a simple and organized digital platform where users can:

1. Create an account.
2. Log in securely.
3. Select a diary theme.
4. Select a year.
5. Select a month.
6. Select a day.
7. Write and save a diary entry.
8. View previous entries.
9. Set reminders.
10. View saved reminders.
11. Perform calculations.
12. Store data using a cloud database.

---

## 3. Technologies Used

### Backend

- Python
- Flask
- Werkzeug Security
- Requests

### Frontend

- HTML5
- CSS3
- JavaScript
- Jinja2 Templates

### Database

- Supabase
- PostgreSQL database through Supabase REST API

### Deployment

- Vercel
- Vercel Python Runtime

### Development Tools

- Visual Studio Code
- Git
- GitHub

---

## 4. Application Architecture

The application follows a client-server architecture.

```text
User
 |
 v
Web Browser
 |
 v
Flask Application
 |
 +--------------------+
 |                    |
 v                    v
HTML/CSS/JavaScript   Flask Routes
                         |
                         v
                  Authentication
                         |
                         v
                    Data Storage
                    /          \
                   /            \
                  v              v
          Supabase Database   Local Files
