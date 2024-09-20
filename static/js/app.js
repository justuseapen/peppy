document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('results');
    const trendingResultsContainer = document.getElementById('trending-results');
    const categoryResultsContainer = document.getElementById('category-results');
    const untaggedResultsContainer = document.getElementById('untagged-results');
    const errorMessage = document.getElementById('error-message');
    const loadingIndicator = document.getElementById('loading');
    const modal = document.getElementById('modal');
    const modalImage = document.getElementById('modal-image');
    const modalTags = document.getElementById('modal-tags');
    const addTagInput = document.getElementById('add-tag-input');
    const addTagButton = document.getElementById('add-tag-button');
    const closeModal = document.getElementById('close-modal');
    const fileUpload = document.getElementById('file-upload');
    const uploadStatus = document.getElementById('upload-status');
    const searchResultsSection = document.getElementById('search-results-section');
    const trendingSection = document.getElementById('trending-section');
    const categoriesSection = document.getElementById('categories-section');
    const untaggedSection = document.getElementById('untagged-section');
    const refreshTrendingButton = document.getElementById('refresh-trending');
    const toggleViewButton = document.getElementById('toggle-view');
    const categoryButtons = document.querySelectorAll('.category-button');
    const uploadProgress = document.getElementById('upload-progress');
    const uploadProgressBar = document.getElementById('upload-progress-bar');
    const dragDropArea = document.getElementById('drag-drop-area');
    const selectedFiles = document.getElementById('selected-files');
    const selectedFilesList = document.getElementById('selected-files-list');

    let currentOffset = 0;
    let currentCategory = '';
    const limit = 20;
    let currentQuery = '';
    let currentImageId = '';
    let currentView = 'trending';
    let isLoading = false;
    let hasMoreResults = true;

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
        hasMoreResults = true;
        if (query === '') {
            searchResultsSection.classList.add('hidden');
            showCurrentView();
            return;
        }

        searchResultsSection.classList.remove('hidden');
        trendingSection.classList.add('hidden');
        categoriesSection.classList.add('hidden');
        untaggedSection.classList.add('hidden');
        showLoading();
        fetchImages(query);
    }, 300);

    const fetchImages = (query) => {
        if (!hasMoreResults || isLoading) return;
        isLoading = true;
        showLoading();
        fetch(`/api/search?q=${encodeURIComponent(query)}&offset=${currentOffset}&limit=${limit}`)
            .then(response => response.json())
            .then(data => {
                hideLoading();
                displayResults(data.images, resultsContainer);
                currentOffset += data.images.length;
                hasMoreResults = data.has_more;
                isLoading = false;
            })
            .catch(error => {
                console.error('Error:', error);
                showError('An error occurred while fetching images. Please try again.');
                hideLoading();
                isLoading = false;
            });
    };

    const fetchTrendingGifs = () => {
        showLoading();
        fetch('/api/trending?limit=8')
            .then(response => response.json())
            .then(data => {
                hideLoading();
                trendingResultsContainer.innerHTML = '';
                displayResults(data, trendingResultsContainer);
            })
            .catch(error => {
                console.error('Error:', error);
                showError('An error occurred while fetching trending GIFs. Please try again.');
                hideLoading();
            });
    };

    const fetchCategoryGifs = (category) => {
        if (!hasMoreResults || isLoading) return;
        isLoading = true;
        showLoading();
        currentCategory = category;
        fetch(`/api/category/${encodeURIComponent(category)}?offset=${currentOffset}&limit=${limit}`)
            .then(response => response.json())
            .then(data => {
                hideLoading();
                displayResults(data, categoryResultsContainer);
                currentOffset += data.length;
                hasMoreResults = data.length === limit;
                isLoading = false;
            })
            .catch(error => {
                console.error('Error:', error);
                showError('An error occurred while fetching category GIFs. Please try again.');
                hideLoading();
                isLoading = false;
            });
    };

    const fetchUntaggedAssets = () => {
        showLoading();
        fetch('/api/untagged')
            .then(response => response.json())
            .then(data => {
                hideLoading();
                untaggedResultsContainer.innerHTML = '';
                displayResults(data, untaggedResultsContainer);
            })
            .catch(error => {
                console.error('Error:', error);
                showError('An error occurred while fetching untagged assets. Please try again.');
                hideLoading();
            });
    };

    const displayResults = (images, container) => {
        errorMessage.classList.add('hidden');

        if (images.length === 0 && currentOffset === 0) {
            showError('No images found. Try a different search term or category.');
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

    const handleFileSelection = (files) => {
        selectedFilesList.innerHTML = '';
        selectedFiles.classList.remove('hidden');
        Array.from(files).forEach(file => {
            const li = document.createElement('li');
            li.textContent = file.name;
            selectedFilesList.appendChild(li);
        });
    };

    const uploadImages = (files) => {
        const totalFiles = files.length;
        let uploadedFiles = 0;
        let failedUploads = 0;

        uploadProgress.classList.remove('hidden');
        uploadProgressBar.style.width = '0%';

        const uploadFile = (file) => {
            const formData = new FormData();
            formData.append('file', file);

            fetch('/api/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || 'An error occurred while uploading the image.');
                    });
                }
                return response.json();
            })
            .then(data => {
                uploadedFiles++;
                updateUploadProgress(uploadedFiles, totalFiles);
                displayResults([data], resultsContainer);
                fetchUntaggedAssets();
            })
            .catch(error => {
                console.error('Error:', error);
                failedUploads++;
                updateUploadProgress(uploadedFiles, totalFiles);
            })
            .finally(() => {
                if (uploadedFiles + failedUploads === totalFiles) {
                    showUploadStatus(`Uploaded ${uploadedFiles} out of ${totalFiles} files.`, uploadedFiles === totalFiles ? 'success' : 'warning');
                    uploadProgress.classList.add('hidden');
                    selectedFiles.classList.add('hidden');
                }
            });
        };

        Array.from(files).forEach(uploadFile);
    };

    const updateUploadProgress = (uploaded, total) => {
        const progress = (uploaded / total) * 100;
        uploadProgressBar.style.width = `${progress}%`;
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
                fetchUntaggedAssets();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('An error occurred while adding tags. Please try again.');
        });
    };

    const showCurrentView = () => {
        if (currentView === 'trending') {
            trendingSection.classList.remove('hidden');
            categoriesSection.classList.add('hidden');
        } else {
            trendingSection.classList.add('hidden');
            categoriesSection.classList.remove('hidden');
        }
        untaggedSection.classList.remove('hidden');
    };

    const handleScroll = () => {
        if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 100) {
            if (currentQuery) {
                fetchImages(currentQuery);
            } else if (currentCategory) {
                fetchCategoryGifs(currentCategory);
            }
        }
    };

    searchInput.addEventListener('input', (e) => performSearch(e.target.value.trim()));

    closeModal.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    fileUpload.addEventListener('change', (e) => {
        const files = e.target.files;
        if (files.length > 0) {
            handleFileSelection(files);
            const validFiles = Array.from(files).filter(file => 
                ['image/png', 'image/jpeg', 'image/gif', 'image/webp'].includes(file.type)
            );
            if (validFiles.length > 0) {
                uploadImages(validFiles);
            } else {
                showUploadStatus('Please upload valid image files (PNG, JPEG, GIF, or WebP).', 'error');
            }
        }
    });

    addTagButton.addEventListener('click', addTags);

    refreshTrendingButton.addEventListener('click', fetchTrendingGifs);

    toggleViewButton.addEventListener('click', () => {
        currentView = currentView === 'trending' ? 'categories' : 'trending';
        showCurrentView();
    });

    categoryButtons.forEach(button => {
        button.addEventListener('click', () => {
            currentOffset = 0;
            categoryResultsContainer.innerHTML = '';
            hasMoreResults = true;
            fetchCategoryGifs(button.textContent);
        });
    });

    window.addEventListener('scroll', debounce(handleScroll, 200));

    dragDropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        dragDropArea.classList.add('bg-green-100');
    });

    dragDropArea.addEventListener('dragleave', () => {
        dragDropArea.classList.remove('bg-green-100');
    });

    dragDropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        dragDropArea.classList.remove('bg-green-100');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelection(files);
            fileUpload.files = files;
            const validFiles = Array.from(files).filter(file => 
                ['image/png', 'image/jpeg', 'image/gif', 'image/webp'].includes(file.type)
            );
            if (validFiles.length > 0) {
                uploadImages(validFiles);
            } else {
                showUploadStatus('Please upload valid image files (PNG, JPEG, GIF, or WebP).', 'error');
            }
        }
    });

    dragDropArea.addEventListener('click', () => {
        fileUpload.click();
    });

    fetchTrendingGifs();
    fetchUntaggedAssets();
});