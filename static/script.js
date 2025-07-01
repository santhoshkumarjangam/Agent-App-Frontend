document.addEventListener('DOMContentLoaded', function() {
    // --- Elements for the Delete Confirmation Modal ---
    const confirmationModal = document.getElementById('confirmationModal');
    const modalMessage = document.getElementById('modalMessage');
    const confirmDeleteBtn = document.getElementById('confirmDelete');
    const cancelDeleteBtn = document.getElementById('cancelDelete');
    const closeButton = document.querySelector('.modal .close-button');

    let agentToDeleteCard = null; // Variable to store the specific agent card to be deleted

    // --- Event Listeners for all Delete Buttons ---
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            agentToDeleteCard = this.closest('.agent-card'); // Get the parent agent card element
            const agentName = this.dataset.agentName; // Get the agent name from data-agent-name attribute

            modalMessage.textContent = `Are you sure you want to delete the agent "${agentName}"? This action cannot be undone.`;
            confirmationModal.classList.add('show'); // Show the modal (using flex to center)
        });
    });

    // --- Event Listeners for Modal Buttons ---
    closeButton.addEventListener('click', function() {
        confirmationModal.classList.remove('show'); // Hide the modal
        agentToDeleteCard = null; // Reset the stored card
    });

    cancelDeleteBtn.addEventListener('click', function() {
        confirmationModal.classList.remove('show'); // Hide the modal
        agentToDeleteCard = null; // Reset the stored card
    });

    confirmDeleteBtn.addEventListener('click', async function() {
        if (agentToDeleteCard) {
            const agentId = agentToDeleteCard.dataset.agentId;
            const agentType = agentToDeleteCard.dataset.agentType;
            const agentName = agentToDeleteCard.querySelector('.agent-name').textContent; // Get the name for logging

            console.log(`Attempting to delete ${agentType} agent: ID=${agentId}, Name=${agentName}`);

            try {
                // --- Send DELETE request to your Flask backend ---
                // IMPORTANT: Replace '/delete_agent' with your actual Flask endpoint
                // and adjust the data sent based on what your backend expects.
                const response = await fetch('/delete', { // Example endpoint
                    method: 'POST', // Or 'DELETE' if your Flask route is set up for DELETE requests
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        id: agentId,
                        type: agentType
                    })
                });

                if (response.ok) {
                    const result = await response.json(); // Assuming your backend sends a JSON response
                    console.log('Backend response:', result);

                    if (result.success) {
                        // --- If deletion successful on backend, remove from DOM ---
                        window.location.href = "/";
                    } else {
                        // Backend indicated an error
                        alert(`Failed to delete agent "${agentName}": ${result.message || 'Unknown error'}`);
                        console.error('Backend deletion failed:', result.message);
                    }
                } else {
                    // HTTP error (e.g., 404, 500)
                    const errorText = await response.text();
                    alert(`Error deleting agent "${agentName}": ${response.status} ${response.statusText}\n${errorText}`);
                    console.error('HTTP error during deletion:', response.status, response.statusText, errorText);
                }
            } catch (error) {
                // Network error or other fetch-related issues
                alert(`Network error during deletion of agent "${agentName}". Please try again.`);
                console.error('Fetch error:', error);
            } finally {
                // Always hide the modal and reset the stored card, regardless of success/failure
                confirmationModal.classList.remove('show');
                agentToDeleteCard = null;
            }
        }
    });

    // --- Close modal if user clicks outside of modal content ---
    window.addEventListener('click', function(event) {
        if (event.target == confirmationModal) {
            confirmationModal.classList.remove('show');
            agentToDeleteCard = null;
        }
    });

    // --- Existing JavaScript for dropdown toggle (from your previous code) ---
    const dropdownToggle = document.getElementById('dropdownToggle');
    const createBtn = document.querySelector('.create-btn');
    const chevron = document.querySelector('.create-btn .chevron');

    dropdownToggle.addEventListener('change', function() {
        if (this.checked) {
            chevron.style.transform = 'rotate(180deg)';
        } else {
            chevron.style.transform = 'rotate(0deg)';
        }
    });

    document.addEventListener('click', function(event) {
        const isClickInside = createBtn.contains(event.target) || dropdownToggle.contains(event.target);
        if (!isClickInside && dropdownToggle.checked) {
            dropdownToggle.checked = false;
            chevron.style.transform = 'rotate(0deg)';
        }
    });
});