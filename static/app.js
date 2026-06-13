/**
 * FlashSearch — Frontend Logic
 * Debounced search, mode toggle, pagination, result rendering.
 */
(function () {
    "use strict";

    // ── DOM Elements ──
    const searchInput = document.getElementById("searchInput");
    const modeToggle = document.getElementById("modeToggle");
    const btnAnd = document.getElementById("btnAnd");
    const btnOr = document.getElementById("btnOr");
    const resultsList = document.getElementById("resultsList");
    const resultsMeta = document.getElementById("resultsMeta");
    const metaCount = document.getElementById("metaCount");
    const metaLatency = document.getElementById("metaLatency");
    const metaCached = document.getElementById("metaCached");
    const metaTokens = document.getElementById("metaTokens");
    const loading = document.getElementById("loading");
    const emptyState = document.getElementById("emptyState");
    const searchHint = document.getElementById("searchHint");
    const pagination = document.getElementById("pagination");
    const btnPrev = document.getElementById("btnPrev");
    const btnNext = document.getElementById("btnNext");
    const pageInfo = document.getElementById("pageInfo");
    const statDocs = document.getElementById("statDocs");
    const statTokens = document.getElementById("statTokens");

    // ── State ──
    let currentMode = "AND";
    let currentOffset = 0;
    const LIMIT = 20;
    let debounceTimer = null;
    let currentQuery = "";

    // ── Init: Fetch Stats ──
    async function fetchStats() {
        try {
            const res = await fetch("/api/stats");
            const data = await res.json();
            statDocs.textContent = data.total_documents.toLocaleString() + " docs";
            statTokens.textContent = data.total_tokens.toLocaleString() + " tokens";
        } catch (e) {
            console.error("Failed to fetch stats:", e);
        }
    }
    fetchStats();

    // ── Search ──
    async function performSearch(query, offset = 0) {
        if (query.length < 2) {
            clearResults();
            searchHint.style.display = "block";
            return;
        }

        searchHint.style.display = "none";
        loading.style.display = "flex";
        emptyState.style.display = "none";
        resultsMeta.style.display = "none";
        resultsList.innerHTML = "";
        pagination.style.display = "none";

        const endpoint = currentMode === "AND" ? "/api/search" : "/api/search/or";

        try {
            const res = await fetch(endpoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query, limit: LIMIT, offset }),
            });
            const data = await res.json();
            loading.style.display = "none";
            renderResults(data, query);
        } catch (err) {
            loading.style.display = "none";
            console.error("Search failed:", err);
        }
    }

    // ── Render ──
    function renderResults(data, query) {
        if (!data.results || data.results.length === 0) {
            emptyState.style.display = "block";
            resultsMeta.style.display = "none";
            pagination.style.display = "none";
            return;
        }

        // Meta bar
        resultsMeta.style.display = "flex";
        metaCount.textContent = data.total_matches + " result" + (data.total_matches !== 1 ? "s" : "");
        metaLatency.textContent = data.latency_ms + "ms";
        metaCached.style.display = data.cached ? "inline" : "none";
        metaTokens.textContent = data.tokens ? "tokens: " + data.tokens.join(", ") : "";

        // Result cards
        resultsList.innerHTML = "";
        data.results.forEach(function (r, i) {
            var card = document.createElement("div");
            card.className = "result-card";
            card.style.animationDelay = (i * 0.04) + "s";

            var rank = currentOffset + i + 1;
            var preview = highlightTerms(r.preview, data.tokens || []);

            card.innerHTML =
                '<div class="result-rank">#' + rank + "</div>" +
                '<div class="result-title">' + escapeHtml(r.title) + "</div>" +
                '<div class="result-preview">' + preview + "</div>" +
                '<div class="result-footer">' +
                '<span class="result-score">score: ' + r.score + "</span>" +
                '<span class="result-docid">doc #' + r.doc_id + "</span>" +
                "</div>";

            resultsList.appendChild(card);
        });

        // Pagination
        var totalPages = Math.ceil(data.total_matches / LIMIT);
        var currentPage = Math.floor(currentOffset / LIMIT) + 1;

        if (totalPages > 1) {
            pagination.style.display = "flex";
            pageInfo.textContent = "Page " + currentPage + " of " + totalPages;
            btnPrev.disabled = currentPage <= 1;
            btnNext.disabled = currentPage >= totalPages;
        } else {
            pagination.style.display = "none";
        }
    }

    function clearResults() {
        resultsList.innerHTML = "";
        resultsMeta.style.display = "none";
        emptyState.style.display = "none";
        pagination.style.display = "none";
        loading.style.display = "none";
    }

    // ── Highlight matching tokens in preview text ──
    function highlightTerms(text, tokens) {
        if (!tokens || tokens.length === 0) return escapeHtml(text);
        var escaped = escapeHtml(text);
        tokens.forEach(function (token) {
            var regex = new RegExp("(" + escapeRegex(token) + ")", "gi");
            escaped = escaped.replace(regex, "<mark>$1</mark>");
        });
        return escaped;
    }

    function escapeHtml(str) {
        var div = document.createElement("div");
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }

    function escapeRegex(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    }

    // ── Event Listeners ──

    // Debounced search input
    searchInput.addEventListener("input", function () {
        var query = searchInput.value.trim();
        currentQuery = query;
        currentOffset = 0;

        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(function () {
            performSearch(query, 0);
        }, 300);
    });

    // Enter key
    searchInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            clearTimeout(debounceTimer);
            currentOffset = 0;
            performSearch(searchInput.value.trim(), 0);
        }
    });

    // Mode toggle
    modeToggle.addEventListener("click", function (e) {
        if (!e.target.classList.contains("mode-btn")) return;
        var mode = e.target.dataset.mode;
        if (mode === currentMode) return;

        currentMode = mode;
        btnAnd.classList.toggle("active", mode === "AND");
        btnOr.classList.toggle("active", mode === "OR");
        currentOffset = 0;

        if (currentQuery.length >= 2) {
            performSearch(currentQuery, 0);
        }
    });

    // Pagination
    btnPrev.addEventListener("click", function () {
        if (currentOffset >= LIMIT) {
            currentOffset -= LIMIT;
            performSearch(currentQuery, currentOffset);
        }
    });

    btnNext.addEventListener("click", function () {
        currentOffset += LIMIT;
        performSearch(currentQuery, currentOffset);
    });
})();
