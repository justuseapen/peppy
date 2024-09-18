document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const resultsContainer = document.getElementById('results');
    const errorMessage = document.getElementById('error-message');
    const modal = document.getElementById('modal');
    const modalImage = document.getElementById('modal-image');
    const closeModal = document.getElementById('close-modal');

    searchButton.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    closeModal.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    function performSearch() {
        const query = searchInput.value.trim();
        if (query === '') return;

        fetch(`/api/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                displayResults(data);
            })
            .catch(error => {
                console.error('Error:', error);
                showError('An error occurred while fetching GIFs. Please try again.');
            });
    }

    function displayResults(gifs) {
        resultsContainer.innerHTML = '';
        errorMessage.classList.add('hidden');

        if (gifs.length === 0) {
            showError('No GIFs found. Try a different search term.');
            return;
        }

        gifs.forEach(gif => {
            const gifElement = document.createElement('div');
            gifElement.classList.add('gif-item');
            gifElement.innerHTML = `
                <img src="${gif.images.fixed_height.url}" alt="${gif.title}" class="w-full h-auto rounded-lg shadow-md">
            `;
            gifElement.addEventListener('click', () => showFullSize(gif));
            resultsContainer.appendChild(gifElement);
        });
    }

    function showFullSize(gif) {
        modalImage.src = gif.images.original.url;
        modal.classList.remove('hidden');
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
    }
});
