from datetime import date
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import extract
from models import db, Income, Expense, Budget, SavingsGoal

advisor_bp = Blueprint('advisor', __name__)

NEEDS_CATEGORIES = {'Rent', 'Utilities', 'Food', 'Transport', 'Healthcare', 'Bills'}
WANTS_CATEGORIES = {'Entertainment', 'Shopping', 'Travel', 'Other'}

def get_financial_audit(user_id):
    today = date.today()
    cur_year = today.year
    cur_month = today.month

    # Income
    cur_incomes = Income.query.filter(
        Income.user_id == user_id,
        extract('year', Income.date) == cur_year,
        extract('month', Income.date) == cur_month
    ).all()
    monthly_income = sum(i.amount for i in cur_incomes)

    # Expenses
    cur_expenses = Expense.query.filter(
        Expense.user_id == user_id,
        extract('year', Expense.date) == cur_year,
        extract('month', Expense.date) == cur_month
    ).all()
    total_expenses = sum(e.amount for e in cur_expenses)

    # Budgets
    budgets = Budget.query.filter_by(user_id=user_id).all()
    budgets_dict = {b.category: b.amount for b in budgets}

    # Savings Goals
    savings_goals = SavingsGoal.query.filter_by(user_id=user_id).all()

    # Savings & rate
    monthly_savings = monthly_income - total_expenses
    savings_rate = round((monthly_savings / monthly_income * 100), 1) if monthly_income > 0 else 0.0

    # 50/30/20 Breakdown
    needs_spend = sum(e.amount for e in cur_expenses if e.category in NEEDS_CATEGORIES)
    wants_spend = sum(e.amount for e in cur_expenses if e.category in WANTS_CATEGORIES)

    needs_pct = round((needs_spend / monthly_income * 100), 1) if monthly_income > 0 else 0.0
    wants_pct = round((wants_spend / monthly_income * 100), 1) if monthly_income > 0 else 0.0
    actual_savings_pct = max(0.0, savings_rate)

    # Category breakdown
    cat_spent = {}
    for e in cur_expenses:
        cat_spent[e.category] = cat_spent.get(e.category, 0.0) + e.amount

    # Overspending detection
    overspending_alerts = []
    for cat, spent in cat_spent.items():
        limit = budgets_dict.get(cat)
        if limit and spent > limit:
            overage = spent - limit
            pct_over = round(((spent - limit) / limit * 100), 1)
            overspending_alerts.append({
                'category': cat,
                'spent': spent,
                'limit': limit,
                'overage': overage,
                'pct_over': pct_over,
                'severity': 'high' if pct_over > 20 else 'medium'
            })
        elif not limit and monthly_income > 0 and (spent / monthly_income) > 0.25:
            overspending_alerts.append({
                'category': cat,
                'spent': spent,
                'limit': 0,
                'overage': 0,
                'pct_over': round((spent / monthly_income * 100), 1),
                'severity': 'medium',
                'unbudgeted': True
            })

    # Financial Score (0 - 100)
    score = 50
    if savings_rate >= 20:
        score += 25
    elif savings_rate >= 10:
        score += 15
    elif savings_rate > 0:
        score += 5
    else:
        score -= 20

    if len(overspending_alerts) == 0:
        score += 20
    else:
        score -= min(25, len(overspending_alerts) * 10)

    if needs_pct <= 55:
        score += 5

    score = max(10, min(98, score))

    # Advice Sections
    summary_text = f"Your current monthly income is ₹{monthly_income:,.2f} with total expenses of ₹{total_expenses:,.2f}. You are saving ₹{monthly_savings:,.2f} per month ({savings_rate}% savings rate). Your overall financial health index is {score}/100."

    spending_analysis = {
        'needs_spend': needs_spend,
        'needs_pct': needs_pct,
        'target_needs': 50.0,
        'wants_spend': wants_spend,
        'wants_pct': wants_pct,
        'target_wants': 30.0,
        'savings_spend': max(0.0, monthly_savings),
        'savings_pct': actual_savings_pct,
        'target_savings': 20.0
    }

    savings_suggestions = []
    if savings_rate < 20:
        savings_suggestions.append(f"Your savings rate ({savings_rate}%) is below the recommended 20% benchmark. Aim to save at least ₹{(monthly_income * 0.20):,.2f} per month by trimming flexible 'Wants'.")
    else:
        savings_suggestions.append(f"Excellent job! Your savings rate ({savings_rate}%) meets the gold-standard 20% threshold. Consider channeling your ₹{monthly_savings:,.2f} surplus into high-yield savings or diversified mutual funds (SIP).")

    if savings_goals:
        total_monthly_required = sum(g.monthly_required for g in savings_goals)
        if monthly_savings >= total_monthly_required:
            savings_suggestions.append(f"You require ₹{total_monthly_required:,.2f}/mo to reach all your active savings goals on time. Your current monthly savings (₹{monthly_savings:,.2f}) comfortably covers this!")
        else:
            deficit = total_monthly_required - monthly_savings
            savings_suggestions.append(f"To reach all active savings goals on schedule, you need ₹{total_monthly_required:,.2f}/mo. You currently have a shortfall of ₹{deficit:,.2f}/mo. Consider extending your goal deadlines or reducing wants.")
    else:
        savings_suggestions.append("You don't have any active savings goals yet. Create an Emergency Fund goal to build a 6-month buffer!")

    budget_suggestions = []
    if overspending_alerts:
        for alert in overspending_alerts:
            if not alert.get('unbudgeted'):
                budget_suggestions.append(f"Adjust {alert['category']} budget: You spent ₹{alert['spent']:,.2f} vs ₹{alert['limit']:,.2f}. Either curtail spending by ₹{alert['overage']:,.2f} or raise your budget cap if this is unavoidable.")
    else:
        budget_suggestions.append("All category budgets are currently operating within defined thresholds. Keep maintaining strict discipline!")

    if wants_pct > 30:
        budget_suggestions.append(f"Discretionary 'Wants' spending is currently at {wants_pct}% of total income (target: ≤30%). Review non-essential dining, leisure, and shopping.")

    return {
        'monthly_income': monthly_income,
        'total_expenses': total_expenses,
        'monthly_savings': monthly_savings,
        'savings_rate': savings_rate,
        'score': score,
        'summary_text': summary_text,
        'spending_analysis': spending_analysis,
        'overspending_alerts': overspending_alerts,
        'savings_suggestions': savings_suggestions,
        'budget_suggestions': budget_suggestions,
        'savings_goals': savings_goals,
        'cat_spent': cat_spent
    }

