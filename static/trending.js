document.addEventListener('DOMContentLoaded', () => {
    const trendingContainer = document.getElementById('trending-container');
    if (!trendingContainer) return;

    // Show loading state
    trendingContainer.innerHTML = `
        <div class="loading-state">
            <div class="spinner"></div>
            <p>Loading trending videos...</p>
        </div>
    `;

    fetch('/api/trending')
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || 'Failed to load trending videos');
                }).catch(() => {
                    throw new Error('Failed to load trending videos');
                });
            }
            return response.json();
        })
        .then(videos => {
            if (!videos || videos.length === 0) {
                trendingContainer.innerHTML = `
                    <div class="error-state">
                        <div class="no-results-icon">😕</div>
                        <p>No trending videos currently available.</p>
                    </div>
                `;
                return;
            }

            // Clear loading state
            trendingContainer.innerHTML = '';

            // Render videos
            videos.forEach(video => {
                const videoCard = createVideoCard(video);
                trendingContainer.appendChild(videoCard);
            });
        })
        .catch(error => {
            console.error('Error fetching trending videos:', error);

            // Show toast error
            if (window.showError) {
                window.showError(error.message);
            }

            trendingContainer.innerHTML = `
                <div class="error-state">
                    <div class="no-results-icon">⚠️</div>
                    <p>Failed to load trending content.</p>
                    <button onclick="location.reload()" class="back-home-button" style="margin-top: 1rem; font-size: 0.9rem; padding: 0.5rem 1rem;">Retry</button>
                </div>
            `;
        });
});

function createVideoCard(video) {
    const card = document.createElement('article');
    card.className = 'video-card';

    card.innerHTML = `
        <a href="/watch?v=${video.id}" class="video-link">
            <div class="video-thumbnail-wrapper">
                <img src="${video.thumbnail}" alt="${video.title}" class="video-thumbnail" loading="lazy">
                <span class="video-duration">${video.duration}</span>
            </div>
            <div class="video-info">
                <h2 class="video-title" title="${video.title}">
                    ${video.title}
                </h2>
                <div class="video-meta">
                    <p class="video-channel">${video.channel}</p>
                    <p class="video-stats">${video.view_count}</p>
                </div>
            </div>
        </a>
    `;

    return card;
}
