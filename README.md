# About CareerSphere
CareerSphere is a modern and professional job portal designed to connect job seekers with employers. The platform allows employers to post job listings and review applications, while job seekers can browse job openings, apply, and track their application status.

The website features a clean, responsive design with a user-friendly interface to ensure a seamless experience for all users.

# Features
User Authentication: Secure login and registration for both job seekers and employers.

Job Listings: Employers can post new job openings with details like title, company, description, salary, and location.

Job Search: Job seekers can search for jobs by title, company, location, and category.

Application Management: Job seekers can apply for jobs and track the status of their applications.

Employer Dashboard: Employers can view their posted jobs and manage applications from candidates.

Responsive Design: The website is built with Bootstrap 5, ensuring it looks great on any device.

# Tech Stack
Client-Side:

HTML5

CSS3 (with Bootstrap 5)

JavaScript


Server-Side:

Flask: Python-based micro-framework for the web application.

SQLAlchemy: ORM (Object-Relational Mapper) for database interactions.

PostgreSQL: Production-grade database hosted on Aiven.

psycopg2-binary: PostgreSQL adapter for Python.

gunicorn: A production-ready WSGI HTTP server to run the application.

# Getting Started
Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

 # Prerequisites
Python 3.8 or higher

pip (Python package installer)

venv (Python virtual environment)

# Installation
Clone the repository:

Bash

git clone https://github.com/Sourabh2320/Career-Sphere.git
cd CareerSphere
Set up a virtual environment:

Bash

python -m venv venv
On Windows:

Bash

venv\Scripts\activate
On macOS/Linux:

Bash

source venv/bin/activate
Install dependencies:

Bash

pip install -r requirements.txt
Local Development
Configure environment variables:
Create a .env file in the root directory and add your local or a test database URI and a secret key.

Code snippet

# .env
DATABASE_URL="sqlite:///jobportal.db"
SECRET_KEY="your-secret-key-here"
Note: This file should be in your .gitignore to prevent it from being committed to the repository.

Initialize the database:
Use a separate script to create the database tables.

Bash

python create_db.py
Run the application:

Bash

flask run
Your application will be available at http://127.0.0.1:5000.

Deployment
The project is configured for continuous deployment on Render.

Set up your Aiven PostgreSQL database.

Connect your GitHub repository to Render.

Configure environment variables on Render:

DATABASE_URL: Your full Aiven PostgreSQL connection string.

SECRET_KEY: A strong, unique secret key for your application.

Set the Build Command:

Bash

python create_db.py && pip install -r requirements.txt
Set the Start Command:

Bash

gunicorn app:app
This ensures that the database schema is created on the production server before the application starts.

# Credits
Made with ❤️ by Sourabh

Github: https://github.com/Sourabh2320

Bootstrap Icons
   https://icons.getbootstrap.com/
