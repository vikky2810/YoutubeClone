// Infinite scroll functionality for loading more search results

class InfiniteScroll {
    constructor() {
        this.currentPage = 1;
        this.loading = false;
        this.hasMore = true;
        this.query = this.getQueryFromURL();

        if (this.query) {
            this.init();
        }
    }

    init() {
        // Add scroll event listener
        window.addEventListener('scroll', () => this.handleScroll());

        // Create loading indicator
        this.createLoadingIndicator();
    }

    getQueryFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('q');
    }

    createLoadingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'loading-indicator';
        indicator.id = 'loading-indicator';
        indicator.innerHTML = `
            <div class="loading-spinner"></div>
            <p>Loading more videos...</p>
        `;
        indicator.style.display = 'none';

        const container = document.querySelector('.container');
        if (container) {
            container.appendChild(indicator);
        }
    }

    handleScroll() {
        if (this.loading || !this.hasMore) return;

        // Check if user is near bottom of page
        const scrollPosition = window.innerHeight + window.scrollY;
        const pageHeight = document.documentElement.scrollHeight;
        const threshold = 300; // pixels from bottom

        if (scrollPosition >= pageHeight - threshold) {
            this.loadMore();
        }
    }

    async loadMore() {
        if (this.loading || !this.hasMore) return;

        this.loading = true;
        this.showLoading();

        try {
            this.currentPage++;
            const offset = (this.currentPage - 1) * 10;

            // Fetch more results
            const response = await fetch(`/api/search-more?q=${encodeURIComponent(this.query)}&offset=${offset}`);
            const data = await response.json();

            if (data.videos && data.videos.length > 0) {
                this.appendVideos(data.videos);
            } else {
                this.hasMore = false;
                this.showNoMoreResults();
            }
        } catch (error) {
            console.error('Error loading more videos:', error);
            this.showError();
        } finally {
            this.loading = false;
            this.hideLoading();
        }
    }

    appendVideos(videos) {
        const grid = document.querySelector('.video-grid');
        if (!grid) return;

        videos.forEach(video => {
            const videoCard = this.createVideoCard(video);
            grid.appendChild(videoCard);
        });

        // Animate new cards
        const newCards = grid.querySelectorAll('.video-card:not(.animated)');
        newCards.forEach((card, index) => {
            card.classList.add('animated');
            card.style.animation = `fadeInUp 0.6s ease ${index * 0.1}s backwards`;
        });
    }

    createVideoCard(video) {
        const article = document.createElement('article');
        article.className = 'video-card';

        article.innerHTML = `
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

        return article;
    }

    showLoading() {
        const indicator = document.getElementById('loading-indicator');
        if (indicator) {
            indicator.style.display = 'block';
        }
    }

    hideLoading() {
        const indicator = document.getElementById('loading-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }

    showNoMoreResults() {
        const indicator = document.getElementById('loading-indicator');
        if (indicator) {
            indicator.innerHTML = `
                <div class="no-more-results">
                    <p>✓ All results loaded</p>
                </div>
            `;
            indicator.style.display = 'block';

            setTimeout(() => {
                indicator.style.display = 'none';
            }, 3000);
        }
    }

    showError() {
        const indicator = document.getElementById('loading-indicator');
        if (indicator) {
            indicator.innerHTML = `
                <div class="error-message">
                    <p>❌ Error loading more videos</p>
                    <button onclick="location.reload()">Retry</button>
                </div>
            `;
            indicator.style.display = 'block';
        }
    }
}

// Initialize infinite scroll on page load
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize on results page
    if (document.querySelector('.video-grid')) {
        new InfiniteScroll();
    }
});
