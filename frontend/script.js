// Fetch real transactions from Flask API
fetch('http://127.0.0.1:5000/api/transactions')
    .then(response => response.json())
    .then(data => {
        // Group by category for visualization
        const counts = {};
        data.forEach(tx => {
            const category = tx.category || "Uncategorized";
            counts[category] = (counts[category] || 0) + 1;
        });

        // Render chart
        const ctx = document.getElementById('categoryChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(counts),
                datasets: [{
                    label: 'Number of Transactions',
                    data: Object.values(counts),
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    })
    .catch(error => console.error('Error fetching transactions:', error));
