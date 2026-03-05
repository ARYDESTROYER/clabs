// Function to scroll to the top of the page
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'instant' });
}

// Function to scroll to the bottom of the page
function scrollToBottom() {
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'instant' });
}

// Function to trigger an alert
function showAlert() {
    window.alert("Alert triggered!");
}
