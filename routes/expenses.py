from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Expense, Budget

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/')
@login_required
def index():
    today = date.today()
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc(), Expense.id.desc()).all()

    cur_month_expenses = [e for e in expenses if e.date.year == today.year and e.date.month == today.month]
    cur_month_total = sum(e.amount for e in cur_month_expenses)
    all_time_total = sum(e.amount for e in expenses)

    # Category breakdown for current month
    category_totals = {}
    for e in cur_month_expenses:
        category_totals[e.category] = category_totals.get(e.category, 0.0) + e.amount

    # Budgets lookup for warnings
    budgets = {b.category: b.amount for b in Budget.query.filter_by(user_id=current_user.id).all()}

    category_breakdown = []
    for cat in Expense.CATEGORIES:
        spent = category_totals.get(cat, 0.0)
        limit = budgets.get(cat, 0.0)
        if spent > 0 or limit > 0:
            category_breakdown.append({
                'category': cat,
                'spent': spent,
                'limit': limit,
                'pct': round((spent / limit * 100), 1) if limit > 0 else 0.0,
                'exceeded': limit > 0 and spent > limit
            })

    category_breakdown.sort(key=lambda x: x['spent'], reverse=True)

    return render_template(
        'expenses.html',
        expenses=expenses,
        cur_month_total=cur_month_total,
        all_time_total=all_time_total,
        category_breakdown=category_breakdown,
        categories=Expense.CATEGORIES,
        today_str=today.isoformat()
    )

@expenses_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 0))
            if amount <= 0:
                flash('Expense amount must be greater than zero.', 'danger')
                return redirect(url_for('expenses.index'))
        except (ValueError, TypeError):
            flash('Invalid amount provided.', 'danger')
            return redirect(url_for('expenses.index'))

        category = request.form.get('category', 'Food').strip()
        if category not in Expense.CATEGORIES:
            category = 'Other'

        date_str = request.form.get('date', '').strip()
        try:
            expense_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
        except ValueError:
            expense_date = date.today()

        description = request.form.get('description', '').strip()

        new_expense = Expense(
            user_id=current_user.id,
            amount=amount,
            category=category,
            date=expense_date,
            description=description
        )
        db.session.add(new_expense)
        db.session.commit()

        # Check if this expense exceeded budget
        budget = Budget.query.filter_by(user_id=current_user.id, category=category).first()
        if budget:
            total_spent = sum(
                e.amount for e in Expense.query.filter_by(user_id=current_user.id, category=category).all()
                if e.date.year == expense_date.year and e.date.month == expense_date.month
            )
            if total_spent > budget.amount:
                flash(f'Expense recorded. ⚠️ Notice: {category} budget of ₹{budget.amount:,.2f} has been exceeded (Total spent: ₹{total_spent:,.2f})!', 'warning')
                return redirect(url_for('expenses.index'))

        flash(f'Successfully added ₹{amount:,.2f} under {category}!', 'success')
        return redirect(url_for('expenses.index'))

    return redirect(url_for('expenses.index'))

@expenses_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    try:
        amount = float(request.form.get('amount', expense.amount))
        if amount > 0:
            expense.amount = amount
    except (ValueError, TypeError):
        pass

    category = request.form.get('category', expense.category).strip()
    if category in Expense.CATEGORIES:
        expense.category = category

    date_str = request.form.get('date')
    if date_str:
        try:
            expense.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    expense.description = request.form.get('description', expense.description).strip()
    db.session.commit()
    flash('Expense record updated successfully.', 'success')
    return redirect(url_for('expenses.index'))

@expenses_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    flash('Expense record deleted.', 'info')
    return redirect(url_for('expenses.index'))
