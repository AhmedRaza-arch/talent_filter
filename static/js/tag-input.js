document.addEventListener('DOMContentLoaded', function() {
    // Find all tag input containers
    const tagInputContainers = document.querySelectorAll('.tag-input-container');

    // Prevent form submission on Enter key
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && e.target.classList.contains('tag-input')) {
                e.preventDefault();
                return false;
            }
        });
    });

    tagInputContainers.forEach(container => {
        const input = container.querySelector('input.tag-input');
        const tagsContainer = container.querySelector('.tags-container');
        const hiddenInput = container.querySelector('input[type="hidden"]');

        if (!input || !tagsContainer || !hiddenInput) return;

        // Initialize tags from hidden input value
        let tags = [];
        if (hiddenInput.value) {
            tags = hiddenInput.value.split(',').map(tag => tag.trim()).filter(tag => tag);
            renderTags();
        }

        // Add event listener for keydown on the input
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault();
                e.stopPropagation();
                addTag();
                return false;
            } else if (e.key === 'Backspace' && input.value === '' && tags.length > 0) {
                // Remove the last tag when backspace is pressed on an empty input
                tags.pop();
                renderTags();
                updateHiddenInput();
            }
        });

        // Add event listener for blur on the input
        input.addEventListener('blur', function() {
            addTag();
        });

        // Function to add a tag
        function addTag() {
            const value = input.value.trim();
            if (value && !tags.includes(value)) {
                tags.push(value);
                renderTags();
                updateHiddenInput();
            }
            input.value = '';
        }

        // Function to render tags
        function renderTags() {
            tagsContainer.innerHTML = '';
            tags.forEach((tag, index) => {
                const tagElement = document.createElement('span');
                tagElement.className = 'tag is-primary is-medium';
                tagElement.textContent = tag;

                const deleteButton = document.createElement('button');
                deleteButton.className = 'delete is-small';
                deleteButton.addEventListener('click', function() {
                    tags.splice(index, 1);
                    renderTags();
                    updateHiddenInput();
                });

                tagElement.appendChild(deleteButton);
                tagsContainer.appendChild(tagElement);
            });
        }

        // Function to update the hidden input
        function updateHiddenInput() {
            hiddenInput.value = tags.join(', ');
        }
    });
});
