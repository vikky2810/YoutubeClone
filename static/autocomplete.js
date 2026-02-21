// Autocomplete functionality for YouTube-style search inputs
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
        this.createDropdown();
        this.input.addEventListener('input', (e) => this.handleInput(e));
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        this.input.addEventListener('focus', (e) => this.handleFocus(e));

        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.dropdown.contains(e.target)) {
                this.hideDropdown();
            }
        });
    }

    createDropdown() {
        this.dropdown = document.createElement('div');
        this.dropdown.className = 'yt-autocomplete-dropdown';
        this.dropdown.style.cssText = `
            position: absolute;
            background: #212121;
            width: 100%;
            border-radius: 0 0 12px 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
            z-index: 2000;
            display: none;
            overflow: hidden;
            border: 1px solid #333;
            border-top: none;
        `;

        const container = this.input.closest('.yt-search-box, .yt-hero-search-box');
        if (container) {
            container.appendChild(this.dropdown);
        }
    }

    handleInput(e) {
        const query = e.target.value.trim();
        clearTimeout(this.debounceTimer);

        if (query.length < 2) {
            this.hideDropdown();
            return;
        }

        this.debounceTimer = setTimeout(() => {
            this.fetchSuggestions(query);
        }, 200);
    }

    async fetchSuggestions(query) {
        try {
            const response = await fetch(`/api/autocomplete?q=${encodeURIComponent(query)}`);
            const suggestions = await response.json();
            this.suggestions = suggestions;
            this.displaySuggestions(suggestions);
        } catch (error) {
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
            item.className = 'yt-autocomplete-item';
            item.textContent = suggestion;
            item.style.cssText = `
                padding: 8px 16px;
                cursor: pointer;
                color: #f1f1f1;
                font-size: 14px;
                display: flex;
                align-items: center;
                gap: 12px;
            `;

            item.addEventListener('click', () => {
                this.selectSuggestion(suggestion);
            });

            item.addEventListener('mouseenter', () => {
                this.highlightItem(index);
            });

            this.dropdown.appendChild(item);
        });

        this.showDropdown();
    }

    handleKeydown(e) {
        if (!this.dropdown || this.dropdown.style.display === 'none') return;
        const items = this.dropdown.querySelectorAll('.yt-autocomplete-item');

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, items.length - 1);
                this.highlightItem(this.selectedIndex);
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                if (this.selectedIndex === -1) this.clearHighlight();
                else this.highlightItem(this.selectedIndex);
                break;
            case 'Enter':
                if (this.selectedIndex >= 0) {
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
        if (query.length >= 2 && this.suggestions.length > 0) this.showDropdown();
    }

    highlightItem(index) {
        const items = this.dropdown.querySelectorAll('.yt-autocomplete-item');
        items.forEach((item, i) => {
            item.style.background = i === index ? '#444' : 'transparent';
        });
    }

    clearHighlight() {
        const items = this.dropdown.querySelectorAll('.yt-autocomplete-item');
        items.forEach(item => item.style.background = 'transparent');
    }

    selectSuggestion(suggestion) {
        this.input.value = suggestion;
        this.hideDropdown();
        this.form.submit();
    }

    showDropdown() { this.dropdown.style.display = 'block'; }
    hideDropdown() { this.dropdown.style.display = 'none'; this.selectedIndex = -1; }
}

document.addEventListener('DOMContentLoaded', () => {
    // Standard YouTube inputs
    const inputs = document.querySelectorAll('.yt-search-input, .yt-hero-search-input');
    inputs.forEach(input => {
        const form = input.closest('form');
        if (form) new SearchAutocomplete(input, form);
    });
});
