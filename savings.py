from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, SavingsGoal

savings_bp = Blueprint('savings', __name__)

@savings_bp.route('/')
@login_required
def index():
    goals = SavingsGoal.query.filter_by(user_id=current_user.id).order_by(SavingsGoal.deadline.asc()).all()
    total_target = sum(g.target_amount for g in goals)
    total_saved = sum(g.current_amount for g in goals)
    total_remaining = sum(g.remaining_amount for g in goals)
    overall_progress = round((total_saved / total_target * 100), 1) if total_target > 0 else 0.0

    return render_template(
        'savings.html',
        goals=goals,
        total_target=total_target,
        total_saved=total_saved,
        total_remaining=total_remaining,
        overall_progress=overall_progress,
        today=date.today()
    )

@savings_bp.route('/add', methods=['POST'])
@login_required
def add():
    name = request.form.get('name', '').strip()
    if not name:
        flash('Please enter a goal name.', 'danger')
        return redirect(url_for('savings.index'))

    try:
        target_amount = float(request.form.get('target_amount', 0))
        current_amount = float(request.form.get('current_amount', 0))
        if target_amount <= 0:
            flash('Target amount must be greater than zero.', 'danger')
            return redirect(url_for('savings.index'))
    except (ValueError, TypeError):
        flash('Invalid amounts specified.', 'danger')
        return redirect(url_for('savings.index'))

    deadline_str = request.form.get('deadline', '').strip()
    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        flash('Please select a valid deadline date.', 'danger')
        return redirect(url_for('savings.index'))

    goal = SavingsGoal(
        user_id=current_user.id,
        name=name,
        target_amount=target_amount,
        current_amount=max(0.0, current_amount),
        deadline=deadline
    )
    db.session.add(goal)
    db.session.commit()
    flash(f'Savings Goal "{name}" created successfully!', 'success')
    return redirect(url_for('savings.index'))

@savings_bp.route('/deposit/<int:id>', methods=['POST'])
@login_required
def deposit(id):
    goal = SavingsGoal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    try:
        amount = float(request.form.get('amount', 0))
        if amount <= 0:
            flash('Deposit amount must be greater than zero.', 'danger')
            return redirect(url_for('savings.index'))
    except (ValueError, TypeError):
        flash('Invalid deposit amount.', 'danger')
        return redirect(url_for('savings.index'))

    goal.current_amount += amount
    db.session.commit()
    flash(f'Added ₹{amount:,.2f} to "{goal.name}". New balance: ₹{goal.current_amount:,.2f}!', 'success')
    return redirect(url_for('savings.index'))

@savings_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    goal = SavingsGoal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    name = request.form.get('name', '').strip()
    if name:
        goal.name = name

    try:
        target = float(request.form.get('target_amount', goal.target_amount))
        if target > 0:
            goal.target_amount = target
    except (ValueError, TypeError):
        pass

    deadline_str = request.form.get('deadline')
    if deadline_str:
        try:
            goal.deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    db.session.commit()
    flash('Savings goal updated successfully.', 'success')
    return redirect(url_for('savings.index'))

@savings_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    goal = SavingsGoal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    flash(f'Goal "{goal.name}" deleted.', 'info')
    return redirect(url_for('savings.index'))
