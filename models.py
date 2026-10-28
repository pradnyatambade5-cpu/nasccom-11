from datetime import datetime, date, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def utc_now():
    return datetime.now(timezone.utc)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    # Relationships
    incomes = db.relationship('Income', backref='user', lazy=True, cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='user', lazy=True, cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade='all, delete-orphan')
    savings_goals = db.relationship('SavingsGoal', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'


class Income(db.Model):
    __tablename__ = 'incomes'

    SOURCES = ['Salary', 'Freelance', 'Allowance', 'Scholarship', 'Business', 'Other']

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(50), nullable=False, default='Salary')
    date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def __repr__(self):
        return f'<Income {self.source} - ₹{self.amount}>'


class Expense(db.Model):
    __tablename__ = 'expenses'

    CATEGORIES = [
        'Food', 'Rent', 'Transport', 'Education', 'Healthcare',
        'Shopping', 'Entertainment', 'Utilities', 'Bills', 'Travel', 'Other'
    ]

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False, default='Food')
    date = db.Column(db.Date, nullable=False, default=date.today)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def __repr__(self):
        return f'<Expense {self.category} - ₹{self.amount}>'


class Budget(db.Model):
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'category', name='unique_user_category_budget'),
    )

    def __repr__(self):
        return f'<Budget {self.category} - ₹{self.amount}>'


class SavingsGoal(db.Model):
    __tablename__ = 'savings_goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0, nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    @property
    def progress_percent(self):
        if self.target_amount <= 0:
            return 100.0 if self.current_amount > 0 else 0.0
        pct = (self.current_amount / self.target_amount) * 100
        return min(100.0, max(0.0, round(pct, 1)))

    @property
    def remaining_amount(self):
        return max(0.0, round(self.target_amount - self.current_amount, 2))

    @property
    def months_remaining(self):
        today = date.today()
        if self.deadline <= today:
            return 0
        months = (self.deadline.year - today.year) * 12 + (self.deadline.month - today.month)
        if self.deadline.day < today.day:
            months = max(1, months)
        return max(1, months)

    @property
    def monthly_required(self):
        if self.remaining_amount <= 0:
            return 0.0
        m = self.months_remaining
        return round(self.remaining_amount / (m if m > 0 else 1), 2)

    def __repr__(self):
        return f'<SavingsGoal {self.name} - ₹{self.current_amount}/₹{self.target_amount}>'
