# ML-Powered Employee Motivation & Productivity Tracker

## Overview
A full-stack Django web application to track employee attendance, manage tasks, and generate AI-driven performance insights using Scikit-Learn KMeans clustering.

## Prerequisites
- Python 3.10+
- MySQL Server Installation

## Setup Instructions

1. **Install Virtual Environment and Dependencies**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Configure Database**
   - Open your MySQL Server and enter:
     `CREATE DATABASE productivity_db;`
   - Update `d:\new_program\tracker_project\settings.py` with your MySQL `USER` and `PASSWORD`.

3. **Database Migrations**
   ```bash
   python manage.py makemigrations tracker_app
   python manage.py migrate
   ```

4. **Create Superuser (First Admin)**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to add the admin name, email, and password.

5. **Run the Application**
   ```bash
   python manage.py runserver
   ```
   Access the app at `http://127.0.0.1:8000/`. You can log in as Admin using the superuser created above to manage your employees.
