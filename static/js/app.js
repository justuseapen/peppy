document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('results');
    const errorMessage = document.getElementById('error-message');
    const loadingIndicator = document.getElementById('loading');
    const modal = document.getElementById('modal');
    const modalImage = document.getElementById('modal-image');
    const closeModal = document.getElementById('close-modal');
    const loadMoreButton = document.getElementById('load-more-button');

    let currentOffset = 0;
    const limit = 20;
    let currentQuery = '';

    const debounce = (func, delay) => {
        let timeoutId;
        return (...args) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(null, args), delay);
        };
    };

    const performSearch = debounce((query) => {
        currentQuery = query;
        currentOffset = 0;
        resultsContainer.innerHTML = '';
        if (query === '') return;

        showLoading();
        fetchGifs(query);
    }, 300);

    const fetchGifs = (query) => {
        fetch(`/api/search?q=${encodeURIComponent(query)}&offset=${currentOffset}&limit=${limit}`)
            .then(response => response.json())
            .then(data => {
                hideLoading();
                displayResults(data);
                updateLoadMoreButton(data.length === limit);
            })
            .catch(error => {
                console.error('Error:', error);
                showError('An error occurred while fetching GIFs. Please try again.');
                hideLoading();
            });
    };

    const displayResults = (gifs) => {
        errorMessage.classList.add('hidden');

        if (gifs.length === 0 && currentOffset === 0) {
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
    };

    const showFullSize = (gif) => {
        modalImage.src = gif.images.original.url;
        modal.classList.remove('hidden');
    };

    const showError = (message) => {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
    };

    const showLoading = () => {
        loadingIndicator.classList.remove('hidden');
    };

    const hideLoading = () => {
        loadingIndicator.classList.add('hidden');
    };

    const updateLoadMoreButton = (show) => {
        if (show) {
            loadMoreButton.parentElement.classList.remove('hidden');
        } else {
            loadMoreButton.parentElement.classList.add('hidden');
        }
    };

    searchInput.addEventListener('input', (e) => performSearch(e.target.value.trim()));

    closeModal.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    loadMoreButton.addEventListener('click', () => {
        currentOffset += limit;
        showLoading();
        fetchGifs(currentQuery);
    });
});
