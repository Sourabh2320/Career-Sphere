import os
from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

# Configuration and Flask App Initialization
app = Flask(__name__)

if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobportal.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_employer = db.Column(db.Boolean, default=False)
    jobs = db.relationship('Job', backref='employer', lazy=True)
    applications = db.relationship('Application', backref='applicant', lazy=True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    salary = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    applications = db.relationship('Application', backref='job', lazy=True, cascade='all, delete-orphan')

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_applied = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    details = db.relationship('ApplicationDetails', backref='application', uselist=False, lazy=True)

class ApplicationDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    qualification = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.String(50), nullable=False)
    percentage_cgpa = db.Column(db.String(10), nullable=False)
    skills = db.Column(db.String(255), nullable=False)
    hobbies = db.Column(db.String(255), nullable=True)

def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

# --- NEW: Context Processor for User Count ---
@app.context_processor
def inject_user_count():
    """Injects the total number of users into the context of all templates."""
    with app.app_context():
        try:
            user_count = db.session.query(User).count()
        except Exception:
            # Fallback in case the database is not ready
            user_count = 0
        return dict(user_count=user_count)
# --- END NEW CODE ---

@app.route('/')
def home():
    user = get_current_user()
    jobs = Job.query.order_by(Job.date_posted.desc()).all()
    return render_template('home.html', user=user, jobs=jobs)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_employer = request.form.get('is_employer') == 'on'
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists!')
        
        hashed_password = generate_password_hash(password, method='scrypt')
        new_user = User(username=username, password_hash=hashed_password, is_employer=is_employer)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            return redirect(url_for('home'))
        return render_template('login.html', error='Invalid username or password!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    user = get_current_user()
    if not user or not user.is_employer:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        salary = request.form['salary']
        country = request.form['country']
        state = request.form['state']
        category = request.form['category']
        job_type = request.form['job_type']
        company = request.form['company']
        
        location = f"{state}, {country}"

        new_job = Job(title=title, description=description, salary=salary,
                      location=location, country=country, state=state, 
                      category=category, job_type=job_type, company=company, employer_id=user.id)
        db.session.add(new_job)
        db.session.commit()
        return redirect(url_for('my_jobs'))
    return render_template('post_job.html', user=user)

@app.route('/my_jobs')
def my_jobs():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    if user.is_employer:
        jobs = Job.query.filter_by(employer_id=user.id).all()
        jobs_with_applicants = []
        for job in jobs:
            applications_for_job = job.applications
            applicants_details = []
            for application in applications_for_job:
                applicant_user = User.query.get(application.applicant_id)
                applicant_info = ApplicationDetails.query.filter_by(application_id=application.id).first()
                applicants_details.append({
                    'id': applicant_user.id,
                    'username': applicant_user.username,
                    'date_applied': application.date_applied,
                    'application_id': application.id,
                    'status': application.status,
                    'details': applicant_info
                })
            
            jobs_with_applicants.append({
                'job': job,
                'applicant_count': len(applications_for_job),
                'applicants': applicants_details
            })
            
        return render_template('my_jobs_employer.html', user=user, jobs_with_applicants=jobs_with_applicants)
    else:
        applications = Application.query.filter_by(applicant_id=user.id).all()
        return render_template('my_jobs_seeker.html', user=user, applications=applications)

# Corrected delete route
@app.route('/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    user = get_current_user()
    
    if not user or not user.is_employer:
        return "Unauthorized", 403

    job = Job.query.get_or_404(job_id)

    if job.employer_id != user.id:
        return "Unauthorized", 403

    # Manually delete related records to handle circular dependencies properly
    for application in job.applications:
        if application.details:
            db.session.delete(application.details)
        db.session.delete(application)
    
    db.session.delete(job)
    db.session.commit()

    return redirect(url_for('my_jobs'))

@app.route('/apply/<int:job_id>')
def apply_for_job(job_id):
    user = get_current_user()
    if not user or user.is_employer:
        return redirect(url_for('login'))

    job = Job.query.get_or_404(job_id)
    existing_application = Application.query.filter_by(
        job_id=job_id, applicant_id=user.id
    ).first()
    if existing_application:
        return f'<div class="alert alert-warning">You have already applied for this job. <a href="{url_for("home")}">Go back to home</a></div>'

    new_application = Application(job_id=job_id, applicant_id=user.id)
    db.session.add(new_application)
    db.session.commit()
    return f'<div class="alert alert-success">Application submitted successfully! <a href="{url_for("home")}">Go back to home</a></div>'

@app.route('/accept_application/<int:application_id>')
def accept_application(application_id):
    user = get_current_user()
    application = Application.query.get_or_404(application_id)
    if not user or user.id != application.job.employer_id:
        return "Unauthorized", 403

    application.status = 'accepted'
    db.session.commit()
    return redirect(url_for('my_jobs'))

@app.route('/reject_application/<int:application_id>')
def reject_application(application_id):
    user = get_current_user()
    application = Application.query.get_or_404(application_id)
    if not user or user.id != application.job.employer_id:
        return "Unauthorized", 403

    application.status = 'rejected'
    db.session.commit()
    return redirect(url_for('my_jobs'))

@app.route('/hire_applicant/<int:application_id>')
def hire_applicant(application_id):
    user = get_current_user()
    application = Application.query.get_or_404(application_id)
    if not user or user.id != application.job.employer_id:
        return "Unauthorized", 403

    application.status = 'hired'
    db.session.commit()
    return redirect(url_for('my_jobs'))

@app.route('/cancel_hire/<int:application_id>')
def cancel_hire(application_id):
    user = get_current_user()
    application = Application.query.get_or_404(application_id)
    if not user or user.id != application.job.employer_id:
        return "Unauthorized", 403

    application.status = 'canceled'
    db.session.commit()
    return redirect(url_for('my_jobs'))

@app.route('/submit_details/<int:application_id>', methods=['GET', 'POST'])
def submit_details(application_id):
    user = get_current_user()
    application = Application.query.get_or_404(application_id)
    
    if not user or user.id != application.applicant_id or application.status != 'accepted':
        return "Unauthorized or Application not accepted", 403

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        address = request.form.get('address')
        qualification = request.form.get('qualification')
        experience = request.form.get('experience')
        percentage_cgpa = request.form.get('percentage_cgpa')
        skills = request.form.get('skills')
        hobbies = request.form.get('hobbies')
        
        details = ApplicationDetails.query.filter_by(application_id=application_id).first()
        if not details:
            details = ApplicationDetails(
                application_id=application_id,
                full_name=full_name,
                email=email,
                phone_number=phone_number,
                address=address,
                qualification=qualification,
                experience=experience,
                percentage_cgpa=percentage_cgpa,
                skills=skills,
                hobbies=hobbies
            )
            db.session.add(details)
        else:
            details.full_name = full_name
            details.email = email
            details.phone_number = phone_number
            details.address = address
            details.qualification = qualification
            details.experience = experience
            details.percentage_cgpa = percentage_cgpa
            details.skills = skills
            details.hobbies = hobbies

        db.session.commit()
        
        return f'<div class="alert alert-success">Details submitted successfully! Your employer will review your information. <a href="{url_for("home")}">Go back to home</a></div>'
            
    return render_template('submit_details.html', application_id=application_id)

@app.route('/search', methods=['GET'])
def search_jobs():
    user = get_current_user()
    query = request.args.get('query')
    location = request.args.get('location')
    category = request.args.get('category')

    search_results = Job.query
    if query:
        search_results = search_results.filter(
            (Job.title.contains(query)) |
            (Job.description.contains(query)) |
            (Job.company.contains(query))
        )
    if location:
        search_results = search_results.filter(Job.location.contains(location))
    if category:
        search_results = search_results.filter(Job.category.contains(category))

    search_results = search_results.order_by(Job.date_posted.desc()).all()
    return render_template('home.html', user=user, jobs=search_results, search_query=query, search_location=location, search_category=category)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')