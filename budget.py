from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Budget, Expense

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/')
@login_required
def index():
    today = date.today()
    budgets = Budget.query.filter_by(user_id=current_user.id).all()

    # Calculate actual spending for current month per category
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    cur_month_expenses = [e for e in expenses if e.date.year == today.year and e.date.month == today.month]

    cat_spent = {}
    for e in cur_month_expenses:
        cat_spent[e.category] = cat_spent.get(e.category, 0.0) + e.amount

    budget_items = []
    total_budgeted = 0.0
    total_spent_budgeted = 0.0

    for b in budgets:
        spent = cat_spent.get(b.category, 0.0)
        pct = round((spent / b.amount * 100), 1) if b.amount > 0 else 0.0
        remaining = round(b.amount - spent, 2)

        if spent > b.amount:
            status = 'Budget Exceeded'
            status_class = 'danger'
        elif pct >= 80:
            status = 'Near Limit'
            status_class = 'warning'
        else:
            status = 'On Track'
            status_class = 'success'

        total_budgeted += b.amount
        total_spent_budgeted += spent

        budget_items.append({
            'id': b.id,
            'category': b.category,
            'amount': b.amount,
            'spent': spent,
            'remaining': remaining,
            'pct': pct,
            'status': status,
            'status_class': status_class
        })

    budgeted_categories = {b.category for b in budgets}
    unbudgeted_categories = [c for c in Expense.CATEGORIES if c not in budgeted_categories]

    return render_template(
        'budget.html',
        budget_items=budget_items,
        total_budgeted=total_budgeted,
        total_spent_budgeted=total_spent_budgeted,
        unbudgeted_categories=unbudgeted_categories,
        categories=Expense.CATEGORIES
    )

@budget_bp.route('/add', methods=['POST'])
@login_required
def add():
    category = request.form.get('category', '').strip()
    try:
        amount = float(request.form.get('amount', 0))
        if amount <= 0:
            flash('Budget amount must be greater than zero.', 'danger')
            return redirect(url_for('budget.index'))
    except (ValueError, TypeError):
        flash('Invalid budget amount.', 'danger')
        return redirect(url_for('budget.index'))

    existing = Budget.query.filter_by(user_id=current_user.id, category=category).first()
    if existing:
        existing.amount = amount
        db.session.commit()
        flash(f'Budget for {category} updated to ₹{amount:,.2f}.', 'success')
    else:
        new_budget = Budget(user_id=current_user.id, category=category, amount=amount)
        db.session.add(new_budget)
        db.session.commit()
        flash(f'Budget for {category} set to ₹{amount:,.2f}.', 'success')

    return redirect(url_for('budget.index'))

@budget_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    budget = Budget.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    cat = budget.category
    db.session.delete(budget)
    db.session.commit()
    flash(f'Budget limit for {cat} removed.', 'info')
    return redirect(url_for('budget.index'))
