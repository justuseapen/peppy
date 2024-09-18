document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('results');
    const trendingResultsContainer = document.getElementById('trending-results');
    const errorMessage = document.getElementById('error-message');
    const loadingIndicator = document.getElementById('loading');
    const modal = document.getElementById('modal');
    const modalImage = document.getElementById('modal-image');
    const modalTags = document.getElementById('modal-tags');
    const addTagInput = document.getElementById('add-tag-input');
    const addTagButton = document.getElementById('add-tag-button');
    const closeModal = document.getElementById('close-modal');
    const loadMoreButton = document.getElementById('load-more-button');
    const fileUpload = document.getElementById('file-upload');
    const uploadStatus = document.getElementById('upload-status');
    const searchResultsSection = document.getElementById('search-results-section');
    const trendingSection = document.getElementById('trending-section');

    let currentOffset = 0;
    const limit = 20;
    let currentQuery = '';
    let currentImageId = '';

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
        if (query === '') {
            searchResultsSection.classList.add('hidden');
            trendingSection.classList.remove('hidden');
            return;
        }

        searchResultsSection.classList.remove('hidden');
        trendingSection.classList.add('hidden');
        showLoading();
        fetchImages(query);
    }, 300);

    const fetchImages = (query) => {
        fetch(`/api/search?q=${encodeURIComponent(query)}&offset=${currentOffset}&limit=${limit}`)
            .then(response => response.json())
            .then(data => {
                hideLoading();
                displayResults(data, resultsContainer);
                updateLoadMoreButton(data.length === limit);
                trendingSection.classList.add('hidden');
            })
            .catch(error => {
                console.error('Error:', error);
                showError('An error occurred while fetching images. Please try again.');
                hideLoading();
            });
    };

    const fetchTrendingGifs = () => {
        fetch('/api/trending?limit=8')
            .then(response => response.json())
            .then(data => {
                displayResults(data, trendingResultsContainer);
            })
            .catch(error => {
                console.error('Error:', error);
                showError('An error occurred while fetching trending GIFs. Please try again.');
            });
    };

    const displayResults = (images, container) => {
        errorMessage.classList.add('hidden');

        if (images.length === 0 && currentOffset === 0) {
            showError('No images found. Try a different search term.');
            return;
        }

        images.forEach(image => {
            const imageElement = document.createElement('div');
            imageElement.classList.add('image-item');
            imageElement.innerHTML = `
                <img src="${image.images.fixed_height.url}" alt="${image.title}" class="w-full h-auto rounded-lg shadow-md">
                <div class="mt-2">
                    <p class="font-bold">${image.title}</p>
                    <p class="text-sm text-gray-600">${image.tags.join(', ')}</p>
                </div>
            `;
            imageElement.addEventListener('click', () => showFullSize(image));
            container.appendChild(imageElement);
        });
    };

    const showFullSize = (image) => {
        modalImage.src = image.images.original.url;
        modalImage.alt = image.title;
        currentImageId = image.id;
        updateModalTags(image.tags);
        modal.classList.remove('hidden');
    };

    const updateModalTags = (tags) => {
        modalTags.innerHTML = `
            <p class="font-bold mb-2">Tags:</p>
            <div class="flex flex-wrap">
                ${tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
            </div>
        `;
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

    const uploadImage = (file) => {
        const formData = new FormData();
        formData.append('file', file);

        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showUploadStatus(data.error, 'error');
            } else {
                showUploadStatus('Image uploaded successfully!', 'success');
                displayResults([data], resultsContainer);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showUploadStatus('An error occurred while uploading the image.', 'error');
        });
    };

    const showUploadStatus = (message, type) => {
        uploadStatus.textContent = message;
        uploadStatus.classList.remove('hidden', 'text-green-500', 'text-red-500');
        uploadStatus.classList.add(type === 'success' ? 'text-green-500' : 'text-red-500');
        setTimeout(() => {
            uploadStatus.classList.add('hidden');
        }, 3000);
    };

    const addTags = () => {
        const newTags = addTagInput.value.split(',').map(tag => tag.trim()).filter(tag => tag !== '');
        if (newTags.length === 0) return;

        fetch('/api/add_tags', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image_id: currentImageId,
                tags: newTags
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
            } else {
                updateModalTags(data.tags);
                addTagInput.value = '';
                showUploadStatus('Tags added successfully!', 'success');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('An error occurred while adding tags. Please try again.');
        });
    };

    searchInput.addEventListener('input', (e) => performSearch(e.target.value.trim()));

    closeModal.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    loadMoreButton.addEventListener('click', () => {
        currentOffset += limit;
        showLoading();
        fetchImages(currentQuery);
    });

    fileUpload.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            if (['image/png', 'image/jpeg', 'image/gif', 'image/webp'].includes(file.type)) {
                uploadImage(file);
            } else {
                showUploadStatus('Please upload a valid image file (PNG, JPEG, GIF, or WebP).', 'error');
            }
        }
    });

    addTagButton.addEventListener('click', addTags);

    // Fetch trending GIFs on page load
    fetchTrendingGifs();
});
