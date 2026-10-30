# Personal Finance Advisor Bot 💰🤖

A full-featured modern FinTech web application for personal income tracking, expense management, smart budgeting, savings goal milestones, and algorithmic rule-based AI financial insights in Indian Rupees (₹).

---

## 🌟 Key Features

1. **Authentication & Data Privacy**
   - Secure Registration and Login with Werkzeug password hashing.
   - Session management via Flask-Login.
   - Complete multi-tenant privacy: each user's financial records are completely isolated.
   - Built-in **1-Click Demo Login** (`demo@example.com` / `Demo@123`) loaded with realistic financial data.

2. **Income Management**
   - Track multiple revenue streams (Salary, Freelance, Allowance, Scholarship, Business, Other).
   - Real-time monthly calculations and full CRUD management.

3. **Expense Tracking**
   - Categorize all daily outlays (Food, Rent, Transport, Education, Healthcare, Shopping, Entertainment, Utilities, Bills, Travel, Other).
   - Instant category breakdown pills and chronological history.

4. **Category Budgets**
   - Configure category-specific monthly spending limits.
   - Visual progress bars with dynamic status indicators (On Track, Near Limit, **Budget Exceeded**).

5. **Savings Goals**
   - Set targets for gadgets, emergency funds, or vacations.
   - Real-time progress bars, remaining target amount, and automated required monthly savings formula.
   - 1-click quick deposit feature.

6. **Rule-Based Local AI Advisor & Interactive Bot**
   - Algorithmic financial audit calculating 50/30/20 proportions, savings rates, and overspending triggers.
   - Structured categorized advice: Summary, Spending Analysis, Overspending Alerts, Savings Suggestions, Budget Suggestions.
   - Interactive Chat Bot with suggested prompts:
     - *"Where am I overspending?"*
     - *"How can I save more?"*
     - *"Analyze my spending"*
     - *"Give me a budget suggestion"*
     - *"Am I on track for my savings goals?"*
   - Clear compliance disclaimer on financial advice.

7. **Financial Analytics & Charts**
   - 4 Chart.js charts: Income vs Expenses (6-month bar), Expense by Category (doughnut), Monthly Savings (line/area), Budget vs Actual (grouped bar).

8. **Monthly Reports & CSV Export**
   - Filterable statement by month and year.
   - One-click CSV export and print-ready format.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.14+, Flask 3.1.0, Flask-SQLAlchemy, Flask-Login, Werkzeug, python-dotenv, email-validator
- **Database**: SQLite (automatic schema creation on startup)
- **Frontend**: HTML5, Vanilla CSS3 (Custom FinTech SaaS Design System), Vanilla JavaScript (ES6+), Jinja2, Chart.js, RemixIcon

---

## 🚀 How to Run the Application

### 1. Create and Activate Virtual Environment
```bash
# Windows
py -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
python app.py
```

Open your browser and visit: **`http://127.0.0.1:5000`**

---

## 🧪 Demo Account Credentials
- **Email**: `demo@example.com`
- **Password**: `Demo@123`
*(Or click the "One-Click Demo User" button on the Login page)*
