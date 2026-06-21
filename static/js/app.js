/**
 * GastroAI — Frontend Application Logic
 * Handles mode switching, filter controls, API calls, and result rendering.
 */

(function () {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════════
    // State
    // ═══════════════════════════════════════════════════════════════════════════
    const state = {
        mode: 'ai', // 'ai' or 'filter'
        locations: [],
        cuisines: [],
        restaurantTypes: [],
        selectedRating: 0,
        maxBudget: 3000,
        numPeople: 2,
        cuisinesExpanded: false,
        CUISINES_COLLAPSED_COUNT: 5,
    };

    // ═══════════════════════════════════════════════════════════════════════════
    // DOM References
    // ═══════════════════════════════════════════════════════════════════════════
    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    const dom = {
        // Mode toggle
        btnModeAI: $('#btnModeAI'),
        btnModeFilter: $('#btnModeFilter'),

        // Sidebar modes
        sidebarNavMode: $('#sidebarNavMode'),
        sidebarFilterMode: $('#sidebarFilterMode'),

        // Views
        aiAssistantView: $('#aiAssistantView'),
        aiResultsView: $('#aiResultsView'),
        aiResultsContent: $('#aiResultsContent'),
        filterSearchView: $('#filterSearchView'),
        filterInitialState: $('#filterInitialState'),
        filterResultsContent: $('#filterResultsContent'),

        // AI inputs
        aiQueryInput: $('#aiQueryInput'),
        aiSearchBtn: $('#aiSearchBtn'),

        // Filter controls
        sidebarLocationSelect: $('#sidebarLocationSelect'),
        filterLocationSelect: $('#filterLocationSelect'),
        cuisineCheckboxes: $('#cuisineCheckboxes'),
        showMoreCuisinesBtn: $('#showMoreCuisinesBtn'),
        ratingChips: $('#ratingChips'),
        budgetSlider: $('#budgetSlider'),
        budgetDisplay: $('#budgetDisplay'),
        diningStyleCheckboxes: $('#diningStyleCheckboxes'),
        sidebarDiningChips: $('#sidebarDiningChips'),
        filterOnlineOrder: $('#filterOnlineOrder'),
        filterBookTable: $('#filterBookTable'),
        filterSearchBtn: $('#filterSearchBtn'),
        clearFiltersBtn: $('#clearFiltersBtn'),
        peopleValue: $('#peopleValue'),
        peopleDecBtn: $('#peopleDecBtn'),
        peopleIncBtn: $('#peopleIncBtn'),

        // Performance
        perfIntentParse: $('#perfIntentParse'),
        perfDbQuery: $('#perfDbQuery'),
        perfTotal: $('#perfTotal'),

        // Loading
        loadingOverlay: $('#loadingOverlay'),
    };

    // ═══════════════════════════════════════════════════════════════════════════
    // Initialization
    // ═══════════════════════════════════════════════════════════════════════════
    async function init() {
        bindEvents();
        await Promise.all([
            loadLocations(),
            loadCuisines(),
            loadRestaurantTypes(),
        ]);
        renderCuisineCheckboxes();
        renderDiningStyleCheckboxes();
        renderSidebarDiningChips();
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Data Loading
    // ═══════════════════════════════════════════════════════════════════════════
    async function loadLocations() {
        try {
            const res = await fetch('/api/locations');
            const data = await res.json();
            state.locations = data.locations || [];
            populateLocationDropdowns();
        } catch (e) {
            console.error('Failed to load locations:', e);
        }
    }

    async function loadCuisines() {
        try {
            const res = await fetch('/api/cuisines');
            const data = await res.json();
            state.cuisines = data.cuisines || [];
        } catch (e) {
            console.error('Failed to load cuisines:', e);
        }
    }

    async function loadRestaurantTypes() {
        try {
            const res = await fetch('/api/restaurant-types');
            const data = await res.json();
            state.restaurantTypes = data.types || [];
        } catch (e) {
            console.error('Failed to load restaurant types:', e);
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Populate Controls
    // ═══════════════════════════════════════════════════════════════════════════
    function populateLocationDropdowns() {
        [dom.sidebarLocationSelect, dom.filterLocationSelect].forEach((sel) => {
            sel.innerHTML = '';
            state.locations.forEach((loc, idx) => {
                const opt = document.createElement('option');
                opt.value = loc;
                opt.textContent = loc;
                // Default select first
                if (idx === 0) opt.selected = true;
                sel.appendChild(opt);
            });
        });
    }

    function renderCuisineCheckboxes() {
        const container = dom.cuisineCheckboxes;
        container.innerHTML = '';

        const limit = state.cuisinesExpanded
            ? state.cuisines.length
            : state.CUISINES_COLLAPSED_COUNT;

        const visible = state.cuisines.slice(0, limit);
        visible.forEach((cuisine) => {
            const label = document.createElement('label');
            label.className = 'gastro-checkbox';
            label.innerHTML = `
                <input type="checkbox" value="${escapeHtml(cuisine)}" class="cuisine-cb" />
                <span class="gastro-checkbox__label">${escapeHtml(titleCase(cuisine))}</span>
            `;
            container.appendChild(label);
        });

        const remaining = state.cuisines.length - state.CUISINES_COLLAPSED_COUNT;
        if (remaining > 0) {
            dom.showMoreCuisinesBtn.textContent = state.cuisinesExpanded
                ? '- Show less'
                : `+ View ${remaining} more`;
            dom.showMoreCuisinesBtn.style.display = 'block';
        } else {
            dom.showMoreCuisinesBtn.style.display = 'none';
        }
    }

    function renderDiningStyleCheckboxes() {
        const container = dom.diningStyleCheckboxes;
        container.innerHTML = '';

        const styles = ['Fine Dining', 'Casual Dining', 'Cafe', 'Pub', 'Bar', 'Lounge', 'Quick Bites'];
        styles.forEach((style) => {
            const label = document.createElement('label');
            label.className = 'gastro-checkbox';
            label.innerHTML = `
                <input type="checkbox" value="${escapeHtml(style)}" class="dining-style-cb" />
                <span class="gastro-checkbox__label">${escapeHtml(style)}</span>
            `;
            container.appendChild(label);
        });
    }

    function renderSidebarDiningChips() {
        const container = dom.sidebarDiningChips;
        container.innerHTML = '';

        const styles = ['Fine Dining', 'Casual', 'Romantic'];
        styles.forEach((style) => {
            const btn = document.createElement('button');
            btn.className = 'chip';
            btn.textContent = style;
            btn.dataset.diningStyle = style;
            btn.addEventListener('click', () => {
                btn.classList.toggle('chip--active');
            });
            container.appendChild(btn);
        });
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Event Binding
    // ═══════════════════════════════════════════════════════════════════════════
    function bindEvents() {
        // Mode toggle
        dom.btnModeAI.addEventListener('click', () => switchMode('ai'));
        dom.btnModeFilter.addEventListener('click', () => switchMode('filter'));

        // AI Search
        dom.aiSearchBtn.addEventListener('click', handleAISearch);
        dom.aiQueryInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleAISearch();
            }
        });

        // Suggestion chips
        $$('.suggestion-chip').forEach((chip) => {
            chip.addEventListener('click', () => {
                dom.aiQueryInput.value = chip.dataset.query;
                handleAISearch();
            });
        });

        // Filter controls
        dom.budgetSlider.addEventListener('input', () => {
            state.maxBudget = parseInt(dom.budgetSlider.value);
            updateBudgetLabel();
        });

        // People stepper
        dom.peopleDecBtn.addEventListener('click', () => {
            if (state.numPeople > 1) {
                state.numPeople--;
                dom.peopleValue.textContent = state.numPeople;
                updateBudgetLabel();
            }
        });
        dom.peopleIncBtn.addEventListener('click', () => {
            if (state.numPeople < 20) {
                state.numPeople++;
                dom.peopleValue.textContent = state.numPeople;
                updateBudgetLabel();
            }
        });

        // Rating chips
        dom.ratingChips.addEventListener('click', (e) => {
            const chip = e.target.closest('.chip');
            if (!chip) return;
            $$('#ratingChips .chip').forEach((c) => c.classList.remove('chip--active'));
            chip.classList.add('chip--active');
            state.selectedRating = parseFloat(chip.dataset.rating) || 0;
        });

        // Show more cuisines
        dom.showMoreCuisinesBtn.addEventListener('click', () => {
            state.cuisinesExpanded = !state.cuisinesExpanded;
            renderCuisineCheckboxes();
        });

        // Filter search
        dom.filterSearchBtn.addEventListener('click', handleFilterSearch);

        // Clear filters
        dom.clearFiltersBtn.addEventListener('click', clearFilters);

        // Mobile bottom nav
        $$('.bottom-nav__link').forEach((link) => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const nav = link.dataset.mobileNav;
                $$('.bottom-nav__link').forEach((l) => l.classList.remove('bottom-nav__link--active'));
                link.classList.add('bottom-nav__link--active');
                if (nav === 'ai') switchMode('ai');
                else if (nav === 'filter') switchMode('filter');
            });
        });

        // Sync location dropdowns
        dom.sidebarLocationSelect.addEventListener('change', () => {
            dom.filterLocationSelect.value = dom.sidebarLocationSelect.value;
        });
        dom.filterLocationSelect.addEventListener('change', () => {
            dom.sidebarLocationSelect.value = dom.filterLocationSelect.value;
        });
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Mode Switching
    // ═══════════════════════════════════════════════════════════════════════════
    function switchMode(mode) {
        state.mode = mode;

        if (mode === 'ai') {
            dom.btnModeAI.className = 'mode-toggle-btn mode-toggle-btn--active';
            dom.btnModeFilter.className = 'mode-toggle-btn mode-toggle-btn--inactive';
            dom.sidebarNavMode.classList.remove('hidden');
            dom.sidebarFilterMode.classList.add('hidden');
            dom.aiAssistantView.classList.remove('hidden');
            dom.aiResultsView.classList.add('hidden');
            dom.filterSearchView.classList.add('hidden');
        } else {
            dom.btnModeAI.className = 'mode-toggle-btn mode-toggle-btn--inactive';
            dom.btnModeFilter.className = 'mode-toggle-btn mode-toggle-btn--active';
            dom.sidebarNavMode.classList.add('hidden');
            dom.sidebarFilterMode.classList.remove('hidden');
            dom.aiAssistantView.classList.add('hidden');
            dom.aiResultsView.classList.add('hidden');
            dom.filterSearchView.classList.remove('hidden');
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // AI Assistant Search
    // ═══════════════════════════════════════════════════════════════════════════
    async function handleAISearch() {
        const query = dom.aiQueryInput.value.trim();
        if (!query) return;

        showLoading();
        dom.aiSearchBtn.disabled = true;

        try {
            const res = await fetch('/api/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, limit: 6 }),
            });
            const data = await res.json();

            if (data.error) {
                hideLoading();
                dom.aiSearchBtn.disabled = false;
                alert('Error: ' + data.error);
                return;
            }

            renderAIResults(data);
            updatePerfMetrics(data.timings);

            // Switch to results view
            dom.aiAssistantView.classList.add('hidden');
            dom.aiResultsView.classList.remove('hidden');
        } catch (e) {
            console.error('AI search failed:', e);
            alert('Failed to fetch recommendations. Please try again.');
        } finally {
            hideLoading();
            dom.aiSearchBtn.disabled = false;
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Filter Search
    // ═══════════════════════════════════════════════════════════════════════════
    async function handleFilterSearch() {
        const location = dom.filterLocationSelect.value;
        const cuisines = Array.from($$('.cuisine-cb:checked')).map((cb) => cb.value);
        const minRating = state.selectedRating;
        const maxBudget = state.maxBudget;
        const numPeople = state.numPeople;
        const diningStyles = Array.from($$('.dining-style-cb:checked')).map((cb) => cb.value);
        const onlineOrder = dom.filterOnlineOrder.checked || null;
        const bookTable = dom.filterBookTable.checked || null;

        showLoading();
        dom.filterSearchBtn.disabled = true;

        try {
            const res = await fetch('/api/filter', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    location,
                    cuisines,
                    min_rating: minRating,
                    max_budget: maxBudget,
                    online_order: onlineOrder,
                    book_table: bookTable,
                    restaurant_type: diningStyles,
                    num_people: numPeople,
                    limit: 9,
                }),
            });
            const data = await res.json();

            if (data.error) {
                hideLoading();
                dom.filterSearchBtn.disabled = false;
                alert('Error: ' + data.error);
                return;
            }

            renderFilterResults(data);
            updatePerfMetrics(data.timings);

            dom.filterInitialState.classList.add('hidden');
            dom.filterResultsContent.classList.remove('hidden');
        } catch (e) {
            console.error('Filter search failed:', e);
            alert('Failed to search. Please try again.');
        } finally {
            hideLoading();
            dom.filterSearchBtn.disabled = false;
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Rendering Results
    // ═══════════════════════════════════════════════════════════════════════════
    function renderAIResults(data) {
        const container = dom.aiResultsContent;
        container.innerHTML = '';

        // Back button
        const backBtn = document.createElement('button');
        backBtn.className = 'chip';
        backBtn.style.marginBottom = '24px';
        backBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size:16px">arrow_back</span> New Search';
        backBtn.addEventListener('click', () => {
            dom.aiResultsView.classList.add('hidden');
            dom.aiAssistantView.classList.remove('hidden');
        });
        container.appendChild(backBtn);

        // Parsed Intent Tags
        if (data.parsed_filters && Object.keys(data.parsed_filters).length > 0) {
            const intentDiv = document.createElement('div');
            intentDiv.className = 'parsed-intent';
            let html = '<span class="parsed-intent__label">Parsed Intent:</span>';
            for (const [key, val] of Object.entries(data.parsed_filters)) {
                const display = Array.isArray(val) ? val.join(', ') : String(val);
                html += `<span class="parsed-intent__tag">${escapeHtml(display)}</span>`;
            }
            intentDiv.innerHTML = html;
            container.appendChild(intentDiv);
        }

        // Alerts
        renderAlerts(container, data);

        // Summary
        if (data.summary) {
            const sumDiv = document.createElement('div');
            sumDiv.className = 'summary-box';
            sumDiv.innerHTML = `
                <span class="material-symbols-outlined">auto_awesome</span>
                <span>${escapeHtml(data.summary)}</span>
            `;
            container.appendChild(sumDiv);
        }

        // Results header
        const recs = data.recommendations || [];
        const headerDiv = document.createElement('div');
        headerDiv.className = 'results-header';
        headerDiv.innerHTML = `
            <div>
                <h2 class="text-headline-md results-header__title">AI Recommendations</h2>
                <p class="results-header__subtitle">
                    <span class="material-symbols-outlined">auto_awesome</span>
                    ${recs.length} match${recs.length !== 1 ? 'es' : ''} found.
                </p>
            </div>
        `;
        container.appendChild(headerDiv);

        // Cards
        if (recs.length === 0) {
            container.appendChild(createEmptyState('search_off', 'No matches found', 'Try broadening your search criteria.'));
        } else {
            const grid = document.createElement('div');
            grid.className = 'results-grid';
            recs.forEach((rec, idx) => grid.appendChild(createCard(rec, idx)));
            container.appendChild(grid);
        }
    }

    function renderFilterResults(data) {
        const container = dom.filterResultsContent;
        container.innerHTML = '';

        // Alerts
        renderAlerts(container, data);

        // Summary
        if (data.summary) {
            const sumDiv = document.createElement('div');
            sumDiv.className = 'summary-box';
            sumDiv.innerHTML = `
                <span class="material-symbols-outlined">auto_awesome</span>
                <span>${escapeHtml(data.summary)}</span>
            `;
            container.appendChild(sumDiv);
        }

        // Header with sort
        const recs = data.recommendations || [];
        const headerDiv = document.createElement('div');
        headerDiv.className = 'results-header';
        headerDiv.innerHTML = `
            <div>
                <h2 class="text-headline-md results-header__title">Search results for your criteria</h2>
                <p class="results-header__subtitle">
                    <span class="material-symbols-outlined">auto_awesome</span>
                    AI analyzed ${data.candidate_count || 0} candidates. Top ${recs.length} matches found.
                </p>
            </div>
            <div class="sort-control">
                <span class="sort-control__label">Sort by:</span>
                <div class="sort-select-wrapper">
                    <select class="sort-select" id="sortSelect">
                        <option value="match_score">AI Match Score (High to Low)</option>
                        <option value="rating">Rating</option>
                        <option value="cost_asc">Cost: Low to High</option>
                    </select>
                    <span class="material-symbols-outlined icon-right">expand_more</span>
                </div>
            </div>
        `;
        container.appendChild(headerDiv);

        // Sort handler
        const sortSelect = headerDiv.querySelector('#sortSelect');
        sortSelect.addEventListener('change', () => {
            sortAndRerender(recs, sortSelect.value, container, headerDiv);
        });

        // Cards
        if (recs.length === 0) {
            container.appendChild(createEmptyState('search_off', 'No restaurants found', 'Try adjusting your filters for broader results.'));
        } else {
            const grid = document.createElement('div');
            grid.className = 'results-grid';
            grid.id = 'filterResultsGrid';
            recs.forEach((rec, idx) => grid.appendChild(createCard(rec, idx)));
            container.appendChild(grid);
        }
    }

    function sortAndRerender(recs, sortKey, container, headerDiv) {
        const sorted = [...recs];
        if (sortKey === 'rating') {
            sorted.sort((a, b) => (b.rating || 0) - (a.rating || 0));
        } else if (sortKey === 'cost_asc') {
            sorted.sort((a, b) => (a.cost || 0) - (b.cost || 0));
        } else {
            sorted.sort((a, b) => (b.match_score || 0) - (a.match_score || 0));
        }

        const oldGrid = container.querySelector('.results-grid');
        if (oldGrid) oldGrid.remove();

        const grid = document.createElement('div');
        grid.className = 'results-grid';
        sorted.forEach((rec, idx) => grid.appendChild(createCard(rec, idx)));
        container.appendChild(grid);
    }

    function renderAlerts(container, data) {
        // Location relaxation alert
        if (data.location_relaxed) {
            const searched = data.searched_locations || [];
            const nearby = searched.slice(1); // first is the original location
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert--info';
            alertDiv.innerHTML = `
                <span class="material-symbols-outlined">near_me</span>
                <span><strong>Location Expanded!</strong>
                Not enough results in <strong>${escapeHtml(searched[0] || '')}</strong>.
                Also searched nearby areas: ${nearby.slice(0, 5).map(l => '<strong>' + escapeHtml(l) + '</strong>').join(', ')}${nearby.length > 5 ? ' and ' + (nearby.length - 5) + ' more' : ''}.</span>
            `;
            container.appendChild(alertDiv);
        }

        if (data.relaxation_applied) {
            const orig = data.original_constraints || {};
            const final = data.final_constraints || {};
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert--warning';
            alertDiv.innerHTML = `
                <span class="material-symbols-outlined">warning</span>
                <span><strong>Constraint Relaxation Applied!</strong>
                Rating relaxed from ${orig.min_rating || '—'} to ${final.min_rating || '—'}.
                Budget expanded from ₹${orig.max_budget || '—'} to ₹${Math.round(final.max_budget) || '—'}.</span>
            `;
            container.appendChild(alertDiv);
        }

        if (data.fallback_applied) {
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert--info';
            alertDiv.innerHTML = `
                <span class="material-symbols-outlined">info</span>
                <span><strong>Local Heuristic Scoring Active:</strong> Showing template-ranked recommendations.</span>
            `;
            container.appendChild(alertDiv);
        } else if (data.recommendations && data.recommendations.length > 0) {
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert--success';
            alertDiv.innerHTML = `
                <span class="material-symbols-outlined">auto_awesome</span>
                <span><strong>Live AI Reasoning Active:</strong> Recommendations dynamically generated by AI.</span>
            `;
            container.appendChild(alertDiv);
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Card Component
    // ═══════════════════════════════════════════════════════════════════════════
    function createCard(rec, index) {
        const card = document.createElement('div');
        card.className = 'restaurant-card';

        const rating = rec.rating || 0;
        const matchScore = rec.match_score || 0;
        const cuisines = rec.cuisines || '';
        const cost = rec.cost || 0;
        const reason = rec.reason || '';
        const name = rec.restaurant_name || 'Unknown';
        const restType = rec.restaurant_type || '';

        // Generate cuisine tags
        const cuisineArr = cuisines.split(',').map((c) => titleCase(c.trim())).filter(Boolean).slice(0, 3);
        const typeArr = restType.split(',').map((t) => titleCase(t.trim())).filter(Boolean).slice(0, 1);
        const allTags = [...cuisineArr, ...typeArr];
        if (cost > 0) allTags.push(`₹${cost} for two`);

        const tagsHtml = allTags.map((t) => `<span class="card-tag">${escapeHtml(t)}</span>`).join('');

        const gradientClass = `card-gradient-${(index % 5) + 1}`;

        card.innerHTML = `
            <div class="card-image">
                <div class="card-image__gradient ${gradientClass}">
                    <span class="material-symbols-outlined">restaurant</span>
                </div>
                <div class="card-image__overlay"></div>
                ${rating > 0 ? `
                <div class="card-rating-badge">
                    <span class="card-rating-badge__value">${rating.toFixed(1)}</span>
                    <span class="material-symbols-outlined">star</span>
                </div>
                ` : ''}
            </div>
            <div class="card-body">
                <div class="card-body__header">
                    <h3 class="card-body__name">${escapeHtml(name)}</h3>
                    <div class="match-score-pill">
                        <span class="material-symbols-outlined">target</span>
                        <span class="match-score-pill__value">${matchScore}% Match</span>
                    </div>
                </div>
                <div class="card-tags">
                    ${tagsHtml}
                </div>
                ${reason ? `
                <div class="card-reasoning">
                    <span class="material-symbols-outlined">auto_awesome</span>
                    <p class="card-reasoning__text">${escapeHtml(reason)}</p>
                </div>
                ` : ''}
            </div>
        `;

        return card;
    }

    function createEmptyState(icon, title, subtitle) {
        const div = document.createElement('div');
        div.className = 'empty-state';
        div.innerHTML = `
            <span class="material-symbols-outlined">${icon}</span>
            <h3 class="empty-state__title">${escapeHtml(title)}</h3>
            <p class="empty-state__subtitle">${escapeHtml(subtitle)}</p>
        `;
        return div;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Performance Metrics
    // ═══════════════════════════════════════════════════════════════════════════
    function updatePerfMetrics(timings) {
        if (!timings) return;

        const intentMs = timings.intent_parsing_ms;
        const dbMs = timings.db_query_ms;
        const totalMs = timings.total_ms;

        if (intentMs !== undefined) {
            dom.perfIntentParse.innerHTML = `Intent Parse: <strong>${intentMs.toFixed(0)}ms</strong>`;
        }
        if (dbMs !== undefined) {
            dom.perfDbQuery.innerHTML = `DB Query: <strong>${dbMs.toFixed(0)}ms</strong>`;
        }
        if (totalMs !== undefined) {
            dom.perfTotal.innerHTML = `Total: <strong class="perf-footer__highlight">${totalMs.toFixed(0)}ms</strong>`;
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Filter Controls
    // ═══════════════════════════════════════════════════════════════════════════
    function clearFilters() {
        // Reset location to first
        if (state.locations.length > 0) {
            dom.filterLocationSelect.value = state.locations[0];
            dom.sidebarLocationSelect.value = state.locations[0];
        }

        // Uncheck all cuisines
        $$('.cuisine-cb').forEach((cb) => (cb.checked = false));

        // Reset rating to "Any"
        $$('#ratingChips .chip').forEach((c) => c.classList.remove('chip--active'));
        $$('#ratingChips .chip')[0].classList.add('chip--active');
        state.selectedRating = 0;

        // Reset budget
        dom.budgetSlider.value = 3000;
        state.maxBudget = 3000;

        // Reset people
        state.numPeople = 2;
        dom.peopleValue.textContent = '2';

        updateBudgetLabel();

        // Uncheck dining styles
        $$('.dining-style-cb').forEach((cb) => (cb.checked = false));

        // Uncheck options
        dom.filterOnlineOrder.checked = false;
        dom.filterBookTable.checked = false;

        // Reset view
        dom.filterInitialState.classList.remove('hidden');
        dom.filterResultsContent.classList.add('hidden');
        dom.filterResultsContent.innerHTML = '';
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Loading State
    // ═══════════════════════════════════════════════════════════════════════════
    function showLoading() {
        dom.loadingOverlay.classList.add('loading-overlay--active');
    }
    function hideLoading() {
        dom.loadingOverlay.classList.remove('loading-overlay--active');
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Utilities
    // ═══════════════════════════════════════════════════════════════════════════
    function escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = String(str);
        return div.innerHTML;
    }

    function titleCase(str) {
        if (!str) return '';
        return str.replace(/\b\w/g, (char) => char.toUpperCase());
    }

    function updateBudgetLabel() {
        const n = state.numPeople;
        const b = state.maxBudget;
        dom.budgetDisplay.textContent = `₹0 - ₹${b.toLocaleString('en-IN')}`;
        // Update the section title to reflect number of people
        const budgetTitle = dom.budgetSlider.closest('.filter-section').querySelector('.filter-section__title');
        if (budgetTitle) {
            // Keep the budget-value span
            const span = budgetTitle.querySelector('.budget-value');
            if (span) {
                budgetTitle.childNodes[0].textContent = `Budget (For ${n} ${n === 1 ? 'Person' : 'People'}) `;
                span.textContent = `₹0 - ₹${b.toLocaleString('en-IN')}`;
            }
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // Boot
    // ═══════════════════════════════════════════════════════════════════════════
    document.addEventListener('DOMContentLoaded', init);
})();
