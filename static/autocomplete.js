// Autocomplete functionality for search inputs

class SearchAutocomplete {
    constructor(inputElement, formElement) {
        this.input = inputElement;
        this.form = formElement;
        this.dropdown = null;
        this.suggestions = [];
        this.selectedIndex = -1;
        this.debounceTimer = null;

        this.init();
    }

    init() {
        // Create dropdown element
        this.createDropdown();

        // Add event listeners
        this.input.addEventListener('input', (e) => this.handleInput(e));
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        this.input.addEventListener('focus', (e) => this.handleFocus(e));

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.dropdown.contains(e.target)) {
                this.hideDropdown();
            }
        });
    }

    createDropdown() {
        this.dropdown = document.createElement('div');
        this.dropdown.className = 'autocomplete-dropdown';
        this.dropdown.style.display = 'none';

        // Insert dropdown after the input's parent container
        const container = this.input.closest('.search-container, .header-search-container');
        if (container) {
            container.parentNode.insertBefore(this.dropdown, container.nextSibling);
        }
    }

    handleInput(e) {
        const query = e.target.value.trim();

        // Clear previous timer
        clearTimeout(this.debounceTimer);

        if (query.length < 2) {
            this.hideDropdown();
            return;
        }

        // Debounce API calls (wait 300ms after user stops typing)
        this.debounceTimer = setTimeout(() => {
            this.fetchSuggestions(query);
        }, 300);
    }

    async fetchSuggestions(query) {
        try {
            const response = await fetch(`/api/autocomplete?q=${encodeURIComponent(query)}`);
            const suggestions = await response.json();

            this.suggestions = suggestions;
            this.displaySuggestions(suggestions);
        } catch (error) {
            console.error('Error fetching suggestions:', error);
            this.hideDropdown();
        }
    }

    displaySuggestions(suggestions) {
        if (!suggestions || suggestions.length === 0) {
            this.hideDropdown();
            return;
        }

        this.dropdown.innerHTML = '';
        this.selectedIndex = -1;

        suggestions.forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.textContent = suggestion;
            item.dataset.index = index;

            // Click handler
            item.addEventListener('click', () => {
                this.selectSuggestion(suggestion);
            });

            // Hover handler
            item.addEventListener('mouseenter', () => {
                this.highlightItem(index);
            });

            this.dropdown.appendChild(item);
        });

        this.showDropdown();
    }

    handleKeydown(e) {
        if (!this.dropdown || this.dropdown.style.display === 'none') {
            return;
        }

        const items = this.dropdown.querySelectorAll('.autocomplete-item');

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, items.length - 1);
                this.highlightItem(this.selectedIndex);
                break;

            case 'ArrowUp':
                e.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                if (this.selectedIndex === -1) {
                    this.clearHighlight();
                } else {
                    this.highlightItem(this.selectedIndex);
                }
                break;

            case 'Enter':
                if (this.selectedIndex >= 0 && this.selectedIndex < this.suggestions.length) {
                    e.preventDefault();
                    this.selectSuggestion(this.suggestions[this.selectedIndex]);
                }
                break;

            case 'Escape':
                this.hideDropdown();
                break;
        }
    }

    handleFocus(e) {
        const query = e.target.value.trim();
        if (query.length >= 2 && this.suggestions.length > 0) {
            this.showDropdown();
        }
    }

    highlightItem(index) {
        const items = this.dropdown.querySelectorAll('.autocomplete-item');
        items.forEach((item, i) => {
            if (i === index) {
                item.classList.add('active');
                // Scroll item into view if needed
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('active');
            }
        });
    }

    clearHighlight() {
        const items = this.dropdown.querySelectorAll('.autocomplete-item');
        items.forEach(item => item.classList.remove('active'));
    }

    selectSuggestion(suggestion) {
        this.input.value = suggestion;
        this.hideDropdown();
        this.form.submit();
    }

    showDropdown() {
        this.dropdown.style.display = 'block';
    }

    hideDropdown() {
        this.dropdown.style.display = 'none';
        this.selectedIndex = -1;
    }
}

// Initialize autocomplete on page load
document.addEventListener('DOMContentLoaded', () => {
    // Home page search
    const homeSearchInput = document.querySelector('.search-input');
    const homeSearchForm = document.querySelector('.search-form');
    if (homeSearchInput && homeSearchForm) {
        new SearchAutocomplete(homeSearchInput, homeSearchForm);
    }

    // Header search (on results and watch pages)
    const headerSearchInput = document.querySelector('.header-search-input');
    const headerSearchForm = document.querySelector('.header-search-form');
    if (headerSearchInput && headerSearchForm) {
        new SearchAutocomplete(headerSearchInput, headerSearchForm);
    }
});
