let transactions = [];

function fetchAllTransactions() {
  fetch('http://localhost:5000/api/transactions')
    .then(res => res.json())
    .then(data => {
      transactions = data;
      populateTable(data);
    });
}

function handleSearch(query) {
  fetch(`http://localhost:5000/api/search?query=${encodeURIComponent(query)}`)
    .then(res => res.json())
    .then(data => {
      document.getElementById('noResultMsg').classList.toggle('hidden', data.length > 0);
      populateTable(data);
    });
}

function filterData() {
  const value = document.getElementById('searchBox').value;
  handleSearch(value);
}

function populateTable(data) {
  const tbody = document.querySelector('#transactionTable tbody');
  tbody.innerHTML = '';
  data.forEach(txn => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${txn.type}</td>
      <td>${txn.amount}</td>
      <td>${txn.party}</td>
      <td>${txn.tx_id || 'N/A'}</td>
      <td>${txn.date || 'N/A'}</td>
    `;
    tbody.appendChild(tr);
  });
}

// Color Palette for Each Transaction Category
const categoryColors = {
  "Incoming Money": "#4CAF50",     // Green
  "Payment": "#FF9800",            // Orange
  "Bank Deposit": "#2196F3",       // Blue
  "Peer Transfer": "#9C27B0",      // Purple
  "Airtime Purchase": "#FF5722",   // Deep Orange
  "Withdrawal": "#F44336",         // Red
  "Cash Power Payment": "#795548", // Brown
  "Bundle Purchase": "#009688",    // Teal
  "Bank Transfer": "#3F51B5"       // Indigo
};

function drawCharts() {
  fetch('http://localhost:5000/api/summary')
    .then(res => res.json())
    .then(summary => {
      const typeData = summary.type_summary;
      const monthData = summary.monthly_summary;

      const types = Object.keys(typeData);
      const amounts = Object.values(typeData);
      const colors = types.map(type => categoryColors[type] || getRandomColor());

      new Chart(document.getElementById('typeChart'), {
        type: 'bar',
        data: {
          labels: types,
          datasets: [{
            label: 'Total Amount by Type',
            data: amounts,
            backgroundColor: colors
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
            tooltip: { callbacks: { label: ctx => `${ctx.dataset.label}: ${ctx.formattedValue} RWF` } }
          }
        }
      });

      new Chart(document.getElementById('monthlyChart'), {
        type: 'line',
        data: {
          labels: Object.keys(monthData),
          datasets: [{
            label: 'Monthly Summary',
            data: Object.values(monthData),
            borderColor: "#4CAF50",
            fill: false,
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          plugins: {
            tooltip: { callbacks: { label: ctx => `${ctx.dataset.label}: ${ctx.formattedValue} RWF` } }
          }
        }
      });

      new Chart(document.getElementById('pieChart'), {
        type: 'pie',
        data: {
          labels: types,
          datasets: [{
            label: 'Distribution by Type',
            data: amounts,
            backgroundColor: colors
          }]
        },
        options: {
          responsive: true,
          plugins: {
            tooltip: { callbacks: { label: ctx => `${ctx.label}: ${ctx.formattedValue} RWF `} }
          }
        }
      });
    });
}

function getRandomColor() {
  const hue = Math.floor(Math.random() * 360);
  return `hsl(${hue}, 70%, 60%)`;
}

window.onload = function () {
  fetchAllTransactions();
  drawCharts();
};