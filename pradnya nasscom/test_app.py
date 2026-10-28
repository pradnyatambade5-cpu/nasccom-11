import unittest
from app import create_app
from models import db, User, Income, Expense, Budget, SavingsGoal

class FinanceAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def login_demo(self):
        return self.client.post('/login', data={
            'email': 'demo@example.com',
            'password': 'Demo@123'
        }, follow_redirects=True)

    def test_landing_page(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Take Control of Your Money', res.data)
        self.assertIn(b'Smart Budgeting', res.data)

    def test_demo_login_flow(self):
        res = self.login_demo()
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Dashboard Overview', res.data)
        self.assertIn(b'Monthly Income', res.data)
        self.assertIn(b'Total Expenses', res.data)

    def test_dashboard_charts_api(self):
        self.login_demo()
        res = self.client.get('/dashboard/api/charts')
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertIn('monthly_labels', json_data)
        self.assertIn('income_data', json_data)
        self.assertIn('category_labels', json_data)
        self.assertIn('budget_labels', json_data)

    def test_income_crud(self):
        self.login_demo()
        # View income page
        res = self.client.get('/income/')
        self.assertEqual(res.status_code, 200)

        # Add new income
        res = self.client.post('/income/add', data={
            'amount': '15000',
            'source': 'Freelance',
            'date': '2026-09-01',
            'description': 'Mobile App Contract'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Mobile App Contract', res.data)

    def test_expenses_crud(self):
        self.login_demo()
        # View expense page
        res = self.client.get('/expenses/')
        self.assertEqual(res.status_code, 200)

        # Add expense
        res = self.client.post('/expenses/add', data={
            'amount': '850',
            'category': 'Food',
            'date': '2026-09-05',
            'description': 'Dinner with team'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Dinner with team', res.data)

    def test_budget_management(self):
        self.login_demo()
        res = self.client.get('/budget/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Category Budgets', res.data)
        self.assertIn(b'Food', res.data)

    def test_savings_goals(self):
        self.login_demo()
        res = self.client.get('/savings/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'New Laptop', res.data)

    def test_ai_advisor_page_and_chat(self):
        self.login_demo()
        res = self.client.get('/advisor/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'AI Financial Advisor', res.data)
        self.assertIn(b'These insights are for informational purposes only', res.data)

        # Chat API
        chat_res = self.client.post('/advisor/chat', json={
            'message': 'Where am I overspending?'
        })
        self.assertEqual(chat_res.status_code, 200)
        json_data = chat_res.get_json()
        self.assertIn('response', json_data)
        self.assertTrue(len(json_data['response']) > 10)

    def test_reports_and_csv(self):
        self.login_demo()
        res = self.client.get('/reports/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Monthly Financial Report', res.data)

        # CSV Export
        csv_res = self.client.get('/reports/export/csv')
        self.assertEqual(csv_res.status_code, 200)
        self.assertEqual(csv_res.content_type, 'text/csv; charset=utf-8')

    def test_profile_page(self):
        self.login_demo()
        res = self.client.get('/profile/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Alex Morgan', res.data)

if __name__ == '__main__':
    unittest.main()
