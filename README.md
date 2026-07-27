# 🏥 Clinic Management System

A comprehensive web application for managing a medical clinic's operations, including patient booking, appointment management, and administrative dashboard.

## 📋 Project Overview

This is a complete clinic management system built with Flask that allows:
- **Patients** to book appointments online
- **Administrators** to manage appointments, patients, and prescriptions
- **Healthcare providers** to view and update patient information

### Key Features
- ✅ Online appointment booking system
- ✅ Patient registration and login
- ✅ Admin dashboard with analytics
- ✅ Appointment management
- ✅ Patient records management
- ✅ Prescription management
- ✅ Lab test management
- ✅ Contact form
- ✅ Responsive design

---

## 🚀 Technology Stack

| Technology | Purpose |
|------------|---------|
| **Flask** | Python web framework |
| **SQLite** | Database |
| **HTML/CSS** | Frontend templates |
| **JavaScript** | Client-side interactions |
| **Render** | Deployment platform |

---
## 📁 Project Structure
clinic-website/
├── app.py # Main Flask application
├── requirements.txt # Python dependencies
├── Procfile # Render deployment config
├── .gitignore # Git ignore rules
├── templates/ # HTML templates
│ ├── base.html # Base layout template
│ ├── index.html # Home page
│ ├── about.html # About page
│ ├── contact.html # Contact page
│ ├── services.html # Services page
│ ├── book.html # Appointment booking
│ ├── confirmation.html # Booking confirmation
│ ├── patient_login.html
│ ├── patient_register.html
│ ├── patient_dashboard.html
│ ├── patient_book.html
│ ├── admin_login.html
│ ├── admin_dashboard.html
│ ├── admin_appointments.html
│ ├── admin_patients.html
│ ├── admin_prescriptions.html
│ ├── admin_lab_tests.html
│ ├── admin_messages.html
│ ├── admin_analytics.html
│ └── admin_upcoming.html
├── static/ # Static files
│ ├── css/
│ │ └── cinematic.css
│ ├── js/
│ │ └── gradient-bg.js
│ ├── favicon.ico
│ └── img/
│ ├── logo.png
│ ├── hero-bg.jpg
│ └── ... (other images)
├── create-favicon.py # Favicon generator script
├── create-images.py # Image optimization script
└── migrate.py # Database migration script

---

## 💻 Local Development Setup

### Prerequisites
- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/jenenhasan/clinic-website.git
   cd clinic-website