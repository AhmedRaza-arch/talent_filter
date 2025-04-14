// JavaScript for authentication pages (login, signup)

// Add auth-section class to the section element when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Find the section element that contains our login background
    const section = document.querySelector('.section');
    if (section) {
        section.classList.add('auth-section');
        console.log('Added auth-section class to section');
    } else {
        console.error('Could not find section element');
    }

    // Ensure the login card has proper dimensions
    const loginCard = document.querySelector('.login-card');
    if (loginCard) {
        // Make sure the card is visible and properly sized
        loginCard.style.display = 'block';
        console.log('Login card found and styled');
    }
});
