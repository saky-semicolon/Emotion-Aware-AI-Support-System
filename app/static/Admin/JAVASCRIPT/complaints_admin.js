// Example complaints data (replace with backend API calls if needed)
const complaints = [
    { id: 1, user: 'Emma', status: 'Pending', priority: 'High', emotion: 'Angry', message: 'System is slow.' },
    { id: 2, user: 'Olivia', status: 'Resolved', priority: 'Medium', emotion: 'Neutral', message: 'Issue with login.' },
    { id: 3, user: 'James', status: 'Pending', priority: 'Low', emotion: 'Happy', message: 'Request for feature.' }
];

// Function to populate the complaints table
function populateComplaintsTable(filteredComplaints = complaints) {
    const tableBody = document.getElementById('complaintTable').querySelector('tbody');
    tableBody.innerHTML = ''; // Clear existing content

    filteredComplaints.forEach(complaint => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${complaint.id}</td>
            <td>${complaint.user}</td>
            <td>${complaint.status}</td>
            <td>${complaint.priority}</td>
            <td>${complaint.emotion}</td>
            <td>
                <button onclick="downloadReport(${complaint.id})">Download Report</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

// Function to filter complaints by priority
function filterComplaintsByPriority() {
    const priorityFilter = document.getElementById('priorityFilter').value;

    if (priorityFilter === 'all') {
        populateComplaintsTable(); // Show all complaints
    } else {
        const filteredComplaints = complaints.filter(
            complaint => complaint.priority.toLowerCase() === priorityFilter
        );
        populateComplaintsTable(filteredComplaints);
    }
}

// Function to open the reply modal
function openReplyModal(complaintId) {
    const modal = document.getElementById('replyModal');
    modal.style.display = 'block';
    modal.dataset.complaintId = complaintId; // Store the complaint ID in the modal
}

// Function to close the reply modal
function closeReplyModal() {
    const modal = document.getElementById('replyModal');
    modal.style.display = 'none';
}

// Function to submit the reply
function submitReply() {
    const modal = document.getElementById('replyModal');
    const complaintId = modal.dataset.complaintId;
    const replyMessage = document.getElementById('replyMessage').value;

    if (replyMessage.trim() === '') {
        alert('Please enter a reply message.');
        return;
    }

    // Simulate resolving the complaint
    const complaint = complaints.find(c => c.id === parseInt(complaintId));
    if (complaint) {
        complaint.status = 'Resolved';
    }

    // Update the table and close the modal
    populateComplaintsTable();
    closeReplyModal();
    document.getElementById('replyMessage').value = '';
}

// Function to download a report for a complaint
function downloadReport(complaintId) {
    const complaint = complaints.find(c => c.id === complaintId);
    if (!complaint) {
        alert('Complaint not found.');
        return;
    }

    // Create a report as a text file
    const reportContent = `
        Complaint Report
        ----------------
        ID: ${complaint.id}
        User: ${complaint.user}
        Status: ${complaint.status}
        Priority: ${complaint.priority}
        Emotion: ${complaint.emotion}
        Message: ${complaint.message || 'No message provided.'}
    `;

    // Create a Blob and download it
    const blob = new Blob([reportContent], { type: 'text/plain' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `Complaint_${complaint.id}_Report.txt`;
    link.click();
}

// Populate the table on page load
document.addEventListener('DOMContentLoaded', () => {
    populateComplaintsTable();
});

function updateStatus(complaintId, newStatus) {
    console.log(complaintId, newStatus);  // Debugging line

    // Send the new status to the backend to update the database
    fetch(`/update_status/${complaintId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Status updated successfully');
            // Update the status in the table without reloading
            const row = document.querySelector(`tr[data-complaint-id="${complaintId}"]`);
            const statusCell = row.querySelector('.status-dropdown');
            statusCell.value = newStatus;  // Update the dropdown value
            row.querySelector('td:nth-child(3)').textContent = newStatus;  // Update the text in the status column
        } else {
            alert('Error updating status');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the status.');
    });
}
