// Theme Switcher for Talent Filter

document.addEventListener('DOMContentLoaded', () => {
    // Check for saved theme preference or use default
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    // Apply the theme
    applyTheme(currentTheme);
    
    // Set up theme toggle button if it exists
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            // Toggle between light and dark themes
            const newTheme = document.body.classList.contains('is-dark-theme') ? 'light' : 'dark';
            applyTheme(newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
});

// Function to apply theme
function applyTheme(theme) {
    if (theme === 'dark') {
        document.body.classList.add('is-dark-theme');
        updateThemeIcon('sun');
    } else {
        document.body.classList.remove('is-dark-theme');
        updateThemeIcon('moon');
    }
}

// Update the theme toggle icon
function updateThemeIcon(icon) {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        // Clear existing icon
        themeToggle.innerHTML = '';
        
        // Add new icon
        const iconElement = document.createElement('i');
        iconElement.className = `fa fa-${icon}`;
        themeToggle.appendChild(iconElement);
    }
}
