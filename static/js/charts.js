// Chart.js initialization for Financial Dashboard

document.addEventListener('DOMContentLoaded', () => {
  const chartCanvas = document.getElementById('incomeExpenseChart');
  if (!chartCanvas) return;

  fetch('/dashboard/api/charts')
    .then(res => res.json())
    .then(data => {
      // 1. Income vs Expenses Chart (6-month Bar Chart)
      const ctx1 = document.getElementById('incomeExpenseChart').getContext('2d');
      new Chart(ctx1, {
        type: 'bar',
        data: {
          labels: data.monthly_labels,
          datasets: [
            {
              label: 'Income (₹)',
              data: data.income_data,
              backgroundColor: 'rgba(16, 185, 129, 0.75)',
              borderColor: '#10b981',
              borderWidth: 1,
              borderRadius: 6
            },
            {
              label: 'Expenses (₹)',
              data: data.expense_data,
              backgroundColor: 'rgba(244, 63, 94, 0.75)',
              borderColor: '#f43f5e',
              borderWidth: 1,
              borderRadius: 6
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { labels: { color: '#94a3b8' } },
            tooltip: {
              callbacks: {
                label: (ctx) => ` ${ctx.dataset.label}: ₹${ctx.raw.toLocaleString('en-IN')}`
              }
            }
          },
          scales: {
            x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
            y: { 
              grid: { color: 'rgba(255, 255, 255, 0.05)' }, 
              ticks: { 
                color: '#94a3b8',
                callback: (val) => '₹' + val.toLocaleString('en-IN')
              } 
            }
          }
        }
      });

      // 2. Expense by Category Chart (Doughnut Chart)
      const ctx2 = document.getElementById('categoryDoughnutChart').getContext('2d');
      const vibrantColors = [
        '#6366f1', '#10b981', '#f59e0b', '#f43f5e', '#06b6d4',
        '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#3b82f6', '#a855f7'
      ];
      new Chart(ctx2, {
        type: 'doughnut',
        data: {
          labels: data.category_labels,
          datasets: [{
            data: data.category_data,
            backgroundColor: vibrantColors.slice(0, data.category_labels.length),
            borderWidth: 2,
            borderColor: '#111827'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'right', labels: { color: '#94a3b8', boxWidth: 14 } },
            tooltip: {
              callbacks: {
                label: (ctx) => ` ${ctx.label}: ₹${ctx.raw.toLocaleString('en-IN')}`
              }
            }
          },
          cutout: '68%'
        }
      });

      // 3. Monthly Savings Trend (Line / Area Chart)
      const ctx3 = document.getElementById('savingsTrendChart').getContext('2d');
      new Chart(ctx3, {
        type: 'line',
        data: {
          labels: data.monthly_labels,
          datasets: [{
            label: 'Net Savings (₹)',
            data: data.savings_data,
            fill: true,
            backgroundColor: 'rgba(99, 102, 241, 0.15)',
            borderColor: '#6366f1',
            tension: 0.35,
            borderWidth: 2.5,
            pointBackgroundColor: '#818cf8',
            pointRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { labels: { color: '#94a3b8' } },
            tooltip: {
              callbacks: {
                label: (ctx) => ` Savings: ₹${ctx.raw.toLocaleString('en-IN')}`
              }
            }
          },
          scales: {
            x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
            y: { 
              grid: { color: 'rgba(255, 255, 255, 0.05)' }, 
              ticks: { 
                color: '#94a3b8',
                callback: (val) => '₹' + val.toLocaleString('en-IN')
              } 
            }
          }
        }
      });

      // 4. Budget vs Actual Chart (Grouped Horizontal/Vertical Bar Chart)
      const ctx4 = document.getElementById('budgetVsActualChart').getContext('2d');
      new Chart(ctx4, {
        type: 'bar',
        data: {
          labels: data.budget_labels.length > 0 ? data.budget_labels : ['No Budgets Set'],
          datasets: [
            {
              label: 'Budget Limit (₹)',
              data: data.budget_data.length > 0 ? data.budget_data : [0],
              backgroundColor: 'rgba(99, 102, 241, 0.65)',
              borderColor: '#6366f1',
              borderWidth: 1,
              borderRadius: 6
            },
            {
              label: 'Actual Spent (₹)',
              data: data.actual_data.length > 0 ? data.actual_data : [0],
              backgroundColor: 'rgba(245, 158, 11, 0.65)',
              borderColor: '#f59e0b',
              borderWidth: 1,
              borderRadius: 6
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { labels: { color: '#94a3b8' } },
            tooltip: {
              callbacks: {
                label: (ctx) => ` ${ctx.dataset.label}: ₹${ctx.raw.toLocaleString('en-IN')}`
              }
            }
          },
          scales: {
            x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
            y: { 
              grid: { color: 'rgba(255, 255, 255, 0.05)' }, 
              ticks: { 
                color: '#94a3b8',
                callback: (val) => '₹' + val.toLocaleString('en-IN')
              } 
            }
          }
        }
      });
    })
    .catch(err => {
      console.error('Failed to load chart data:', err);
    });
});
