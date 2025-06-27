// Example data for notifications
const notifications = [
    { "title": "System Update", "message": "The system will be down for maintenance at 10 PM.", "timestamp": "2025-05-04 14:00" },
    { "title": "New Complaint", "message": "A new complaint has been submitted by John.", "timestamp": "2025-05-04 13:45" }
];

// Populate notifications list
function populateNotifications() {
    const notificationsList = document.getElementById('notificationsList');
    notificationsList.innerHTML = ''; // Clear existing notifications

    notifications.forEach(notification => {
        const listItem = document.createElement('li');
        listItem.className = 'notification-item';
        listItem.textContent = `${notification.title}: ${notification.message} (${notification.timestamp})`;
        notificationsList.appendChild(listItem);
    });
}

// Initialize notifications page
document.addEventListener('DOMContentLoaded', populateNotifications);