from datetime import date
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import extract
from models import db, Income, Expense, Budget, SavingsGoal

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    today = date.today()
    cur_year = today.year
    cur_month = today.month

    # Current month incomes
    cur_incomes = Income.query.filter(
        Income.user_id == current_user.id,
        extract('year', Income.date) == cur_year,
        extract('month', Income.date) == cur_month
    ).all()
    monthly_income = sum(i.amount for i in cur_incomes)

    # Current month expenses
    cur_expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        extract('year', Expense.date) == cur_year,
        extract('month', Expense.date) == cur_month
    ).all()
    total_expenses = sum(e.amount for e in cur_expenses)

    # Net monthly savings and rate
    monthly_savings = monthly_income - total_expenses
    savings_rate = round((monthly_savings / monthly_income * 100), 1) if monthly_income > 0 else 0.0

    # Budgets & utilization
    budgets = Budget.query.filter_by(user_id=current_user.id).all()
    total_budget_allocated = sum(b.amount for b in budgets)
    
    # Category spending breakdown
    category_spending = {}
    for exp in cur_expenses:
        category_spending[exp.category] = category_spending.get(exp.category, 0.0) + exp.amount

    budget_alerts = []
    for b in budgets:
        spent = category_spending.get(b.category, 0.0)
        pct = round((spent / b.amount * 100), 1) if b.amount > 0 else 0.0
        if spent > b.amount:
            budget_alerts.append({
                'category': b.category,
                'spent': spent,
                'limit': b.amount,
                'pct': pct,
                'status': 'exceeded'
            })
        elif pct >= 80:
            budget_alerts.append({
                'category': b.category,
                'spent': spent,
                'limit': b.amount,
                'pct': pct,
                'status': 'warning'
            })

    # Savings goals
    savings_goals = SavingsGoal.query.filter_by(user_id=current_user.id).all()
    total_goal_target = sum(g.target_amount for g in savings_goals)
    total_goal_saved = sum(g.current_amount for g in savings_goals)
    overall_goal_progress = round((total_goal_saved / total_goal_target * 100), 1) if total_goal_target > 0 else 0.0

    # Recent activity (combined last 8 transactions)
    recent_incomes = [{
        'id': inc.id,
        'type': 'income',
        'title': inc.source,
        'description': inc.description or inc.source,
        'amount': inc.amount,
        'date': inc.date
    } for inc in Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc(), Income.id.desc()).limit(6).all()]

    recent_expenses = [{
        'id': exp.id,
        'type': 'expense',
        'title': exp.category,
        'description': exp.description or exp.category,
        'amount': exp.amount,
        'date': exp.date
    } for exp in Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc(), Expense.id.desc()).limit(6).all()]

    all_recent = sorted(recent_incomes + recent_expenses, key=lambda x: x['date'], reverse=True)[:8]

    return render_template(
        'dashboard.html',
        monthly_income=monthly_income,
        total_expenses=total_expenses,
        monthly_savings=monthly_savings,
        savings_rate=savings_rate,
        budgets=budgets,
        budget_alerts=budget_alerts,
        savings_goals=savings_goals,
        total_goal_target=total_goal_target,
        total_goal_saved=total_goal_saved,
        overall_goal_progress=overall_goal_progress,
        recent_transactions=all_recent,
        today=today
    )

@dashboard_bp.route('/api/charts')
@login_required
def api_charts():
    today = date.today()
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Generate last 6 months list
    months_list = []
    for m_back in reversed(range(6)):
        m = today.month - m_back
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        months_list.append((y, m, f"{month_names[m-1]} {y % 100}"))

    monthly_labels = [label for _, _, label in months_list]
    income_data = []
    expense_data = []
    savings_data = []

    for y, m, _ in months_list:
        inc = db.session.query(db.func.sum(Income.amount)).filter(
            Income.user_id == current_user.id,
            extract('year', Income.date) == y,
            extract('month', Income.date) == m
        ).scalar() or 0.0

        exp = db.session.query(db.func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id,
            extract('year', Expense.date) == y,
            extract('month', Expense.date) == m
        ).scalar() or 0.0

        income_data.append(round(inc, 2))
        expense_data.append(round(exp, 2))
        savings_data.append(round(inc - exp, 2))

    # Category breakdown for current month
    cat_query = db.session.query(
        Expense.category,
        db.func.sum(Expense.amount)
    ).filter(
        Expense.user_id == current_user.id,
        extract('year', Expense.date) == today.year,
        extract('month', Expense.date) == today.month
    ).group_by(Expense.category).all()

    category_labels = [c[0] for c in cat_query]
    category_data = [round(c[1], 2) for c in cat_query]

    # If no expenses this month, provide fallback
    if not category_labels:
        category_labels = ['No Expenses']
        category_data = [0.0]

    # Budgets vs Actual for budgeted categories
    budgets = Budget.query.filter_by(user_id=current_user.id).all()
    budget_labels = []
    budget_data = []
    actual_data = []

    cat_spent_dict = dict(cat_query)
    for b in budgets:
        budget_labels.append(b.category)
        budget_data.append(round(b.amount, 2))
        actual_data.append(round(cat_spent_dict.get(b.category, 0.0), 2))

    return jsonify({
        'monthly_labels': monthly_labels,
        'income_data': income_data,
        'expense_data': expense_data,
        'savings_data': savings_data,
        'category_labels': category_labels,
        'category_data': category_data,
        'budget_labels': budget_labels,
        'budget_data': budget_data,
        'actual_data': actual_data
    })
