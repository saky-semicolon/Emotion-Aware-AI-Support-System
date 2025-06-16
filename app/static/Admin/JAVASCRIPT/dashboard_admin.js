// Example complaints data (shared with complaints.js)
const complaints = [
    { id: 1, user: 'Emma', status: 'Pending', priority: 'High', urgency: 'Critical', emotion: 'Angry' },
    { id: 2, user: 'Olivia', status: 'Pending', priority: 'Medium', urgency: 'Moderate', emotion: 'Neutral' },
    { id: 3, user: 'James', status: 'Resolved', priority: 'Low', urgency: 'Low', emotion: 'Happy' }
];

// Updated data for emotions detected from students
const emotions = [
    { name: 'Happy', count: 40, percentage: 40 },
    { name: 'Sad', count: 20, percentage: 20 },
    { name: 'Angry', count: 15, percentage: 15 },
    { name: 'Fear', count: 10, percentage: 10 },
    { name: 'Neutral', count: 15, percentage: 15 }
];

// Function to update complaint counts on the dashboard
function updateDashboardCounts() {
    const totalComplaints = complaints.length;

    // Count complaints with status "Pending" or "In Progress"
    const pendingComplaints = complaints.filter(c => c.status === 'Pending').length;

    // Count complaints with status "Resolved"
    const resolvedComplaints = complaints.filter(c => c.status === 'Resolved').length;

    // Update the dashboard elements
    document.getElementById('totalComplaints').textContent = totalComplaints;
    document.getElementById('pendingComplaints').textContent = pendingComplaints;
    document.getElementById('resolvedComplaints').textContent = resolvedComplaints;
}

// Function to populate the Emotion Distribution Chart
function populateEmotionsChart() {
    const ctx = document.getElementById('emotionsChart').getContext('2d');

    // Extract data for the chart
    const labels = emotions.map(data => data.name);
    const counts = emotions.map(data => data.count);
    const backgroundColors = [
        'rgba(75, 192, 192, 0.6)', // Happy
        'rgba(54, 162, 235, 0.6)', // Sad
        'rgba(255, 99, 132, 0.6)', // Angry
        'rgba(153, 102, 255, 0.6)', // Fear
        'rgba(201, 203, 207, 0.6)'  // Neutral
    ];

    // Create the chart
    new Chart(ctx, {
        type: 'doughnut', // Doughnut chart for better animation
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: backgroundColors,
                borderColor: backgroundColors.map(color => color.replace('0.6', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    enabled: true
                }
            },
            animation: {
                animateScale: true,
                animateRotate: true
            }
        }
    });
}

// Function to populate the Emotion Details Table
function populateEmotionDetails() {
    const tableBody = document.getElementById('emotionDetailsTable').querySelector('tbody');
    tableBody.innerHTML = ''; // Clear existing content

    // Populate the table with emotion details
    emotions.forEach(data => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${data.name}</td>
            <td>${data.count}</td>
            <td>${data.percentage}%</td>
        `;
        tableBody.appendChild(row);
    });
}

// Call the functions to populate the chart and details on page load
document.addEventListener('DOMContentLoaded', () => {
    updateDashboardCounts(); // Ensure complaint counts are updated
    populateEmotionsChart();
    populateEmotionDetails();
});