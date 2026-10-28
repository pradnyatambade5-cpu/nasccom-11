from flask import Flask
from .auth import auth_bp
from .dashboard import dashboard_bp
from .income import income_bp
from .expenses import expenses_bp
from .budget import budget_bp
from .savings import savings_bp
from .advisor import advisor_bp
from .reports import reports_bp
from .profile import profile_bp

def register_blueprints(app: Flask):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(income_bp, url_prefix='/income')
    app.register_blueprint(expenses_bp, url_prefix='/expenses')
    app.register_blueprint(budget_bp, url_prefix='/budget')
    app.register_blueprint(savings_bp, url_prefix='/savings')
    app.register_blueprint(advisor_bp, url_prefix='/advisor')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(profile_bp, url_prefix='/profile')
