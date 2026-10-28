import os
from datetime import date, timedelta
from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models import db, User, Income, Expense, Budget, SavingsGoal
from routes import register_blueprints

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance folder exists safely
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    register_blueprints(app)

    # Jinja filters
    @app.template_filter('inr')
    def inr_format(value):
        try:
            val = float(value)
            return f"₹{val:,.2f}"
        except (ValueError, TypeError):
            return f"₹{value}"

    @app.template_filter('inr_int')
    def inr_int_format(value):
        try:
            val = float(value)
            return f"₹{val:,.0f}"
        except (ValueError, TypeError):
            return f"₹{value}"

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    # Create tables and seed demo user on first run
    with app.app_context():
        db.create_all()
        seed_demo_data()

    return app

def seed_data_for_user(user_id):
    today = date.today()

    # Clear existing
    Income.query.filter_by(user_id=user_id).delete()
    Expense.query.filter_by(user_id=user_id).delete()
    Budget.query.filter_by(user_id=user_id).delete()
    SavingsGoal.query.filter_by(user_id=user_id).delete()

    # Income: ₹50,000 (Primary Salary ₹45,000 + Freelance ₹5,000)
    inc1 = Income(
        user_id=user_id,
        amount=45000.0,
        source='Salary',
        date=today.replace(day=1),
        description='Monthly Tech Job Salary'
    )
    inc2 = Income(
        user_id=user_id,
        amount=5000.0,
        source='Freelance',
        date=today.replace(day=10),
        description='UI Design Consulting Gig'
    )
    db.session.add_all([inc1, inc2])

    # Previous months income & expenses for chart trends
    for m_back in [1, 2, 3]:
        prev_m = today.month - m_back
        prev_y = today.year
        while prev_m <= 0:
            prev_m += 12
            prev_y -= 1
        d = date(prev_y, prev_m, 1)
        db.session.add(Income(
            user_id=user_id,
            amount=50000.0,
            source='Salary',
            date=d,
            description='Monthly Salary'
        ))
        # Add basic historical expenses
        db.session.add_all([
            Expense(user_id=user_id, amount=12000.0, category='Rent', date=d.replace(day=2), description='House Rent'),
            Expense(user_id=user_id, amount=5200.0 + m_back*100, category='Food', date=d.replace(day=5), description='Groceries & Dining'),
            Expense(user_id=user_id, amount=2800.0, category='Transport', date=d.replace(day=8), description='Metro & Fuel'),
            Expense(user_id=user_id, amount=4000.0, category='Education', date=d.replace(day=12), description='Online Certification Course'),
            Expense(user_id=user_id, amount=2200.0, category='Entertainment', date=d.replace(day=15), description='Movies & Streaming'),
            Expense(user_id=user_id, amount=2500.0, category='Shopping', date=d.replace(day=18), description='Clothing'),
            Expense(user_id=user_id, amount=1900.0, category='Utilities', date=d.replace(day=20), description='Electricity & Internet')
        ])

    # Current Month Expenses:
    # Rent ₹12,000, Food ₹5,500, Transport ₹3,000, Education ₹4,000, Entertainment ₹2,500, Shopping ₹3,000, Utilities ₹2,000
    expenses_data = [
        (12000.0, 'Rent', today.replace(day=2), 'Monthly Apartment Rent'),
        (5500.0, 'Food', today.replace(day=5), 'Groceries, Supermarket & Dining'),
        (3000.0, 'Transport', today.replace(day=7), 'Metro pass & Cab rides'),
        (4000.0, 'Education', today.replace(day=11), 'Data Science Certification & Books'),
        (2500.0, 'Entertainment', today.replace(day=14), 'Weekend Movie, Gaming & Concert'),
        (3000.0, 'Shopping', today.replace(day=18), 'Summer Apparel & Accessories'),
        (2000.0, 'Utilities', today.replace(day=22), 'High-speed Fiber Broadband & Power Bill')
    ]

    for amt, cat, dt, desc in expenses_data:
        exp = Expense(
            user_id=user_id,
            amount=amt,
            category=cat,
            date=dt,
            description=desc
        )
        db.session.add(exp)

    # Budgets:
    # Food ₹5,000 (spent 5,500 -> exceeded!), Transport ₹3,000, Education ₹4,000, Entertainment ₹2,000 (spent 2,500 -> exceeded!), Shopping ₹3,500, Rent ₹12,000, Utilities ₹2,500
    budgets_data = [
        ('Rent', 12000.0),
        ('Food', 5000.0),
        ('Transport', 3000.0),
        ('Education', 4000.0),
        ('Entertainment', 2000.0),
        ('Shopping', 3500.0),
        ('Utilities', 2500.0)
    ]
    for cat, amt in budgets_data:
        b = Budget(user_id=user_id, category=cat, amount=amt)
        db.session.add(b)

    # Savings Goals:
    # Goal: "New Laptop", Target: ₹70,000, Saved: ₹32,000, Deadline: 6 months ahead
    deadline_laptop = today + timedelta(days=180)
    g1 = SavingsGoal(
        user_id=user_id,
        name='New Laptop (MacBook Pro)',
        target_amount=70000.0,
        current_amount=32000.0,
        deadline=deadline_laptop
    )
    # Goal 2: Emergency Fund
    deadline_fund = today + timedelta(days=365)
    g2 = SavingsGoal(
        user_id=user_id,
        name='Emergency Fund (6 Months)',
        target_amount=100000.0,
        current_amount=45000.0,
        deadline=deadline_fund
    )
    db.session.add_all([g1, g2])

    db.session.commit()

def seed_demo_data():
    demo_email = 'demo@example.com'
    user = User.query.filter_by(email=demo_email).first()
    if not user:
        user = User(
            name='Alex Morgan',
            email=demo_email
        )
        user.set_password('Demo@123')
        db.session.add(user)
        db.session.commit()
        seed_data_for_user(user.id)

app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