@advisor_bp.route('/')
@login_required
def index():
    audit = get_financial_audit(current_user.id)
    return render_template('advisor.html', audit=audit)

@advisor_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get('message', '').strip().lower()

    if not message:
        return jsonify({'response': "Please ask a question regarding your personal finances, budgets, or savings goals."}), 200

    audit = get_financial_audit(current_user.id)
    inc = audit['monthly_income']
    exp = audit['total_expenses']
    sav = audit['monthly_savings']
    rate = audit['savings_rate']
    alerts = audit['overspending_alerts']
    goals = audit['savings_goals']
    analysis = audit['spending_analysis']

    # Rule-Based Intent Resolution
    if any(k in message for k in ['overspend', 'exceed', 'spending too much', 'limit', 'where am i overspending']):
        if alerts:
            bullet_points = []
            for a in alerts:
                if not a.get('unbudgeted'):
                    bullet_points.append(f"• **{a['category']}**: Spent ₹{a['spent']:,.2f} against a limit of ₹{a['limit']:,.2f} (+{a['pct_over']}% over limit, excess ₹{a['overage']:,.2f}).")
                else:
                    bullet_points.append(f"• **{a['category']}**: High unbudgeted spend of ₹{a['spent']:,.2f} ({a['pct_over']}% of your income).")
            response = (
                f"⚠️ **Overspending Audit Detected:**\n\n"
                + "\n".join(bullet_points)
                + f"\n\n**Recommendation:** Reducing discretionary spending in these categories will immediately free up cash flow to strengthen your monthly savings."
            )
        else:
            response = (
                f"✅ **Great news!** You are currently not exceeding any of your established category budgets this month.\n\n"
                f"Your total monthly expenses are ₹{exp:,.2f} against an income of ₹{inc:,.2f}, leaving a net surplus of ₹{sav:,.2f}."
            )

    elif any(k in message for k in ['save more', 'how can i save', 'increase savings', 'saving advice']):
        recommendations = []
        if analysis['wants_pct'] > 30:
            excess_wants = (analysis['wants_pct'] - 30) * inc / 100
            recommendations.append(f"• **Trim Discretionary Wants**: You are spending {analysis['wants_pct']}% of your earnings on wants (target is 30%). Cutting ₹{excess_wants:,.2f} from shopping and entertainment would boost your savings rate immediately.")
        
        if alerts:
            recommendations.append(f"• **Curb Exceeded Budgets**: Resolve your budget overages in {', '.join([a['category'] for a in alerts])} to conserve up to ₹{sum(a['overage'] for a in alerts if not a.get('unbudgeted')):,.2f} each month.")

        recommendations.append(f"• **Automate Savings**: Set up automated transfers on salary day directly into a separate high-interest recurring deposit or mutual fund SIP.")

        response = (
            f"💡 **Strategies to Boost Your Monthly Savings:**\n\n"
            + "\n".join(recommendations)
            + f"\n\nWith your current income of ₹{inc:,.2f}, saving 20% amounts to **₹{(inc * 0.2):,.2f}/month**."
        )

    elif any(k in message for k in ['analyze', 'analysis', 'breakdown', 'spending', '50/30/20']):
        response = (
            f"📊 **50/30/20 Spending Breakdown Audit:**\n\n"
            f"• **Needs (Target 50%):** ₹{analysis['needs_spend']:,.2f} ({analysis['needs_pct']}%)\n"
            f"• **Wants (Target 30%):** ₹{analysis['wants_spend']:,.2f} ({analysis['wants_pct']}%)\n"
            f"• **Savings (Target 20%):** ₹{analysis['savings_spend']:,.2f} ({analysis['savings_pct']}%)\n\n"
            f"**Evaluation:** " + (
                "Your allocation matches ideal budgeting guidelines!" if analysis['needs_pct'] <= 55 and analysis['savings_pct'] >= 20
                else "Review your wants category and keep strict boundaries on lifestyle spending to hit the 20% savings milestone."
            )
        )

    elif any(k in message for k in ['budget suggestion', 'suggest budget', 'recommend budget', 'budget plan']):
        response = (
            f"🎯 **Personalized Budget Suggestions Based on Your ₹{inc:,.2f} Monthly Income:**\n\n"
            f"• **Essential Living Needs (50% max):** Up to ₹{(inc * 0.50):,.2f} (Rent, Food, Transport, Utilities)\n"
            f"• **Lifestyle & Discretionary (30% max):** Up to ₹{(inc * 0.30):,.2f} (Dining out, Entertainment, Shopping)\n"
            f"• **Wealth & Emergency Savings (20% min):** At least ₹{(inc * 0.20):,.2f} (Emergency buffer, SIP investments)\n\n"
            f"Make sure to set specific caps under the **Budgets** section for your highest spending items."
        )

    elif any(k in message for k in ['goal', 'track', 'laptop', 'emergency', 'am i on track']):
        if goals:
            lines = []
            for g in goals:
                lines.append(f"• **{g.name}**: Saved ₹{g.current_amount:,.2f} of ₹{g.target_amount:,.2f} ({g.progress_percent}%). Remaining: ₹{g.remaining_amount:,.2f} by {g.deadline.strftime('%b %d, %Y')} (~₹{g.monthly_required:,.2f}/mo needed).")
            tot_req = sum(g.monthly_required for g in goals)
            response = (
                f"🎯 **Savings Goals Milestone Check:**\n\n"
                + "\n".join(lines)
                + f"\n\n**Total required savings:** ₹{tot_req:,.2f}/month.\n"
                + f"**Your current monthly savings:** ₹{sav:,.2f}/month.\n\n"
                + ("✅ **You are on track!** Your monthly surplus covers all required deposits." if sav >= tot_req
                   else f"⚠️ **Attention:** You need ₹{(tot_req - sav):,.2f} more per month to achieve all deadlines on schedule.")
            )
        else:
            response = "You currently have no active savings goals configured. Head over to the Savings tab to set your first milestone (e.g., Emergency Fund or New Laptop)!"

    else:
        # Default intelligent response
        response = (
            f"Hello! I am your AI Financial Advisor. Based on your live data for this month:\n\n"
            f"• **Income:** ₹{inc:,.2f}\n"
            f"• **Expenses:** ₹{exp:,.2f}\n"
            f"• **Net Savings:** ₹{sav:,.2f} ({rate}% savings rate)\n"
            f"• **Budget Status:** {'⚠️ ' + str(len(alerts)) + ' category alerts' if alerts else '✅ All budgets on track'}\n\n"
            f"Try asking:\n"
            f"- *\"Where am I overspending?\"*\n"
            f"- *\"How can I save more?\"*\n"
            f"- *\"Analyze my spending\"*\n"
            f"- *\"Am I on track for my savings goals?\"*"
        )

    return jsonify({'response': response}), 200
