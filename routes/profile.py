from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Income, Expense, Budget, SavingsGoal

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/')
@login_required
def index():
    total_incomes_count = Income.query.filter_by(user_id=current_user.id).count()
    total_expenses_count = Expense.query.filter_by(user_id=current_user.id).count()
    total_budgets_count = Budget.query.filter_by(user_id=current_user.id).count()
    total_goals_count = SavingsGoal.query.filter_by(user_id=current_user.id).count()

    return render_template(
        'profile.html',
        user=current_user,
        total_incomes_count=total_incomes_count,
        total_expenses_count=total_expenses_count,
        total_budgets_count=total_budgets_count,
        total_goals_count=total_goals_count
    )

@profile_bp.route('/update', methods=['POST'])
@login_required
def update():
    name = request.form.get('name', '').strip()
    if name:
        current_user.name = name

    new_password = request.form.get('new_password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()

    if new_password:
        if len(new_password) < 6:
            flash('New password must be at least 6 characters long.', 'danger')
            return redirect(url_for('profile.index'))
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('profile.index'))
        current_user.set_password(new_password)
        flash('Password successfully updated.', 'success')

    db.session.commit()
    flash('Profile details updated successfully.', 'success')
    return redirect(url_for('profile.index'))
