import csv
import io
from datetime import date
from flask import Blueprint, render_template, request, Response
from flask_login import login_required, current_user
from sqlalchemy import extract
from models import Income, Expense, Budget

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
@login_required
def index():
    today = date.today()
    try:
        selected_month = int(request.args.get('month', today.month))
        selected_year = int(request.args.get('year', today.year))
    except (ValueError, TypeError):
        selected_month = today.month
        selected_year = today.year

    # Query incomes for month/year
    incomes = Income.query.filter(
        Income.user_id == current_user.id,
        extract('year', Income.date) == selected_year,
        extract('month', Income.date) == selected_month
    ).order_by(Income.date.asc()).all()

    # Query expenses for month/year
    expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        extract('year', Expense.date) == selected_year,
        extract('month', Expense.date) == selected_month
    ).order_by(Expense.date.asc()).all()

    total_income = sum(i.amount for i in incomes)
    total_expenses = sum(e.amount for e in expenses)
    net_savings = total_income - total_expenses
    savings_rate = round((net_savings / total_income * 100), 1) if total_income > 0 else 0.0

    # Expense category distribution
    cat_summary = {}
    for e in expenses:
        cat_summary[e.category] = cat_summary.get(e.category, 0.0) + e.amount

    # Budgets for comparison
    budgets = {b.category: b.amount for b in Budget.query.filter_by(user_id=current_user.id).all()}
    comparison = []
    for cat, spent in cat_summary.items():
        limit = budgets.get(cat, 0.0)
        pct = round((spent / limit * 100), 1) if limit > 0 else 0.0
        comparison.append({
            'category': cat,
            'spent': spent,
            'limit': limit,
            'pct': pct,
            'exceeded': limit > 0 and spent > limit
        })
    comparison.sort(key=lambda x: x['spent'], reverse=True)

    month_names = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]

    years_range = list(range(today.year - 3, today.year + 2))

    return render_template(
        'reports.html',
        incomes=incomes,
        expenses=expenses,
        total_income=total_income,
        total_expenses=total_expenses,
        net_savings=net_savings,
        savings_rate=savings_rate,
        comparison=comparison,
        selected_month=selected_month,
        selected_year=selected_year,
        month_names=month_names,
        years_range=years_range,
        today=today
    )

@reports_bp.route('/export/csv')
@login_required
def export_csv():
    incomes = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.asc()).all()
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Date', 'Type', 'Category / Source', 'Description', 'Amount (INR)'])

    combined = []
    for i in incomes:
        combined.append((i.date, 'Income', i.source, i.description or '', f"{i.amount:.2f}"))
    for e in expenses:
        combined.append((e.date, 'Expense', e.category, e.description or '', f"{e.amount:.2f}"))

    combined.sort(key=lambda x: x[0])

    for row in combined:
        writer.writerow(row)

    csv_data = output.getvalue()
    
    response = Response(
        csv_data,
        content_type='text/csv; charset=utf-8',
        headers={
            'Content-Disposition': 'attachment; filename=personal_finance_report.csv'
        }
    )
    return response
