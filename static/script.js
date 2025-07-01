document.addEventListener('DOMContentLoaded', function() {
    // --- Elements for the Delete Confirmation Modal ---
    const confirmationModal = document.getElementById('confirmationModal');
    const modalMessage = document.getElementById('modalMessage');
    const confirmDeleteBtn = document.getElementById('confirmDelete');
    const cancelDeleteBtn = document.getElementById('cancelDelete');
    const closeButton = document.querySelector('.modal .close-button');

    let agentToDeleteCard = null;

    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            agentToDeleteCard = this.closest('.agent-card');
            const agentName = this.dataset.agentName;

            modalMessage.textContent = `Are you sure you want to delete the agent "${agentName}"? This action cannot be undone.`;
            confirmationModal.classList.add('show');
        });
    });

    confirmDeleteBtn.addEventListener('click', async function() {
        if (agentToDeleteCard) {
            const agentId = agentToDeleteCard.dataset.agentId;
            const agentType = agentToDeleteCard.dataset.agentType;
            const agentName = agentToDeleteCard.querySelector('.agent-name').textContent;
            
            console.log(`Attempting to delete ${agentType} agent: ID=${agentId}, Name=${agentName}`);
            
            window.location.href = `/delete/${agentType}/${agentId}`;
        }
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