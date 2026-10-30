from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Budget
from email_validator import validate_email, EmailNotValidError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def landing():
    return render_template('landing.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')

@auth_bp.route('/demo-login', methods=['GET', 'POST'])
def demo_login():
    demo_user = User.query.filter_by(email='demo@example.com').first()
    if demo_user:
        login_user(demo_user)
        flash('Logged in successfully as Demo User (Alex Morgan)!', 'info')
        return redirect(url_for('dashboard.index'))
    else:
        flash('Demo user not found. Please register a new account.', 'warning')
        return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validations
        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html', name=name, email=email)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html', name=name, email=email)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', name=name, email=email)

        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError:
            flash('Please enter a valid email address.', 'danger')
            return render_template('register.html', name=name, email=email)

        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

        # Create user
        new_user = User(name=name, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Seed starter budget categories
        starter_budgets = [
            ('Food', 6000.0),
            ('Rent', 12000.0),
            ('Transport', 3000.0),
            ('Entertainment', 2000.0),
            ('Utilities', 2500.0)
        ]
        for cat, amt in starter_budgets:
            db.session.add(Budget(user_id=new_user.id, category=cat, amount=amt))
        db.session.commit()

        login_user(new_user)
        flash('Account created successfully! Welcome to Personal Finance Advisor Bot.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('auth.login'))
