// Notification handling

document.addEventListener('DOMContentLoaded', function() {
    // Get all notifications
    const notifications = document.querySelectorAll('.notification');

    // Add auto-hide progress bar and set up auto-hide
    notifications.forEach(notification => {
        // Add progress bar
        const progressBar = document.createElement('div');
        progressBar.classList.add('auto-hide-progress');
        notification.appendChild(progressBar);

        // Set up delete button
        const deleteButton = notification.querySelector('.delete');
        if (deleteButton) {
            deleteButton.addEventListener('click', () => {
                hideNotification(notification);
            });
        }

        // Auto-hide after 5 seconds
        setTimeout(() => {
            hideNotification(notification);
        }, 5000);
    });

    // Function to hide notification with animation
    function hideNotification(notification) {
        notification.style.animation = 'fadeOut 0.5s ease-out forwards';

        // Remove from DOM after animation completes
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 500);
    }

    // Handle new notifications that might be added dynamically
    // This is useful for AJAX responses that might add new messages
    const messagesContainer = document.querySelector('.messages');
    if (messagesContainer) {
        // Create a MutationObserver to watch for new notifications
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.classList && node.classList.contains('notification')) {
                            // Add progress bar
                            const progressBar = document.createElement('div');
                            progressBar.classList.add('auto-hide-progress');
                            node.appendChild(progressBar);

                            // Set up delete button
                            const deleteButton = node.querySelector('.delete');
                            if (deleteButton) {
                                deleteButton.addEventListener('click', () => {
                                    hideNotification(node);
                                });
                            }

                            // Auto-hide after 5 seconds
                            setTimeout(() => {
                                hideNotification(node);
                            }, 5000);
                        }
                    });
                }
            });
        });

        // Start observing the messages container
        observer.observe(messagesContainer, { childList: true });
    }
});
