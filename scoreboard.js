(() => {
    const NAME_KEY = 'vanilla-player-name';

    function clamp(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }

    function normalizeDifficulty(raw) {
        const diff = String(raw || '').trim().toLowerCase();
        if (diff === 'easy' || diff === 'medium' || diff === 'hard') return diff;
        return 'all';
    }

    function titleCase(text) {
        const t = String(text || '').trim();
        if (!t) return '';
        return t.charAt(0).toUpperCase() + t.slice(1);
    }

    function escapeHtml(text) {
        return String(text || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function bestKey(gameId, difficulty) {
        return `vanilla-${String(gameId)}-${String(difficulty)}-best`;
    }

    function migrateLocalStorageKey(targetKey, aliases) {
        try {
            const existing = localStorage.getItem(targetKey);
            if (existing !== null && existing !== undefined) return;
            for (const alias of aliases || []) {
                const value = localStorage.getItem(alias);
                if (value === null || value === undefined) continue;
                localStorage.setItem(targetKey, value);
                localStorage.removeItem(alias);
                return;
            }
        } catch (err) {
            // ignore storage failures (private mode)
        }
    }

    function getSavedName() {
        try {
            return (localStorage.getItem(NAME_KEY) || '').trim();
        } catch (err) {
            return '';
        }
    }

    function setSavedName(name) {
        try {
            localStorage.setItem(NAME_KEY, String(name || '').trim());
        } catch (err) {
            // ignore
        }
    }

    class Scoreboard {
        constructor(options) {
            const mount = options.mount;
            if (!mount) throw new Error('Scoreboard mount is required');

            this.gameId = String(options.gameId || '').trim();
            if (!this.gameId) throw new Error('gameId is required');

            this.difficulty = normalizeDifficulty(options.difficulty);
            this.bestKey = String(options.bestKey || bestKey(this.gameId, this.difficulty));
            this.bestAliases = Array.isArray(options.bestKeyAliases) ? options.bestKeyAliases : [];
            this.bestLabel = String(options.bestLabel || 'Personal best');
            this.scoreLabel = String(options.scoreLabel || 'Score');

            this.formatScore = typeof options.formatScore === 'function' ? options.formatScore : (value) => String(value ?? '—');
            this.getSubmitScore = typeof options.getSubmitScore === 'function' ? options.getSubmitScore : () => this._bestValue;
            this.canSubmitScore =
                typeof options.canSubmitScore === 'function'
                    ? options.canSubmitScore
                    : (value) => Number.isFinite(Number(value)) && Number(value) > 0;

            this._bestValue = null;
            this._rawEntries = [];
            this._filter = normalizeDifficulty(options.defaultFilter || this.difficulty);

            migrateLocalStorageKey(this.bestKey, this.bestAliases);

            this.root = mount;
            this.root.innerHTML = `
                <div class="vanilla-scoreboard">
                    <div class="vs-head">
                        <div class="vs-eyebrow">Scores</div>
                        <div class="vs-title-row">
                            <div class="vs-title-col">
                                <h2 class="vs-title">Leaderboard</h2>
                                <div class="vs-subtitle">${escapeHtml(this.scoreLabel)}</div>
                            </div>
                            <div class="vs-best">
                                <div class="vs-best-label">${escapeHtml(this.bestLabel)}</div>
                                <div class="vs-best-value" data-best>—</div>
                            </div>
                        </div>
                        <div class="vs-filters" data-filters>
                            ${this._renderFilterButton('all', 'All')}
                            ${this._renderFilterButton('easy', 'Easy')}
                            ${this._renderFilterButton('medium', 'Medium')}
                            ${this._renderFilterButton('hard', 'Hard')}
                        </div>
                    </div>
                    <div class="vs-list" data-list></div>
                    <div class="vs-submit">
                        <input class="vs-name-input" data-name maxlength="18" placeholder="Name for leaderboard" autocomplete="nickname" />
                        <button class="vs-submit-btn" data-submit type="button">Submit best</button>
                    </div>
                    <div class="vs-note" data-note>Submitting saves your personal best to the global leaderboard.</div>
                </div>
            `;

            this.bestEl = this.root.querySelector('[data-best]');
            this.listEl = this.root.querySelector('[data-list]');
            this.noteEl = this.root.querySelector('[data-note]');
            this.nameEl = this.root.querySelector('[data-name]');
            this.submitBtn = this.root.querySelector('[data-submit]');
            this.filtersEl = this.root.querySelector('[data-filters]');

            const savedName = getSavedName();
            if (this.nameEl && savedName) this.nameEl.value = savedName.slice(0, 18);

            if (this.filtersEl) {
                this.filtersEl.addEventListener('click', (event) => {
                    const button = event.target && event.target.closest ? event.target.closest('[data-filter]') : null;
                    if (!button) return;
                    const next = normalizeDifficulty(button.getAttribute('data-filter'));
                    this.setFilter(next);
                });
            }

            if (this.submitBtn) {
                this.submitBtn.addEventListener('click', () => this.submitBest());
            }

            if (this.nameEl) {
                this.nameEl.addEventListener('input', () => {
                    const name = (this.nameEl.value || '').trim();
                    if (name) setSavedName(name.slice(0, 18));
                });
            }

            this._loadBestFromStorage();
            this._updateSubmitState();
            this.loadLeaderboard();
        }

        _renderFilterButton(value, label) {
            const active = normalizeDifficulty(value) === this._filter ? ' active' : '';
            return `<button class="vs-filter${active}" type="button" data-filter="${escapeHtml(value)}">${escapeHtml(label)}</button>`;
        }

        _rerenderFilters() {
            if (!this.filtersEl) return;
            this.filtersEl.innerHTML = `
                ${this._renderFilterButton('all', 'All')}
                ${this._renderFilterButton('easy', 'Easy')}
                ${this._renderFilterButton('medium', 'Medium')}
                ${this._renderFilterButton('hard', 'Hard')}
            `;
        }

        _loadBestFromStorage() {
            try {
                const raw = localStorage.getItem(this.bestKey);
                if (raw === null || raw === undefined || raw === '') {
                    this.setBest(null);
                    return;
                }
                const num = Number(raw);
                if (!Number.isFinite(num)) {
                    this.setBest(null);
                    return;
                }
                this.setBest(num);
            } catch (err) {
                this.setBest(null);
            }
        }

        setFilter(filter) {
            const next = normalizeDifficulty(filter);
            if (this._filter === next) return;
            this._filter = next;
            this._rerenderFilters();
            this._renderLeaderboard();
        }

        setBest(value) {
            if (value === null || value === undefined || value === '') {
                this._bestValue = null;
                if (this.bestEl) this.bestEl.textContent = '—';
                this._updateSubmitState();
                return;
            }
            const num = Number(value);
            this._bestValue = Number.isFinite(num) ? num : null;
            if (this.bestEl) this.bestEl.textContent = this._bestValue === null ? '—' : this.formatScore(this._bestValue);
            this._updateSubmitState();
        }

        setNote(text) {
            if (!this.noteEl) return;
            this.noteEl.textContent = String(text || '');
        }

        _updateSubmitState() {
            if (!this.submitBtn) return;
            const score = this.getSubmitScore();
            const canSubmit = this.canSubmitScore(score);
            this.submitBtn.disabled = !canSubmit;
        }

        _renderLeaderboard() {
            if (!this.listEl) return;

            const entries = Array.isArray(this._rawEntries) ? this._rawEntries : [];
            const filtered =
                this._filter === 'all'
                    ? entries
                    : entries.filter((entry) => normalizeDifficulty(entry.difficulty) === this._filter);

            const items = filtered.slice(0, 8);
            this.listEl.innerHTML = '';

            if (!items.length) {
                const row = document.createElement('div');
                row.className = 'vs-row vs-row-empty';
                row.innerHTML = `
                    <div class="vs-rank">—</div>
                    <div class="vs-main">
                        <div class="vs-entry-name">No scores yet</div>
                        <div class="vs-meta">Be the first to submit a run.</div>
                    </div>
                    <div class="vs-score">—</div>
                `;
                this.listEl.appendChild(row);
                return;
            }

            items.forEach((entry, idx) => {
                const row = document.createElement('div');
                row.className = 'vs-row';

                const name = escapeHtml(String(entry.player || 'Player'));
                const score = Number(entry.score || 0);
                const diff = normalizeDifficulty(entry.difficulty);
                const meta = diff === 'all' ? '—' : titleCase(diff);

                row.innerHTML = `
                    <div class="vs-rank">${idx + 1}</div>
                    <div class="vs-main">
                        <div class="vs-entry-name">${name}</div>
                        <div class="vs-meta">${escapeHtml(meta)}</div>
                    </div>
                    <div class="vs-score">${escapeHtml(this.formatScore(score))}</div>
                `;

                this.listEl.appendChild(row);
            });
        }

        async loadLeaderboard() {
            this.setNote('Loading leaderboard…');
            try {
                const resp = await fetch(`/api/leaderboard/${encodeURIComponent(this.gameId)}`);
                if (!resp.ok) throw new Error('leaderboard fetch failed');
                const data = await resp.json();
                const scores = Array.isArray(data.scores) ? data.scores : [];
                this._rawEntries = scores;
                this.setNote('Submitting saves your personal best to the global leaderboard.');
                this._renderLeaderboard();
            } catch (err) {
                this._rawEntries = [];
                this.setNote('Leaderboard unavailable (server offline?).');
                this._renderLeaderboard();
            }
        }

        async submitBest() {
            const score = this.getSubmitScore();
            if (!this.canSubmitScore(score)) {
                this.setNote('Play a run to set a personal best first.');
                return;
            }
            const name = (this.nameEl ? this.nameEl.value : '').trim();
            if (!name) {
                this.setNote('Add a name to submit your score.');
                return;
            }

            const payload = {
                game: this.gameId,
                player: name.slice(0, 18),
                score: clamp(Number(score), -1_000_000_000, 1_000_000_000),
                difficulty: this.difficulty === 'all' ? 'unknown' : this.difficulty,
            };

            if (this.submitBtn) this.submitBtn.disabled = true;
            this.setNote('Submitting…');
            try {
                const resp = await fetch('/api/score', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });
                const data = await resp.json().catch(() => ({}));
                if (!resp.ok) throw new Error(data.error || 'Submit failed');
                setSavedName(payload.player);
                this.setNote('Submitted! Refreshing leaderboard…');
                await this.loadLeaderboard();
                this.setNote('Submitted! Your score is on the board.');
            } catch (err) {
                this.setNote('Could not submit (server offline?).');
            } finally {
                if (this.submitBtn) this.submitBtn.disabled = false;
                this._updateSubmitState();
            }
        }
    }

    window.VanillaScoreboard = {
        bestKey,
        migrateLocalStorageKey,
        mount: (options) => new Scoreboard(options),
    };
})();
