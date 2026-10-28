from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import extract
from models import db, Income

income_bp = Blueprint('income', __name__)

@income_bp.route('/')
@login_required
def index():
    today = date.today()
    incomes = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc(), Income.id.desc()).all()

    cur_month_incomes = [i for i in incomes if i.date.year == today.year and i.date.month == today.month]
    cur_month_total = sum(i.amount for i in cur_month_incomes)
    all_time_total = sum(i.amount for i in incomes)

    # Source breakdown
    source_stats = {}
    for i in cur_month_incomes:
        source_stats[i.source] = source_stats.get(i.source, 0.0) + i.amount

    return render_template(
        'income.html',
        incomes=incomes,
        cur_month_total=cur_month_total,
        all_time_total=all_time_total,
        source_stats=source_stats,
        sources=Income.SOURCES,
        today_str=today.isoformat()
    )

@income_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 0))
            if amount <= 0:
                flash('Income amount must be greater than zero.', 'danger')
                return redirect(url_for('income.index'))
        except (ValueError, TypeError):
            flash('Invalid amount provided.', 'danger')
            return redirect(url_for('income.index'))

        source = request.form.get('source', 'Salary').strip()
        if source not in Income.SOURCES:
            source = 'Other'

        date_str = request.form.get('date', '').strip()
        try:
            income_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
        except ValueError:
            income_date = date.today()

        description = request.form.get('description', '').strip()

        new_income = Income(
            user_id=current_user.id,
            amount=amount,
            source=source,
            date=income_date,
            description=description
        )
        db.session.add(new_income)
        db.session.commit()

        flash(f'Successfully added ₹{amount:,.2f} under {source}!', 'success')
        return redirect(url_for('income.index'))

    return redirect(url_for('income.index'))

@income_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    income = Income.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    try:
        amount = float(request.form.get('amount', income.amount))
        if amount > 0:
            income.amount = amount
    except (ValueError, TypeError):
        pass

    source = request.form.get('source', income.source).strip()
    if source in Income.SOURCES:
        income.source = source

    date_str = request.form.get('date')
    if date_str:
        try:
            income.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    income.description = request.form.get('description', income.description).strip()
    db.session.commit()
    flash('Income record updated successfully.', 'success')
    return redirect(url_for('income.index'))

@income_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    income = Income.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(income)
    db.session.commit()
    flash('Income entry deleted.', 'info')
    return redirect(url_for('income.index'))
