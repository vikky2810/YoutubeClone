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
        .then(response => response.json())
        .then(videos => {
            if (!videos || videos.length === 0) {
                trendingContainer.innerHTML = `
                    <div class="error-state">
                        <p>Could not load trending videos at the moment.</p>
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
            trendingContainer.innerHTML = `
                <div class="error-state">
                    <p>Failed to load trending content.</p>
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
