// Infinite scroll functionality for YouTube-style results
class InfiniteScroll {
    constructor() {
        this.currentPage = 1;
        this.loading = false;
        this.hasMore = true;
        this.query = this.getQueryFromURL();
        this.container = document.getElementById('results-list');

        if (this.query && this.container) {
            this.init();
        }
    }

    init() {
        window.addEventListener('scroll', () => this.handleScroll());
        this.createLoadingIndicator();
    }

    getQueryFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('q');
    }

    createLoadingIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'loading-indicator';
        indicator.className = 'yt-loading-container';
        indicator.innerHTML = `
            <div class="yt-spinner"></div>
            <p>Loading more results...</p>
        `;
        indicator.style.display = 'none';
        this.container.parentNode.appendChild(indicator);
    }

    handleScroll() {
        if (this.loading || !this.hasMore) return;
        const scrollPosition = window.innerHeight + window.scrollY;
        const pageHeight = document.documentElement.scrollHeight;
        if (scrollPosition >= pageHeight - 500) this.loadMore();
    }

    async loadMore() {
        if (this.loading || !this.hasMore) return;
        this.loading = true;
        this.showLoading();

        try {
            this.currentPage++;
            const offset = (this.currentPage - 1) * 10;
            const response = await fetch(`/api/search-more?q=${encodeURIComponent(this.query)}&offset=${offset}`);
            const data = await response.json();

            if (data.videos && data.videos.length > 0) {
                this.appendVideos(data.videos);
            } else {
                this.hasMore = false;
            }
        } catch (error) {
            console.error('Error loading more:', error);
        } finally {
            this.loading = false;
            this.hideLoading();
        }
    }

    appendVideos(videos) {
        videos.forEach(video => {
            const card = document.createElement('article');
            card.className = 'yt-result-card';
            card.innerHTML = `
                <a href="/watch?v=${video.id}" class="yt-result-card-link" aria-label="${video.title}">
                    <div class="yt-result-thumbnail-wrapper">
                        <img src="${video.thumbnail}" alt="${video.title}" class="yt-result-thumbnail" loading="lazy">
                        ${video.duration ? `<span class="yt-duration">${video.duration}</span>` : ''}
                    </div>
                    <div class="yt-result-info">
                        <h3 class="yt-result-title" title="${video.title}">${video.title}</h3>
                        <div class="yt-result-meta">
                            <span class="yt-result-views">${video.view_count}</span>
                        </div>
                        <div class="yt-result-channel">
                            <div class="yt-result-channel-icon">
                                <span>${video.channel ? video.channel[0].toUpperCase() : 'V'}</span>
                            </div>
                            <span class="yt-result-channel-name">${video.channel}</span>
                        </div>
                    </div>
                </a>
            `;
            this.container.appendChild(card);
        });
    }

    showLoading() { document.getElementById('loading-indicator').style.display = 'flex'; }
    hideLoading() { document.getElementById('loading-indicator').style.display = 'none'; }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('results-list')) new InfiniteScroll();
});
