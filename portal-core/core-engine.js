/**
 * BDS Clinical Vault — Canonical Core Engine (v2.2)
 * Shared PortalSidebar, PortalTopBar, Synchronized Focus Timer, Audio Walk & Navigation
 */

(function (window) {
  'use strict';

  const CoreEngine = {
    config: null,
    portalKey: 'vault',
    topics: [],
    currentTopicIndex: -1,
    statusFilter: 'all', // 'all' | 'pending' | 'completed' | 'notes'
    collapsedGroups: {},
    railCollapsed: false,
    focusedRowIndex: -1,

    init(config) {
      this.config = config || {};
      this.portalKey = config.portalKey || 'vault';
      this.topics = config.topics || [];
      this.currentTopicIndex = typeof config.currentTopicIndex === 'number' ? config.currentTopicIndex : -1;

      // Load persisted states
      this.loadCollapsedGroups();
      this.loadRailState();

      // Initialize Core Subsystems
      this.initTheme();
      this.initRouter();
      this.initKeyboard();

      // Render Components if in clinical portal mode
      if (this.portalKey !== 'vault') {
        if (this.currentTopicIndex === -1) {
          document.body.classList.add('is-dashboard');
        } else {
          document.body.classList.remove('is-dashboard');
        }
        this.renderSidebar();
        this.renderTopBar();
        this.updateProgressDisplays();
      }

      // Initialize Timer & Audio
      if (window.BdsTimer) window.BdsTimer.init();
      if (this.initAudio) this.initAudio();
    },

    /* -------------------------------------------------------------
       THEME MANAGEMENT (Dark Obsidian Default)
    ------------------------------------------------------------- */
    initTheme() {
      const savedTheme = localStorage.getItem('bds.theme') || 'dark';
      this.setTheme(savedTheme);
    },

    setTheme(theme) {
      const isLight = theme === 'light';
      if (isLight) {
        document.body.classList.remove('dark');
        document.body.classList.add('light');
        document.documentElement.classList.remove('dark');
        document.documentElement.classList.add('light');
        document.documentElement.setAttribute('data-theme', 'light');
        document.documentElement.style.colorScheme = 'light';
      } else {
        document.body.classList.remove('light');
        document.body.classList.add('dark');
        document.documentElement.classList.remove('light');
        document.documentElement.classList.add('dark');
        document.documentElement.setAttribute('data-theme', 'dark');
        document.documentElement.style.colorScheme = 'dark';
      }

      // Update mobile address bar theme-color
      const metaTheme = document.getElementById('metaThemeColor') || document.querySelector('meta[name="theme-color"]');
      if (metaTheme) {
        metaTheme.setAttribute('content', isLight ? '#f8fafc' : '#090a12');
      }

      // Sync across all ecosystem storage keys
      try {
        localStorage.setItem('bds.theme', isLight ? 'light' : 'dark');
        if (this.portalKey) {
          localStorage.setItem(`bds.${this.portalKey}.theme`, isLight ? 'light' : 'dark');
          localStorage.setItem(`${this.portalKey}_theme`, isLight ? 'light' : 'dark');
        }
      } catch (e) {}

      if (this.config && this.config.onThemeChange) {
        this.config.onThemeChange(isLight ? 'light' : 'dark');
      }
    },

    toggleTheme() {
      const isCurrentlyLight = document.body.classList.contains('light') || 
                               document.documentElement.getAttribute('data-theme') === 'light';
      const next = isCurrentlyLight ? 'dark' : 'light';
      this.setTheme(next);
      this.closeTopbarOverflow();
    },

    /* -------------------------------------------------------------
       STATE PERSISTENCE (Groups & Rail)
    ------------------------------------------------------------- */
    loadCollapsedGroups() {
      try {
        const raw = localStorage.getItem(`bds.${this.portalKey}.collapsedGroups`);
        this.collapsedGroups = raw ? JSON.parse(raw) : {};
      } catch (e) {
        this.collapsedGroups = {};
      }
    },

    saveCollapsedGroups() {
      try {
        localStorage.setItem(`bds.${this.portalKey}.collapsedGroups`, JSON.stringify(this.collapsedGroups));
      } catch (e) {}
    },

    loadRailState() {
      try {
        this.railCollapsed = localStorage.getItem(`bds.${this.portalKey}.railCollapsed`) === 'true';
      } catch (e) {
        this.railCollapsed = false;
      }
    },

    toggleSidebarRail() {
      this.railCollapsed = !this.railCollapsed;
      try {
        localStorage.setItem(`bds.${this.portalKey}.railCollapsed`, String(this.railCollapsed));
      } catch (e) {}
      const sidebar = document.getElementById('sidebar');
      if (sidebar) {
        if (this.railCollapsed) sidebar.classList.add('rail-collapsed');
        else sidebar.classList.remove('rail-collapsed');
      }
    },

    /* -------------------------------------------------------------
       ROUTER & HASH NAVIGATION
    ------------------------------------------------------------- */
    initRouter() {
      window.addEventListener('hashchange', () => this.handleHashRoute());
      window.addEventListener('DOMContentLoaded', () => this.handleHashRoute());
      if (document.readyState === 'complete' || document.readyState === 'interactive') {
        this.handleHashRoute();
      }
    },

    handleHashRoute() {
      const hash = window.location.hash || '';
      if (!hash || hash === '#' || hash === '#/') {
        if (typeof this.config.onOpenDashboard === 'function') {
          this.config.onOpenDashboard();
        }
        this.updateViewHeading('Dashboard');
        return;
      }

      if (hash.startsWith('#/topic/')) {
        const slug = hash.replace('#/topic/', '').trim().toLowerCase();
        const foundIdx = this.topics.findIndex(t => {
          return (t.id && t.id.toLowerCase() === slug) ||
                 (t.slug && t.slug.toLowerCase() === slug);
        });
        if (foundIdx !== -1) {
          if (typeof this.config.onSelectTopic === 'function') {
            this.config.onSelectTopic(foundIdx);
          }
        }
        return;
      }

      if (hash === '#/simulator' && typeof this.config.onOpenSimulator === 'function') {
        this.config.onOpenSimulator();
        return;
      }
      if (hash === '#/spotters' && typeof this.config.onOpenSpotters === 'function') {
        this.config.onOpenSpotters();
        return;
      }
      if (hash === '#/flashcards' && typeof this.config.onOpenFlashcards === 'function') {
        this.config.onOpenFlashcards();
        return;
      }
      if (hash === '#/cheatsheet' && typeof this.config.onOpenCheatSheet === 'function') {
        this.config.onOpenCheatSheet();
        return;
      }
    },

    /* -------------------------------------------------------------
       KEYBOARD SHORTCUTS (/ focuses search, [ / ] navigate topics)
       NOTE: NO Ctrl+K listener. Browser native Ctrl+K is untouched!
    ------------------------------------------------------------- */
    initKeyboard() {
      window.addEventListener('keydown', (e) => {
        const tag = (e.target && e.target.tagName) || '';
        const isEditing = tag === 'INPUT' || tag === 'TEXTAREA' || e.target.isContentEditable;

        // "/" focuses sidebar search when not typing in an input
        if (e.key === '/' && !isEditing) {
          e.preventDefault();
          this.toggleSidebar(true);
          const searchInput = document.getElementById('sidebarSearchInput');
          if (searchInput) {
            searchInput.focus();
            searchInput.select();
          }
          return;
        }

        // "[" and "]" navigate to previous/next topic
        if (!isEditing && (e.key === '[' || e.key === ']')) {
          e.preventDefault();
          this.navigateTopic(e.key === '[' ? -1 : 1);
          return;
        }

        // Escape clears search or closes drawer
        if (e.key === 'Escape') {
          const searchInput = document.getElementById('sidebarSearchInput');
          if (searchInput && document.activeElement === searchInput && searchInput.value) {
            searchInput.value = '';
            this.onSidebarSearch('');
            searchInput.blur();
          } else {
            this.toggleSidebar(false);
            this.closeTimerPopover();
            this.closeTopbarOverflow();
          }
          return;
        }

        // Arrow navigation inside topic list (roving tabindex)
        if (!isEditing && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
          const rows = Array.from(document.querySelectorAll('.topic-row:not([style*="display: none"])'));
          if (rows.length === 0) return;
          e.preventDefault();
          if (e.key === 'ArrowDown') {
            this.focusedRowIndex = (this.focusedRowIndex + 1) % rows.length;
          } else {
            this.focusedRowIndex = (this.focusedRowIndex - 1 + rows.length) % rows.length;
          }
          rows[this.focusedRowIndex].focus();
        }
      });

      // Close popovers when clicking outside
      document.addEventListener('click', (e) => {
        if (!e.target.closest('.focus-timer-container') && !e.target.closest('.topbar-timer-wrapper')) {
          this.closeTimerPopover();
        }
        if (!e.target.closest('.topbar-overflow-wrapper')) {
          this.closeTopbarOverflow();
        }
      });
    },

    /* -------------------------------------------------------------
       PORTAL SIDEBAR COMPONENT
    ------------------------------------------------------------- */
    renderSidebar() {
      const cfg = this.config;
      const sidebarEl = document.getElementById('sidebar');
      if (!sidebarEl) return;

      sidebarEl.className = 'portal-sidebar' + (this.railCollapsed ? ' rail-collapsed' : '');
      sidebarEl.setAttribute('data-testid', 'sidebar');
      sidebarEl.setAttribute('role', 'navigation');
      sidebarEl.setAttribute('aria-label', `${cfg.name || 'Portal'} Sidebar`);

      // Ensure drawer scrim exists
      let scrim = document.getElementById('drawerScrim');
      if (!scrim) {
        scrim = document.createElement('div');
        scrim.id = 'drawerScrim';
        scrim.className = 'drawer-scrim';
        scrim.setAttribute('data-testid', 'drawer-scrim');
        scrim.onclick = () => this.toggleSidebar(false);
        document.body.appendChild(scrim);
      }

      // Group topics by category
      const categories = this.getGroupedTopics();

      sidebarEl.innerHTML = `
        <!-- 1. Brand Block (Height 64px, exact match to topbar) -->
        <div class="sidebar-brand-block" data-testid="sidebar-brand" onclick="CoreEngine.onBrandClick()">
          <div class="sidebar-brand-inner">
            <div class="sidebar-logo-tile">
              ${cfg.logoSvg || ''}
            </div>
            <div class="sidebar-brand-text">
              <div class="sidebar-wordmark">${cfg.name || 'PORTAL PRO'}</div>
              <div class="sidebar-subtitle">${cfg.subtitle || 'Clinical monograph'}</div>
            </div>
          </div>
          <button class="sidebar-drawer-close" data-testid="drawer-close" aria-label="Close menu" onclick="event.stopPropagation(); CoreEngine.toggleSidebar(false)">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
          </button>
        </div>

        <!-- 2. Back to Vault (Quiet Text Link) -->
        <div class="sidebar-back-row">
          <a href="${cfg.hubUrl || 'https://krrish41.github.io/bds-vault/'}" class="back-to-vault-link" data-testid="back-to-vault" aria-label="Back to BDS Clinical Vault">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
            <span>BDS Clinical Vault</span>
          </a>
        </div>

        <!-- 3. Dashboard Nav Item -->
        <div class="sidebar-nav-section">
          <button class="sidebar-nav-item active" id="sidebarNavDashboard" data-testid="nav-dashboard" onclick="CoreEngine.onDashboardClick()">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/></svg>
            <span>Dashboard</span>
          </button>
        </div>

        <!-- 4. Search Box (Single plain search — NO Ctrl K keycaps) -->
        <div class="sidebar-search-box" data-testid="sidebar-search">
          <div class="search-input-wrapper">
            <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            <input type="search" id="sidebarSearchInput" class="sidebar-search-input" data-testid="search" placeholder="${cfg.searchPlaceholder || 'Search topics, signs, procedures...'}" aria-label="Search curriculum" autocomplete="off" oninput="CoreEngine.onSidebarSearch(this.value)" />
            <button class="search-clear-btn" id="sidebarSearchClear" style="display:none;" aria-label="Clear search" onclick="CoreEngine.clearSearch()">×</button>
          </div>
          <div class="search-feedback-row" id="searchFeedbackRow" style="display:none;">
            <span class="search-result-count" id="searchResultCount"></span>
            <span class="search-cross-links" id="searchCrossLinks"></span>
          </div>
          <div class="active-filter-container" id="activeFilterContainer" style="display:none;">
            <span class="active-filter-chip" data-testid="active-filter-chip">
              <span id="activeFilterLabel">Pending</span>
              <button class="filter-chip-remove" onclick="CoreEngine.resetDashboardFilter()" aria-label="Remove filter">×</button>
            </span>
          </div>
        </div>

        <!-- 6. Progress Card & 7. Continue Shortcut -->
        <div class="sidebar-progress-card">
          <div class="progress-info-row">
            <span class="progress-label">Syllabus</span>
            <span class="progress-count" data-testid="progress" id="sidebarProgressText">0 / ${this.topics.length}</span>
          </div>
          <div class="progress-bar-track">
            <div class="progress-bar-fill" id="sidebarProgressBar" style="width: 0%;"></div>
          </div>
          <div class="continue-shortcut" data-testid="continue-shortcut" id="sidebarContinueShortcut" onclick="CoreEngine.onContinueClick()">
            <span class="continue-arrow">▶</span>
            <span class="continue-text" id="sidebarContinueText">Start: 1. ${this.topics[0] ? this.topics[0].title : ''}</span>
          </div>
        </div>

        <!-- 8. Grouped Topic List with Collapsible Categories -->
        <div class="sidebar-topics-wrapper" id="sidebarTopicsContainer" data-testid="sidebar-topics">
          <div class="group-control-bar">
            <span class="curriculum-heading">CURRICULUM TOPICS</span>
            <button class="accordion-toggle-all" id="btnToggleAllGroups" onclick="CoreEngine.toggleAllGroups()">Collapse all</button>
          </div>
          <div class="sidebar-groups-list" id="sidebarGroupsList" role="tree" aria-label="Topics grouped by category">
            ${this.renderCategoryGroupsHtml(categories)}
          </div>
        </div>

        <!-- 14. Sidebar Footer -->
        <div class="sidebar-footer">
          <div class="sidebar-action-links">
            <a href="https://github.com/Krrish41/bds-vault" target="_blank" rel="noopener" class="sidebar-action-btn star-highlight" data-testid="sidebar-star-vault" title="Star BDS Clinical Vault on GitHub">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
              <span>Star on GitHub</span>
            </a>
            <button type="button" class="sidebar-action-btn" onclick="CoreEngine.openFeedbackModal()" data-testid="sidebar-feedback-btn" title="Send Feedback or Report a Bug">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
              <span>Report Bug / Feedback</span>
            </button>
          </div>
          <span class="footer-version">BDS Clinical Vault · v2.2.0</span>
        </div>
      `;

      this.updateProgressDisplays();
    },

    getGroupedTopics() {
      const groups = {};
      this.topics.forEach((ch, idx) => {
        const cat = ch.category || 'General';
        if (!groups[cat]) groups[cat] = [];
        groups[cat].push({ topic: ch, index: idx });
      });
      return groups;
    },

    renderCategoryGroupsHtml(groups) {
      const groupNames = Object.keys(groups);
      if (groupNames.length === 0) {
        return '<div style="padding:16px; color:var(--text-muted); text-align:center;">No topics found.</div>';
      }

      return groupNames.map(cat => {
        const items = groups[cat];
        const isCollapsed = !!this.collapsedGroups[cat];
        const completedCount = items.filter(it => this.isTopicCompleted(it.topic.id)).length;

        const rowsHtml = items.map(it => {
          const ch = it.topic;
          const idx = it.index;
          const isDone = this.isTopicCompleted(ch.id);
          const hasNotes = this.topicHasNotes(ch.id);
          const isActive = idx === this.currentTopicIndex;
          const readTime = ch.readMinutes ? `${ch.readMinutes}m` : (ch.readingTime ? ch.readingTime.replace(' min read', 'm') : '15m');

          return `
            <div class="topic-row${isActive ? ' active' : ''}"
                 data-testid="topic-row"
                 data-topic-id="${ch.id}"
                 data-topic-idx="${idx}"
                 role="treeitem"
                 tabindex="0"
                 aria-selected="${isActive ? 'true' : 'false'}"
                 onclick="CoreEngine.selectTopic(${idx})">
              <div class="topic-checkbox${isDone ? ' checked' : ''}"
                   data-testid="topic-checkbox"
                   role="checkbox"
                   aria-checked="${isDone ? 'true' : 'false'}"
                   title="${isDone ? 'Mark as incomplete' : 'Mark as done'}"
                   onclick="event.stopPropagation(); CoreEngine.toggleTopicComplete('${ch.id}', ${idx})">
                ${isDone ? '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>' : ''}
              </div>
              <div class="topic-row-content">
                <div class="topic-row-header">
                  <span class="topic-row-num">${idx + 1}.</span>
                  <div class="topic-row-title">${ch.title}</div>
                  <span class="topic-row-meta">${readTime}</span>
                  ${hasNotes ? '<svg class="topic-row-notes-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-label="Has Notes"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>' : ''}
                </div>
              </div>
            </div>
          `;
        }).join('');

        return `
          <div class="category-group${isCollapsed ? ' collapsed' : ''}" data-testid="category-group" data-category="${cat}">
            <button class="category-toggle" data-testid="category-toggle" onclick="CoreEngine.toggleGroup('${cat}')">
              <div class="category-toggle-left">
                <span class="category-chevron">▼</span>
                <span class="category-title">${cat}</span>
              </div>
              <span class="category-count" id="catCount_${cat.replace(/[^a-zA-Z0-9]/g, '_')}">${completedCount}/${items.length}</span>
            </button>
            <div class="category-topics" role="group">
              ${rowsHtml}
            </div>
          </div>
        `;
      }).join('');
    },

    /* -------------------------------------------------------------
       CATEGORY ACCORDION CONTROLS
    ------------------------------------------------------------- */
    toggleGroup(catName) {
      this.collapsedGroups[catName] = !this.collapsedGroups[catName];
      this.saveCollapsedGroups();
      const groupEl = document.querySelector(`.category-group[data-category="${catName}"]`);
      if (groupEl) {
        if (this.collapsedGroups[catName]) groupEl.classList.add('collapsed');
        else groupEl.classList.remove('collapsed');
      }
    },

    toggleAllGroups() {
      const groupEls = document.querySelectorAll('.category-group');
      const allCollapsed = Array.from(groupEls).every(el => el.classList.contains('collapsed'));
      const btn = document.getElementById('btnToggleAllGroups');

      groupEls.forEach(el => {
        const cat = el.getAttribute('data-category');
        if (allCollapsed) {
          el.classList.remove('collapsed');
          if (cat) this.collapsedGroups[cat] = false;
        } else {
          el.classList.add('collapsed');
          if (cat) this.collapsedGroups[cat] = true;
        }
      });

      this.saveCollapsedGroups();
      if (btn) btn.textContent = allCollapsed ? 'Collapse all' : 'Expand all';
    },

    /* -------------------------------------------------------------
       COMPLETION & PROGRESS TRACKING
    ------------------------------------------------------------- */
    getCompletedTopicsMap() {
      const key = `bds.${this.portalKey}.progress`;
      try {
        const raw = localStorage.getItem(key);
        if (raw) {
          const parsed = JSON.parse(raw);
          if (Array.isArray(parsed)) {
            const map = {};
            parsed.forEach(id => { map[id] = true; });
            return map;
          }
          if (typeof parsed === 'object') return parsed;
        }
      } catch (e) {}
      return {};
    },

    isTopicCompleted(topicId) {
      const map = this.getCompletedTopicsMap();
      return !!map[topicId];
    },

    topicHasNotes(topicId) {
      try {
        const note = localStorage.getItem(`bds.${this.portalKey}.notes.${topicId}`) ||
                     localStorage.getItem(`notes_${topicId}`);
        return !!(note && note.trim());
      } catch (e) {
        return false;
      }
    },

    toggleTopicComplete(topicId, topicIdx) {
      const key = `bds.${this.portalKey}.progress`;
      const map = this.getCompletedTopicsMap();
      const willBeCompleted = !map[topicId];
      if (willBeCompleted) map[topicId] = true;
      else delete map[topicId];

      try {
        localStorage.setItem(key, JSON.stringify(map));
      } catch (e) {}

      // Update row checkbox
      const row = document.querySelector(`.topic-row[data-topic-id="${topicId}"]`);
      if (row) {
        const cb = row.querySelector('.topic-checkbox');
        if (cb) {
          if (willBeCompleted) {
            cb.classList.add('checked');
            cb.setAttribute('aria-checked', 'true');
            cb.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';
          } else {
            cb.classList.remove('checked');
            cb.setAttribute('aria-checked', 'false');
            cb.innerHTML = '';
          }
        }
      }

      this.updateProgressDisplays();

      // Notify host portal app
      if (typeof this.config.onToggleComplete === 'function') {
        this.config.onToggleComplete(topicId, willBeCompleted);
      }
    },

    updateProgressDisplays() {
      const map = this.getCompletedTopicsMap();
      const completedCount = Object.keys(map).length;
      const total = this.topics.length;
      const pct = total > 0 ? Math.round((completedCount / total) * 100) : 0;

      // Update sidebar progress
      const txtEl = document.getElementById('sidebarProgressText');
      if (txtEl) txtEl.textContent = `${completedCount} / ${total}`;

      const barEl = document.getElementById('sidebarProgressBar');
      if (barEl) barEl.style.width = `${pct}%`;

      // Update Continue shortcut
      this.updateContinueShortcut();

      // Synchronize all sidebar checkboxes with current completion map
      document.querySelectorAll('.topic-row').forEach(row => {
        const id = row.getAttribute('data-topic-id');
        const cb = row.querySelector('.topic-checkbox');
        if (cb && id) {
          const isDone = !!map[id];
          cb.classList.toggle('checked', isDone);
          cb.setAttribute('aria-checked', isDone ? 'true' : 'false');
          cb.innerHTML = isDone ? '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>' : '';
        }
      });

      // Update category header counts
      const groups = this.getGroupedTopics();
      Object.keys(groups).forEach(cat => {
        const items = groups[cat];
        const done = items.filter(it => !!map[it.topic.id]).length;
        const cntEl = document.getElementById(`catCount_${cat.replace(/[^a-zA-Z0-9]/g, '_')}`);
        if (cntEl) cntEl.textContent = `${done}/${items.length}`;
      });

      // Update portal dashboard stats if present
      const statCompleted = document.getElementById('statCompleted');
      if (statCompleted) statCompleted.textContent = completedCount;
      const statRemaining = document.getElementById('statRemaining');
      if (statRemaining) statRemaining.textContent = Math.max(0, total - completedCount);
      const dashProgressBar = document.getElementById('dashProgressBar');
      if (dashProgressBar) dashProgressBar.style.width = `${pct}%`;
      const dashProgressPercent = document.getElementById('dashProgressPercent');
      if (dashProgressPercent) dashProgressPercent.textContent = `${pct}%`;
    },

    getNextTopicToStudy() {
      if (!this.topics || this.topics.length === 0) return null;
      const map = this.getCompletedTopicsMap();
      const lastVisited = localStorage.getItem(`bds.${this.portalKey}.lastTopic`);

      // If last visited topic exists and is still uncompleted, resume it
      if (lastVisited) {
        const found = this.topics.findIndex(t => t.id === lastVisited);
        if (found !== -1 && !map[this.topics[found].id]) {
          return { index: found, topic: this.topics[found], isAllComplete: false };
        }
        // If last visited topic IS completed, find the next incomplete topic forward in sequence
        if (found !== -1) {
          for (let i = found + 1; i < this.topics.length; i++) {
            if (!map[this.topics[i].id]) {
              return { index: i, topic: this.topics[i], isAllComplete: false };
            }
          }
          // Wrap around to search from start to found
          for (let i = 0; i < found; i++) {
            if (!map[this.topics[i].id]) {
              return { index: i, topic: this.topics[i], isAllComplete: false };
            }
          }
          // All topics are completed
          return { index: 0, topic: this.topics[0], isAllComplete: true };
        }
      }

      // No last visited topic: find the first uncompleted topic
      const firstIncomplete = this.topics.findIndex(t => !map[t.id]);
      if (firstIncomplete !== -1) {
        return { index: firstIncomplete, topic: this.topics[firstIncomplete], isAllComplete: false };
      }

      // All topics completed
      return { index: 0, topic: this.topics[0], isAllComplete: true };
    },

    updateContinueShortcut() {
      const textEl = document.getElementById('sidebarContinueText');
      if (!textEl || this.topics.length === 0) return;

      const next = this.getNextTopicToStudy();
      if (!next) return;

      const map = this.getCompletedTopicsMap();
      const hasProgress = Object.keys(map).length > 0;

      if (next.isAllComplete) {
        textEl.textContent = `Review: 1. ${next.topic.title}`;
      } else {
        const prefix = hasProgress ? 'Continue' : 'Start';
        textEl.textContent = `${prefix}: ${next.index + 1}. ${next.topic.title}`;
      }
    },

    onContinueClick() {
      const next = this.getNextTopicToStudy();
      if (!next) return;
      this.selectTopic(next.index);
    },

    /* -------------------------------------------------------------
       SEARCH & FILTER PIPELINE
    ------------------------------------------------------------- */
    onSidebarSearch(rawQuery) {
      const q = (rawQuery || '').trim().toLowerCase();
      const clearBtn = document.getElementById('sidebarSearchClear');
      const feedbackRow = document.getElementById('searchFeedbackRow');
      const countEl = document.getElementById('searchResultCount');
      const crossEl = document.getElementById('searchCrossLinks');

      if (clearBtn) clearBtn.style.display = q ? 'flex' : 'none';

      let matchingCount = 0;
      const groups = this.getGroupedTopics();

      Object.keys(groups).forEach(cat => {
        const items = groups[cat];
        let catHasMatch = false;

        items.forEach(it => {
          const ch = it.topic;
          const row = document.querySelector(`.topic-row[data-topic-id="${ch.id}"]`);
          if (!row) return;

          // Search criteria: title, category, tags, and sections
          const tagsStr = (ch.tags || []).join(' ').toLowerCase();
          const matchesQuery = !q ||
            ch.title.toLowerCase().includes(q) ||
            (ch.category && ch.category.toLowerCase().includes(q)) ||
            tagsStr.includes(q) ||
            (ch.sections && JSON.stringify(ch.sections).toLowerCase().includes(q));

          // Check dashboard status filter
          const isDone = this.isTopicCompleted(ch.id);
          const hasNotes = this.topicHasNotes(ch.id);
          let matchesFilter = true;
          if (this.statusFilter === 'pending') matchesFilter = !isDone;
          else if (this.statusFilter === 'completed') matchesFilter = isDone;
          else if (this.statusFilter === 'notes') matchesFilter = hasNotes;

          const visible = matchesQuery && matchesFilter;
          row.style.display = visible ? 'flex' : 'none';

          if (visible) {
            matchingCount++;
            catHasMatch = true;
            // Highlight matching text in title
            const titleEl = row.querySelector('.topic-row-title');
            if (titleEl) {
              if (q) {
                const regex = new RegExp(`(${this.escapeRegex(q)})`, 'gi');
                titleEl.innerHTML = ch.title.replace(regex, '<mark class="search-match">$1</mark>');
              } else {
                titleEl.textContent = ch.title;
              }
            }
          }
        });

        // Auto-expand group if it has matches when searching
        const groupEl = document.querySelector(`.category-group[data-category="${cat}"]`);
        if (groupEl) {
          if (q) {
            if (catHasMatch) {
              groupEl.style.display = 'block';
              groupEl.classList.remove('collapsed');
            } else {
              groupEl.style.display = 'none';
            }
          } else {
            groupEl.style.display = 'block';
            if (this.collapsedGroups[cat]) groupEl.classList.add('collapsed');
            else groupEl.classList.remove('collapsed');
          }
        }
      });

      // Update feedback row
      if (feedbackRow && countEl) {
        if (q || this.statusFilter !== 'all') {
          feedbackRow.style.display = 'flex';
          countEl.textContent = `${matchingCount} of ${this.topics.length} topics`;
          if (crossEl) {
            crossEl.innerHTML = `Also in: <a href="javascript:void(0)" onclick="CoreEngine.triggerTool('spotters')">Spotters</a> · <a href="javascript:void(0)" onclick="CoreEngine.triggerTool('flashcards')">Flashcards</a>`;
          }
        } else {
          feedbackRow.style.display = 'none';
        }
      }
    },

    clearSearch() {
      const searchInput = document.getElementById('sidebarSearchInput');
      if (searchInput) {
        searchInput.value = '';
        this.onSidebarSearch('');
        searchInput.focus();
      }
    },

    escapeRegex(str) {
      return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    },

    /* -------------------------------------------------------------
       DASHBOARD SHARED FILTER STATE
    ------------------------------------------------------------- */
    setDashboardStatusFilter(status) {
      this.statusFilter = status || 'all';
      const container = document.getElementById('activeFilterContainer');
      const label = document.getElementById('activeFilterLabel');

      if (container && label) {
        if (this.statusFilter !== 'all') {
          container.style.display = 'block';
          label.textContent = this.statusFilter.charAt(0).toUpperCase() + this.statusFilter.slice(1);
        } else {
          container.style.display = 'none';
        }
      }

      // Re-run search pipeline with new filter
      const searchInput = document.getElementById('sidebarSearchInput');
      this.onSidebarSearch(searchInput ? searchInput.value : '');
    },

    resetDashboardFilter() {
      this.setDashboardStatusFilter('all');
      if (typeof this.config.onResetStatusFilter === 'function') {
        this.config.onResetStatusFilter();
      }
    },

    /* -------------------------------------------------------------
       PORTAL TOPBAR COMPONENT
    ------------------------------------------------------------- */
    renderTopBar() {
      const cfg = this.config;
      const topbarEl = document.getElementById('portalTopBar');
      if (!topbarEl) return;

      topbarEl.className = 'portal-topbar';
      topbarEl.setAttribute('data-testid', 'topbar');

      topbarEl.innerHTML = `
        <div class="topbar-left">
          <!-- Drawer toggle (<1024px) / Rail toggle (≥1024px) -->
          <button class="topbar-btn drawer-toggle-btn" id="btnDrawerOpen" aria-label="Open navigation drawer" onclick="CoreEngine.toggleSidebar(true)">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
          </button>
          <button class="topbar-btn rail-toggle-btn" id="btnRailToggle" data-testid="rail-toggle" aria-label="Toggle sidebar width" onclick="CoreEngine.toggleSidebarRail()">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 3v18"/></svg>
          </button>

          <!-- Topbar Title / Breadcrumb -->
          <div class="topbar-title-block" data-testid="topbar-title" id="topbarTitle">
            Exam Preparation Dashboard
          </div>

          <!-- Prev / Next Topic Navigation -->
          <div class="topbar-topic-nav" id="topbarTopicNav" style="display: none;">
            <button class="topbar-nav-arrow" data-testid="topic-prev" id="btnPrevTopic" aria-label="Previous Topic" title="Previous Topic ([)" onclick="CoreEngine.navigateTopic(-1)">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
            </button>
            <button class="topbar-nav-arrow" data-testid="topic-next" id="btnNextTopic" aria-label="Next Topic" title="Next Topic (])" onclick="CoreEngine.navigateTopic(1)">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
            </button>
          </div>
        </div>

        <div class="topbar-right">
          <!-- 1. Audio Walk -->
          <button class="topbar-tool-btn audio-walk-btn" data-testid="audio-walkthrough" onclick="CoreEngine.toggleAudioWalk()" title="Continuous Audio Walk">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/></svg>
            <span class="btn-text">Audio Walk</span>
          </button>

          <!-- 2. Focus Timer with Popover (Synced across all portals and hub) -->
          <div class="topbar-timer-wrapper focus-timer-container">
            <button class="topbar-tool-btn timer-btn timer-nav-pill" data-testid="focus-timer" id="topbarTimerBtn" onclick="CoreEngine.toggleTimerPopover(event)" title="Toggle Focus Study Timer" aria-haspopup="dialog" aria-expanded="false">
              <span class="timer-chip-dot"></span>
              <span class="btn-text mono-num" id="topbarTimerText">25:00</span>
              <span class="timer-state-label" id="topbarTimerStateText">Focus</span>
            </button>
            <div class="timer-popover-card timer-popover" id="timerPopover" onclick="event.stopPropagation()">
              <div class="timer-popover-header" id="timerModeLabel">High-Yield Focus Block</div>
              <div class="timer-popover-digits mono-num" id="timerPopoverTime">25:00</div>
              <div class="timer-popover-controls">
                <button class="timer-ctrl-btn primary" id="btnTimerStartPause" onclick="CoreEngine.toggleTimer()">Start Focus</button>
                <button class="timer-ctrl-btn" id="btnPreset25" onclick="CoreEngine.resetTimer(25)">25m</button>
                <button class="timer-ctrl-btn" id="btnPreset50" onclick="CoreEngine.resetTimer(50)">50m</button>
                <button class="timer-ctrl-btn" id="btnTimerReset" onclick="CoreEngine.resetTimer(25)">Reset</button>
              </div>
            </div>
          </div>

          <!-- 3. Command Palette / Search Trigger -->
          <button class="topbar-tool-btn palette-btn" data-testid="palette" style="display: none !important;" onclick="CoreEngine.toggleSidebar(true); const el = document.getElementById('sidebarSearchInput'); if (el) { el.focus(); el.select(); }" title="Search Curriculum (/)" aria-label="Search Curriculum">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            <span class="btn-text">Search</span>
          </button>

          <!-- 4. Master PDF -->
          <a href="${cfg.pdfUrl || '#'}" class="topbar-tool-btn pdf-btn" data-testid="open-pdf" title="Typeset Master PDF Monograph" target="_blank" rel="noopener">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            <span class="btn-text">Master PDF</span>
          </a>

          <!-- 5. Star BDS Vault -->
          <a href="https://github.com/Krrish41/bds-vault" class="topbar-tool-btn star-btn" data-testid="star-vault" target="_blank" rel="noopener" title="Star BDS Vault on GitHub">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            <span class="btn-text">Star</span>
          </a>

          <!-- 6. Theme Toggle -->
          <button class="topbar-tool-btn theme-toggle-btn" data-testid="theme-toggle" onclick="CoreEngine.toggleTheme()" title="Toggle Theme (Dark/Light)">
            <svg class="icon-moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
            <svg class="icon-sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>
          </button>

          <!-- 7. Overflow Menu (Small screens) -->
          <div class="topbar-overflow-wrapper" id="topbarOverflowWrapper">
            <button class="topbar-tool-btn overflow-btn" data-testid="topbar-overflow" onclick="CoreEngine.toggleTopbarOverflow()" aria-label="More tools">⋯</button>
            <div class="topbar-overflow-menu" id="topbarOverflowMenu">
              <a href="${cfg.hubUrl || 'https://krrish41.github.io/bds-vault/'}" class="overflow-item">‹ Back to Vault</a>
              <a href="${cfg.pdfUrl || '#'}" class="overflow-item" target="_blank" rel="noopener"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:inline-block; vertical-align:middle; margin-right:6px;" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>Master PDF</a>
              <button class="overflow-item" onclick="CoreEngine.toggleTheme()"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:inline-block; vertical-align:middle; margin-right:6px;" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 2a10 10 0 0 0 0 20z" fill="currentColor"/></svg>Toggle Theme</button>
              <a href="https://github.com/Krrish41/bds-vault" class="overflow-item" target="_blank" rel="noopener"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:inline-block; vertical-align:middle; margin-right:6px;" aria-hidden="true"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>Star on GitHub</a>
              <button class="overflow-item" onclick="CoreEngine.openFeedbackModal()"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:inline-block; vertical-align:middle; margin-right:6px;" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>Report Bug / Feedback</button>
            </div>
          </div>
        </div>
      `;
    },

    updateViewHeading(title, category, chapterNum) {
      const headingEl = document.getElementById('topbarTitle');
      const topicNav = document.getElementById('topbarTopicNav');
      const dashBtn = document.getElementById('sidebarNavDashboard');

      if (!headingEl) return;

      if (title === 'Dashboard') {
        document.body.classList.add('is-dashboard');
        headingEl.textContent = 'Exam Preparation Dashboard';
        if (topicNav) topicNav.style.display = 'none';
        if (dashBtn) dashBtn.classList.add('active');
        document.querySelectorAll('.topic-row').forEach(r => r.classList.remove('active'));
      } else {
        document.body.classList.remove('is-dashboard');
        const catStr = category ? `${category} › ` : '';
        const numStr = chapterNum ? `${chapterNum}. ` : '';
        headingEl.textContent = `${catStr}${numStr}${title}`;
        if (topicNav) topicNav.style.display = 'flex';
        if (dashBtn) dashBtn.classList.remove('active');
      }
    },

    /* -------------------------------------------------------------
       TOPIC SELECTION & NAVIGATION
    ------------------------------------------------------------- */
    selectTopic(index) {
      if (index < 0 || index >= this.topics.length) return;
      this.currentTopicIndex = index;
      document.body.classList.remove('is-dashboard');
      const topic = this.topics[index];

      // Save last visited topic
      try {
        localStorage.setItem(`bds.${this.portalKey}.lastTopic`, topic.id);
      } catch (e) {}

      // Update active state in sidebar
      document.querySelectorAll('.topic-row').forEach(r => r.classList.remove('active'));
      const activeRow = document.querySelector(`.topic-row[data-topic-id="${topic.id}"]`);
      if (activeRow) {
        activeRow.classList.add('active');
        activeRow.scrollIntoView({ block: 'nearest', behavior: 'smooth' });

        // Ensure category group is open
        const parentGroup = activeRow.closest('.category-group');
        if (parentGroup) {
          parentGroup.classList.remove('collapsed');
          const cat = parentGroup.getAttribute('data-category');
          if (cat) this.collapsedGroups[cat] = false;
        }
      }

      // Update topbar breadcrumb
      this.updateViewHeading(topic.title, topic.category, index + 1);

      // Close mobile drawer after selection
      this.toggleSidebar(false);

      // Invoke portal view callback
      if (typeof this.config.onSelectTopic === 'function') {
        this.config.onSelectTopic(index);
      }
    },

    navigateTopic(delta) {
      if (this.topics.length === 0) return;
      let nextIdx = this.currentTopicIndex + delta;
      if (this.currentTopicIndex === -1) nextIdx = 0;
      if (nextIdx < 0) nextIdx = 0;
      if (nextIdx >= this.topics.length) nextIdx = this.topics.length - 1;
      this.selectTopic(nextIdx);
    },

    /* -------------------------------------------------------------
       SIDEBAR & DRAWER CONTROLS
    ------------------------------------------------------------- */
    toggleSidebar(open) {
      const sidebar = document.getElementById('sidebar');
      const scrim = document.getElementById('drawerScrim');
      if (!sidebar) return;

      if (open) {
        sidebar.classList.add('open');
        if (scrim) scrim.classList.add('open');
        document.body.style.overflow = 'hidden';
      } else {
        sidebar.classList.remove('open');
        if (scrim) scrim.classList.remove('open');
        document.body.style.overflow = '';
      }
    },

    onBrandClick() {
      this.toggleSidebar(false);
      if (typeof this.config.onOpenDashboard === 'function') {
        this.config.onOpenDashboard();
      }
    },

    onDashboardClick() {
      this.toggleSidebar(false);
      this.currentTopicIndex = -1;
      this.updateViewHeading('Dashboard');
      if (typeof this.config.onOpenDashboard === 'function') {
        this.config.onOpenDashboard();
      }
    },

    triggerTool(toolId) {
      this.toggleSidebar(false);
      if (toolId === 'simulator' && typeof this.config.onOpenSimulator === 'function') {
        this.config.onOpenSimulator();
      } else if (toolId === 'spotters' && typeof this.config.onOpenSpotters === 'function') {
        this.config.onOpenSpotters();
      } else if (toolId === 'flashcards' && typeof this.config.onOpenFlashcards === 'function') {
        this.config.onOpenFlashcards();
      } else if (toolId === 'cheatsheet' && typeof this.config.onOpenCheatSheet === 'function') {
        this.config.onOpenCheatSheet();
      }
    },

    toggleAudioWalk() {
      if (typeof this.config.onToggleAudioWalk === 'function') {
        this.config.onToggleAudioWalk();
      } else if (typeof window.openAudioSectionModal === 'function') {
        window.openAudioSectionModal();
      } else if (typeof window.togglePlayPauseAudio === 'function') {
        window.togglePlayPauseAudio();
      } else if (typeof window.playContinuousChapterAudio === 'function') {
        window.playContinuousChapterAudio();
      }
    },

    setAudioPlayingState(isPlaying) {
      document.querySelectorAll('.audio-walk-btn').forEach(btn => {
        btn.classList.toggle('active', !!isPlaying);
        btn.classList.toggle('is-playing', !!isPlaying);
      });
    },

    toggleTimerPopover(event) {
      if (event) event.stopPropagation();
      const pop = document.getElementById('timerPopover');
      const btn = document.getElementById('topbarTimerBtn') || document.getElementById('navTimerPill');
      if (!pop) return;
      const isOpen = pop.classList.contains('open');
      if (isOpen) {
        pop.classList.remove('open');
        if (btn) btn.setAttribute('aria-expanded', 'false');
      } else {
        pop.classList.add('open');
        if (btn) btn.setAttribute('aria-expanded', 'true');
      }
      this.closeTopbarOverflow();
    },

    closeTimerPopover() {
      const pop = document.getElementById('timerPopover');
      const btn = document.getElementById('topbarTimerBtn') || document.getElementById('navTimerPill');
      if (pop) pop.classList.remove('open');
      if (btn) btn.setAttribute('aria-expanded', 'false');
    },

    toggleTimer() {
      if (window.BdsTimer) window.BdsTimer.toggle();
    },

    resetTimer(mins) {
      if (window.BdsTimer) {
        window.BdsTimer.reset(mins);
        window.BdsTimer.start(mins);
      }
    },

    toggleTopbarOverflow() {
      const menu = document.getElementById('topbarOverflowMenu');
      if (menu) menu.classList.toggle('open');
      this.closeTimerPopover();
    },

    closeTopbarOverflow() {
      const menu = document.getElementById('topbarOverflowMenu');
      if (menu) menu.classList.remove('open');
    },

    /* -------------------------------------------------------------
       FEEDBACK & BUG REPORT MODAL SUBSYSTEM
    ------------------------------------------------------------- */
    getClientDiagnostics() {
      const ua = navigator.userAgent || '';
      let os = 'Unknown OS';
      if (/Windows NT 10.0/i.test(ua)) os = 'Windows 10/11';
      else if (/Windows NT/i.test(ua)) os = 'Windows PC';
      else if (/iPhone/i.test(ua)) os = 'iOS (iPhone)';
      else if (/iPad/i.test(ua)) os = 'iPadOS';
      else if (/Android/i.test(ua)) os = 'Android';
      else if (/Macintosh|Mac OS X/i.test(ua)) os = 'macOS';
      else if (/Linux/i.test(ua)) os = 'Linux';

      let browser = 'Unknown Browser';
      if (/Edg\//i.test(ua)) browser = 'Microsoft Edge';
      else if (/Chrome\//i.test(ua) && !/Edg\//i.test(ua)) browser = 'Google Chrome';
      else if (/Safari\//i.test(ua) && !/Chrome\//i.test(ua)) browser = 'Apple Safari';
      else if (/Firefox\//i.test(ua)) browser = 'Mozilla Firefox';

      const portalNames = {
        surgery: 'General Surgery Pro (Paper I)',
        medicine: 'General Medicine Pro (Paper II)',
        pathology: 'Oral Pathology Pro (Paper III)',
        vault: 'BDS Clinical Vault (Hub)'
      };
      const portalName = portalNames[this.portalKey] || 'BDS Clinical Vault';

      let locationStr = 'Dashboard / Overview';
      if (this.currentTopicIndex >= 0 && this.topics && this.topics[this.currentTopicIndex]) {
        locationStr = `Chapter ${this.currentTopicIndex + 1}: ${this.topics[this.currentTopicIndex].title}`;
      } else if (window.location.hash) {
        locationStr = `Route: ${window.location.hash}`;
      }

      const screenRes = `${window.screen ? window.screen.width + 'x' + window.screen.height : 'Unknown'} (Viewport: ${window.innerWidth}x${window.innerHeight})`;
      const theme = document.documentElement.getAttribute('data-theme') || 'dark';
      const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19) + ' UTC';

      return {
        portalName,
        locationStr,
        url: window.location.href,
        os,
        browser,
        screenRes,
        theme,
        timestamp
      };
    },

    generateFeedbackTemplate() {
      const diag = this.getClientDiagnostics();
      return `[BDS Clinical Vault — Bug Report / Clinical Feedback]

1. ENVIRONMENT & CONTEXT:
• Portal / Specialty: ${diag.portalName}
• Current Location: ${diag.locationStr}
• Page URL: ${diag.url}
• Device & OS: ${diag.os}
• Web Browser: ${diag.browser}
• Screen & Viewport: ${diag.screenRes}
• Theme Mode: ${diag.theme}
• Timestamp: ${diag.timestamp}

2. ISSUE CATEGORY:
[ ] Broken Link / Button / Navigation
[ ] Audio Walk / TTS Island Glitch
[ ] Exam Simulator / Flashcard Rubric Issue
[ ] Clinical Inaccuracy / Drug Dosage / Typo
[ ] Layout / Display / Mobile Responsiveness
[ ] Other / General Feedback

3. DESCRIPTION OF ISSUE:
What happened:
[Describe the bug or issue here]

Expected behavior:
[What should have happened instead]

4. STEPS TO REPRODUCE:
1. 
2. 
3. 

5. CLINICAL CORRECTION (if reporting textbook/monograph discrepancies):
• Standard Reference: [e.g. Shafer 9th ed, Chugh, Love & Bailey, WHO Criteria]
• Chapter / Page: 
• Correction Details: 

6. ATTACHMENTS:
(Please attach relevant screenshots or screen recordings if applicable)`;
    },

    ensureFeedbackModal() {
      let overlay = document.getElementById('bdsFeedbackModalOverlay');
      if (overlay) return overlay;

      overlay = document.createElement('div');
      overlay.id = 'bdsFeedbackModalOverlay';
      overlay.className = 'bds-feedback-modal-overlay';
      overlay.setAttribute('role', 'dialog');
      overlay.setAttribute('aria-modal', 'true');
      overlay.setAttribute('aria-labelledby', 'bdsFeedbackTitle');
      overlay.onclick = (e) => {
        if (e.target === overlay) CoreEngine.closeFeedbackModal();
      };

      overlay.innerHTML = `
        <div class="bds-feedback-modal-card" onclick="event.stopPropagation()">
          <div class="bds-feedback-header">
            <div class="bds-feedback-title-wrap">
              <div class="bds-feedback-title" id="bdsFeedbackTitle">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                <span>Feedback &amp; Bug Report</span>
              </div>
              <div class="bds-feedback-sub">Help refine the BDS Clinical Vault ecosystem. Every issue report or clinical correction directly improves exam readiness for dental students.</div>
            </div>
            <button type="button" class="bds-feedback-close" onclick="CoreEngine.closeFeedbackModal()" aria-label="Close dialog">&times;</button>
          </div>

          <div class="bds-feedback-body">
            <!-- Direct Contact Card -->
            <div class="bds-contact-card">
              <div class="bds-contact-meta">
                <div class="bds-contact-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
                </div>
                <div class="bds-contact-details">
                  <span class="bds-contact-label">Direct Clinical Lead Contact</span>
                  <a href="mailto:krrish4173@gmail.com" class="bds-contact-email">krrish4173@gmail.com</a>
                </div>
              </div>
              <div class="bds-contact-actions">
                <button type="button" class="bds-btn-pill" id="bdsCopyEmailBtn" onclick="CoreEngine.copyFeedbackEmail()">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
                  <span id="bdsCopyEmailText">Copy Email</span>
                </button>
                <a href="#" id="bdsFeedbackMailtoBtn" class="bds-btn-pill primary" target="_blank" rel="noopener">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                  <span>Open in Mail Client</span>
                </a>
              </div>
            </div>

            <!-- Standardized Bug Report Template -->
            <div class="bds-template-section">
              <div class="bds-template-header">
                <span class="bds-template-label">Standard Bug Report &amp; Correction Template</span>
                <button type="button" class="bds-btn-pill" id="bdsCopyTemplateBtn" onclick="CoreEngine.copyFeedbackTemplate()">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
                  <span id="bdsCopyTemplateText">Copy Template</span>
                </button>
              </div>
              <pre class="bds-template-box" id="bdsFeedbackTemplateText"></pre>
            </div>
          </div>

          <div class="bds-feedback-footer">
            <div class="bds-github-star-hint">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
              <span>Enjoying the study suite? Support us by giving a <a href="https://github.com/Krrish41/bds-vault" target="_blank" rel="noopener">Star to BDS Clinical Vault on GitHub</a>.</span>
            </div>
            <button type="button" class="bds-btn-pill" onclick="CoreEngine.closeFeedbackModal()">Close</button>
          </div>
        </div>
      `;

      document.body.appendChild(overlay);
      return overlay;
    },

    openFeedbackModal() {
      this.closeTopbarOverflow();
      const overlay = this.ensureFeedbackModal();
      const template = this.generateFeedbackTemplate();
      const templateBox = document.getElementById('bdsFeedbackTemplateText');
      if (templateBox) templateBox.textContent = template;

      const mailtoBtn = document.getElementById('bdsFeedbackMailtoBtn');
      if (mailtoBtn) {
        const diag = this.getClientDiagnostics();
        const subject = encodeURIComponent(`[BDS Vault Bug Report] Issue in ${diag.portalName}`);
        const body = encodeURIComponent(template);
        mailtoBtn.href = `mailto:krrish4173@gmail.com?subject=${subject}&body=${body}`;
      }

      overlay.classList.add('open');
      document.body.style.overflow = 'hidden';
    },

    closeFeedbackModal() {
      const overlay = document.getElementById('bdsFeedbackModalOverlay');
      if (overlay) overlay.classList.remove('open');
      document.body.style.overflow = '';
    },

    copyFeedbackTemplate() {
      const template = this.generateFeedbackTemplate();
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(template).then(() => {
          const btnText = document.getElementById('bdsCopyTemplateText');
          if (btnText) {
            btnText.textContent = 'Copied!';
            setTimeout(() => { btnText.textContent = 'Copy Template'; }, 2000);
          }
        }).catch(() => {});
      }
    },

    copyFeedbackEmail() {
      const email = 'krrish4173@gmail.com';
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(email).then(() => {
          const btnText = document.getElementById('bdsCopyEmailText');
          if (btnText) {
            btnText.textContent = 'Copied!';
            setTimeout(() => { btnText.textContent = 'Copy Email'; }, 2000);
          }
        }).catch(() => {});
      }
    }
  };

  /* =============================================================
     UNIVERSAL SYNCHRONIZED FOCUS TIMER
     (Zero Ctrl+K dependencies; Hydration & 3m walk break chime)
     ============================================================= */
  const BdsTimer = {
    STORAGE_KEY: 'bds.focus.timer',
    localInterval: null,
    walkInterval: null,

    getState() {
      try {
        const raw = localStorage.getItem(this.STORAGE_KEY);
        if (raw) return JSON.parse(raw);
      } catch (e) {}
      return {
        status: 'idle',
        durationMinutes: 25,
        remainingSeconds: 25 * 60,
        targetEndTime: null,
        lastUpdated: Date.now()
      };
    },

    saveState(state) {
      state.lastUpdated = Date.now();
      try {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(state));
      } catch (e) {}
      this.render();
    },

    init() {
      this.ensureRewardModal();
      this.render();

      window.addEventListener('storage', (e) => {
        if (e.key === this.STORAGE_KEY) this.render();
      });

      if (this.localInterval) clearInterval(this.localInterval);
      this.localInterval = setInterval(() => this.tick(), 500);
    },

    tick() {
      const state = this.getState();
      if (state.status === 'running') {
        const now = Date.now();
        const remaining = Math.max(0, Math.round((state.targetEndTime - now) / 1000));
        this.updateDisplays(remaining, true, false);

        if (remaining <= 0) {
          state.status = 'idle';
          state.remainingSeconds = (state.durationMinutes || 25) * 60;
          state.targetEndTime = null;
          this.saveState(state);
          this.triggerReward();
        }
      } else {
        this.updateDisplays(state.remainingSeconds, false, state.status === 'paused');
      }
    },

    start(minutes) {
      const state = this.getState();
      if (minutes) {
        state.durationMinutes = minutes;
        state.remainingSeconds = minutes * 60;
      }
      if (!state.remainingSeconds || state.remainingSeconds <= 0) {
        state.remainingSeconds = (state.durationMinutes || 25) * 60;
      }
      state.status = 'running';
      state.targetEndTime = Date.now() + (state.remainingSeconds * 1000);
      this.saveState(state);
    },

    pause() {
      const state = this.getState();
      if (state.status === 'running') {
        const remaining = Math.max(0, Math.round((state.targetEndTime - Date.now()) / 1000));
        state.remainingSeconds = remaining;
        state.status = 'paused';
        state.targetEndTime = null;
        this.saveState(state);
      }
    },

    toggle() {
      const state = this.getState();
      if (state.status === 'running') this.pause();
      else this.start();
    },

    reset(minutes) {
      const mins = minutes || 25;
      const state = {
        status: 'idle',
        durationMinutes: mins,
        remainingSeconds: mins * 60,
        targetEndTime: null,
        lastUpdated: Date.now()
      };
      this.saveState(state);
    },

    formatTime(sec) {
      const m = Math.floor(sec / 60);
      const s = sec % 60;
      return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    },

    updateDisplays(seconds, isRunning, isPaused) {
      const timeStr = this.formatTime(seconds);
      const stateLabel = isRunning ? 'Running' : (isPaused ? 'Paused' : 'Focus');

      // Topbar button display (Surgery, Medicine, Pathology)
      const topbarText = document.getElementById('topbarTimerText');
      if (topbarText) topbarText.textContent = timeStr;
      const topbarState = document.getElementById('topbarTimerStateText');
      if (topbarState) topbarState.textContent = stateLabel;

      const topbarBtn = document.getElementById('topbarTimerBtn');
      if (topbarBtn) {
        if (isRunning) topbarBtn.classList.add('running', 'active');
        else topbarBtn.classList.remove('running', 'active');
      }

      // Popover countdown digits
      const popoverTime = document.getElementById('timerPopoverTime');
      if (popoverTime) popoverTime.textContent = timeStr;
      const timerMainDigits = document.getElementById('timerMainDigits');
      if (timerMainDigits) timerMainDigits.textContent = timeStr;

      // Start / Pause buttons
      const actionText = isRunning ? 'Pause Focus' : (isPaused ? 'Resume Focus' : 'Start Focus');
      const btnStartPause = document.getElementById('btnTimerStartPause');
      if (btnStartPause) btnStartPause.textContent = actionText;
      const timerStartBtn = document.getElementById('timerStartBtn');
      if (timerStartBtn) timerStartBtn.textContent = actionText;

      // Hub Displays (bds-vault)
      const navTimerDisp = document.getElementById('navTimerDisplay');
      if (navTimerDisp) navTimerDisp.textContent = timeStr;
      const navTimerState = document.getElementById('navTimerStateText');
      if (navTimerState) navTimerState.textContent = stateLabel;

      const navTimerPill = document.getElementById('navTimerPill');
      if (navTimerPill) {
        if (isRunning) navTimerPill.classList.add('running', 'active');
        else navTimerPill.classList.remove('running', 'active');
      }

      // Preset buttons active indicators
      const state = this.getState();
      const p25 = document.getElementById('btnPreset25');
      const p50 = document.getElementById('btnPreset50');
      if (p25) p25.classList.toggle('active', state.durationMinutes === 25);
      if (p50) p50.classList.toggle('active', state.durationMinutes === 50);
    },

    render() {
      const state = this.getState();
      if (state.status === 'running') {
        const remaining = Math.max(0, Math.round((state.targetEndTime - Date.now()) / 1000));
        this.updateDisplays(remaining, true, false);
      } else {
        this.updateDisplays(state.remainingSeconds, false, state.status === 'paused');
      }
    },

    playChime() {
      try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return;
        const ctx = new AudioContext();
        const notes = [523.25, 659.25, 783.99, 1046.50];
        notes.forEach((freq, i) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.value = freq;
          gain.gain.setValueAtTime(0, ctx.currentTime + i * 0.15);
          gain.gain.linearRampToValueAtTime(0.2, ctx.currentTime + i * 0.15 + 0.05);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.15 + 0.8);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(ctx.currentTime + i * 0.15);
          osc.stop(ctx.currentTime + i * 0.15 + 0.85);
        });
      } catch (e) {}
    },

    triggerReward() {
      this.playChime();
      this.showRewardModal();
    },

    ensureRewardModal() {
      if (document.getElementById('bdsFocusRewardModal')) return;
      const modal = document.createElement('div');
      modal.id = 'bdsFocusRewardModal';
      modal.className = 'bds-reward-modal-backdrop';
      modal.innerHTML = `
        <div class="bds-reward-modal-card" role="dialog" aria-modal="true" aria-labelledby="bdsRewardTitle">
          <div class="bds-reward-icon-badge"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg></div>
          <h3 id="bdsRewardTitle" class="bds-reward-title">Focus Block Completed!</h3>
          <p class="bds-reward-msg">
            Walk for 3 mins without music or phone and hydrate yourself even if you're not feeling like drinking water.
          </p>
          <div class="bds-walk-timer-box" id="bdsWalkTimerBox" style="display:none;">
            <div class="bds-walk-digits" id="bdsWalkDigits">03:00</div>
            <div class="bds-walk-sub">Walking Break in Progress</div>
          </div>
          <div class="bds-reward-actions">
            <button class="bds-reward-btn primary" id="bdsStartWalkBtn" onclick="window.BdsTimer.startWalkBreak()">Start 3m Walk</button>
            <button class="bds-reward-btn secondary" onclick="window.BdsTimer.closeRewardModal()">Dismiss</button>
          </div>
        </div>
      `;
      document.body.appendChild(modal);

      if (!document.getElementById('bdsRewardModalStyles')) {
        const style = document.createElement('style');
        style.id = 'bdsRewardModalStyles';
        style.textContent = `
          .bds-reward-modal-backdrop {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(9, 10, 18, 0.85);
            backdrop-filter: blur(8px);
            z-index: 999999;
            align-items: center;
            justify-content: center;
            padding: 20px;
            box-sizing: border-box;
          }
          .bds-reward-modal-backdrop.open {
            display: flex;
            animation: bdsModalFadeIn 0.25s ease-out;
          }
          @keyframes bdsModalFadeIn {
            from { opacity: 0; transform: scale(0.96); }
            to { opacity: 1; transform: scale(1); }
          }
          .bds-reward-modal-card {
            background: #101322;
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.75);
            border-radius: 16px;
            max-width: 440px;
            width: 100%;
            padding: 28px 24px;
            text-align: center;
            box-sizing: border-box;
            color: #f8fafc;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          }
          .bds-reward-icon-badge {
            font-size: 2.4rem;
            line-height: 1;
            margin-bottom: 12px;
          }
          .bds-reward-title {
            font-size: 1.28rem;
            font-weight: 800;
            margin: 0 0 10px 0;
            color: #f8fafc;
          }
          .bds-reward-msg {
            font-size: 0.95rem;
            line-height: 1.55;
            color: #cbd5e1;
            margin: 0 0 20px 0;
            background: rgba(255, 255, 255, 0.04);
            padding: 14px 16px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            font-weight: 500;
          }
          .bds-walk-timer-box {
            margin-bottom: 18px;
            padding: 12px;
            background: rgba(20, 184, 166, 0.1);
            border: 1px solid rgba(20, 184, 166, 0.3);
            border-radius: 10px;
          }
          .bds-walk-digits {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.8rem;
            font-weight: 700;
            color: #5eead4;
          }
          .bds-walk-sub {
            font-size: 0.75rem;
            text-transform: uppercase;
            color: #94a3b8;
            letter-spacing: 0.05em;
            margin-top: 2px;
          }
          .bds-reward-actions {
            display: flex;
            gap: 10px;
            justify-content: center;
          }
          .bds-reward-btn {
            padding: 10px 18px;
            border-radius: 8px;
            font-size: 0.88rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 1px solid transparent;
          }
          .bds-reward-btn.primary {
            background: #14b8a6;
            color: #090a12;
            flex: 1;
          }
          .bds-reward-btn.primary:hover {
            background: #0d9488;
            color: #ffffff;
          }
          .bds-reward-btn.secondary {
            background: rgba(255, 255, 255, 0.06);
            color: #94a3b8;
            border-color: rgba(255, 255, 255, 0.12);
          }
          .bds-reward-btn.secondary:hover {
            background: rgba(255, 255, 255, 0.12);
            color: #f8fafc;
          }
        `;
        document.head.appendChild(style);
      }
    },

    showRewardModal() {
      this.ensureRewardModal();
      const modal = document.getElementById('bdsFocusRewardModal');
      if (modal) modal.classList.add('open');
    },

    closeRewardModal() {
      const modal = document.getElementById('bdsFocusRewardModal');
      if (modal) modal.classList.remove('open');
      if (this.walkInterval) {
        clearInterval(this.walkInterval);
        this.walkInterval = null;
      }
      const box = document.getElementById('bdsWalkTimerBox');
      const startBtn = document.getElementById('bdsStartWalkBtn');
      if (box) box.style.display = 'none';
      if (startBtn) startBtn.style.display = 'inline-block';
    },

    startWalkBreak() {
      const box = document.getElementById('bdsWalkTimerBox');
      const startBtn = document.getElementById('bdsStartWalkBtn');
      if (box) box.style.display = 'block';
      if (startBtn) startBtn.style.display = 'none';

      let walkSec = 3 * 60;
      const digits = document.getElementById('bdsWalkDigits');
      if (this.walkInterval) clearInterval(this.walkInterval);
      this.walkInterval = setInterval(() => {
        walkSec--;
        if (digits) digits.textContent = this.formatTime(walkSec);
        if (walkSec <= 0) {
          clearInterval(this.walkInterval);
          this.walkInterval = null;
          this.playChime();
          if (digits) digits.textContent = "Done! Welcome back";
        }
      }, 1000);
    }
  };

  /* =============================================================
     IN-APP ACCESSIBLE TOAST & CONFIRM DIALOG
     ============================================================= */
  const BdsToast = {
    ensureContainer() {
      let el = document.getElementById('bdsToastContainer');
      if (!el) {
        el = document.createElement('div');
        el.id = 'bdsToastContainer';
        el.setAttribute('role', 'status');
        el.setAttribute('aria-live', 'polite');
        document.body.appendChild(el);
      }
      return el;
    },

    show(message, type = 'info', duration = 4000) {
      const container = this.ensureContainer();
      while (container.children.length >= 3) {
        container.removeChild(container.firstChild);
      }

      const toast = document.createElement('div');
      toast.className = 'bds-toast';
      toast.innerHTML = `
        <span class="bds-toast-msg">${message}</span>
        <button class="bds-toast-close" aria-label="Dismiss notification" onclick="this.parentElement.remove()"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
      `;
      container.appendChild(toast);

      if (duration > 0) {
        setTimeout(() => {
          if (toast.parentElement) toast.remove();
        }, duration);
      }
    },

    confirm(title, message, onConfirm) {
      const existing = document.getElementById('bdsConfirmDialog');
      if (existing) existing.remove();

      const scrim = document.createElement('div');
      scrim.id = 'bdsConfirmDialog';
      scrim.className = 'bds-dialog-scrim';
      scrim.innerHTML = `
        <div class="bds-dialog-card" role="dialog" aria-modal="true" aria-labelledby="bdsDialogTitle">
          <h3 id="bdsDialogTitle" class="bds-dialog-title">${title}</h3>
          <p class="bds-dialog-msg">${message}</p>
          <div class="bds-dialog-actions">
            <button class="btn btn-secondary" id="bdsDialogCancel" style="min-height: 40px; padding: 0 16px; border-radius: 8px;">Cancel</button>
            <button class="btn btn-primary" id="bdsDialogConfirm" style="min-height: 40px; padding: 0 16px; border-radius: 8px;">Confirm</button>
          </div>
        </div>
      `;
      document.body.appendChild(scrim);

      const close = () => scrim.remove();
      scrim.querySelector('#bdsDialogCancel').onclick = close;
      scrim.querySelector('#bdsDialogConfirm').onclick = () => {
        close();
        if (typeof onConfirm === 'function') onConfirm();
      };
      scrim.onclick = (e) => {
        if (e.target === scrim) close();
      };
      const confirmBtn = scrim.querySelector('#bdsDialogConfirm');
      if (confirmBtn) confirmBtn.focus();
    }
  };

  /* =============================================================
     TOPIC TABS (Unified ARIA Tabs Component)
     ============================================================= */
  const TopicTabs = {
    init(tabBarEl, onTabSwitch) {
      if (!tabBarEl) return;
      tabBarEl.setAttribute('role', 'tablist');

      const tabs = Array.from(tabBarEl.querySelectorAll('.tab-btn'));
      tabs.forEach((tab, idx) => {
        tab.setAttribute('role', 'tab');
        const tabId = tab.getAttribute('data-tab') || tab.innerText.toLowerCase().replace(/[^a-z0-9]/g, '');
        tab.setAttribute('id', 'tab-' + tabId);
        tab.setAttribute('aria-controls', 'panel-' + tabId);

        const isActive = tab.classList.contains('active');
        tab.setAttribute('aria-selected', isActive ? 'true' : 'false');
        tab.setAttribute('tabindex', isActive ? '0' : '-1');

        tab.addEventListener('click', (e) => {
          e.preventDefault();
          this.selectTab(tabs, tab, onTabSwitch);
        });

        tab.addEventListener('keydown', (e) => {
          let targetTab = null;
          if (e.key === 'ArrowRight') {
            targetTab = tabs[(idx + 1) % tabs.length];
          } else if (e.key === 'ArrowLeft') {
            targetTab = tabs[(idx - 1 + tabs.length) % tabs.length];
          } else if (e.key === 'Home') {
            targetTab = tabs[0];
          } else if (e.key === 'End') {
            targetTab = tabs[tabs.length - 1];
          }
          if (targetTab) {
            e.preventDefault();
            targetTab.focus();
            this.selectTab(tabs, targetTab, onTabSwitch);
          }
        });
      });

      // Restore active tab from URL query (?tab=...)
      try {
        const hashQuery = window.location.hash.includes('?') ? window.location.hash.split('?')[1] : '';
        const urlParams = new URLSearchParams(window.location.search || hashQuery);
        const requestedTab = urlParams.get('tab');
        if (requestedTab) {
          const matchingTab = tabs.find(t => {
            const tid = t.getAttribute('data-tab') || '';
            return tid.toLowerCase() === requestedTab.toLowerCase() || t.innerText.toLowerCase().includes(requestedTab.toLowerCase());
          });
          if (matchingTab) {
            this.selectTab(tabs, matchingTab, onTabSwitch, false);
          }
        }
      } catch (e) {}
    },

    selectTab(allTabs, selectedTab, onTabSwitch, updateUrl = true) {
      allTabs.forEach(t => {
        const isCurrent = t === selectedTab;
        t.classList.toggle('active', isCurrent);
        t.setAttribute('aria-selected', isCurrent ? 'true' : 'false');
        t.setAttribute('tabindex', isCurrent ? '0' : '-1');
      });

      const tabId = selectedTab.getAttribute('data-tab') || selectedTab.innerText.toLowerCase().replace(/[^a-z0-9]/g, '');

      // Reflect in URL without full refresh
      if (updateUrl && history.replaceState) {
        try {
          const url = new URL(window.location.href);
          if (url.hash.includes('?')) {
            const hashParts = url.hash.split('?');
            const hParams = new URLSearchParams(hashParts[1]);
            hParams.set('tab', tabId);
            url.hash = hashParts[0] + '?' + hParams.toString();
          } else {
            url.hash = url.hash + '?tab=' + tabId;
          }
          history.replaceState(null, '', url.toString());
        } catch (e) {}
      }

      // Scroll active tab into view
      selectedTab.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });

      // Reset panel scroll position
      const panel = document.getElementById('tabContentContainer') || document.querySelector('.topic-view-container');
      if (panel) panel.scrollTop = 0;

      if (typeof onTabSwitch === 'function') {
        onTabSwitch(tabId, selectedTab);
      }
    }
  };

  /* =============================================================
     RUBRIC SIMULATOR PERSISTENCE ENGINE
     ============================================================= */
  const BdsSimulator = {
    getStorageKey(portalKey) {
      return `bds.${portalKey || 'surgery'}.evaluations`;
    },

    getHistory(portalKey, topicId) {
      try {
        const raw = localStorage.getItem(this.getStorageKey(portalKey));
        const all = raw ? JSON.parse(raw) : {};
        return all[topicId] || [];
      } catch (e) {
        return [];
      }
    },

    saveEvaluation(portalKey, topicId, evaluationData) {
      try {
        const key = this.getStorageKey(portalKey);
        const raw = localStorage.getItem(key);
        const all = raw ? JSON.parse(raw) : {};
        if (!all[topicId]) all[topicId] = [];

        const entry = {
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
          dateStr: new Date().toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }),
          total: evaluationData.total,
          outOf: evaluationData.outOf || 15,
          gradeLabel: evaluationData.gradeLabel || '',
          scores: evaluationData.scores || {}
        };

        all[topicId].unshift(entry);
        if (all[topicId].length > 10) all[topicId] = all[topicId].slice(0, 10);

        localStorage.setItem(key, JSON.stringify(all));

        BdsToast.show(`Evaluation saved! Score: ${entry.total} / ${entry.outOf} (${entry.gradeLabel})`, 'success');
        this.updateSaveUI(portalKey, topicId, entry);
        return entry;
      } catch (e) {
        BdsToast.show("Couldn't save: browser storage is unavailable", "error");
        return null;
      }
    },

    deleteEvaluation(portalKey, topicId, entryId) {
      try {
        const key = this.getStorageKey(portalKey);
        const raw = localStorage.getItem(key);
        if (!raw) return;
        const all = JSON.parse(raw);
        if (all[topicId]) {
          all[topicId] = all[topicId].filter(e => e.id !== entryId);
          localStorage.setItem(key, JSON.stringify(all));
          this.renderHistoryList(portalKey, topicId);
          BdsToast.show('Evaluation deleted', 'info');
        }
      } catch (e) {}
    },

    clearAll(portalKey, topicId) {
      BdsToast.confirm('Clear Evaluation History', 'Are you sure you want to delete all past evaluations for this topic?', () => {
        try {
          const key = this.getStorageKey(portalKey);
          const raw = localStorage.getItem(key);
          if (!raw) return;
          const all = JSON.parse(raw);
          delete all[topicId];
          localStorage.setItem(key, JSON.stringify(all));
          this.renderHistoryList(portalKey, topicId);
          BdsToast.show('History cleared', 'info');
        } catch (e) {}
      });
    },

    updateSaveUI(portalKey, topicId, latestEntry) {
      const saveBtn = document.getElementById('btnSaveEvaluation') || document.querySelector('.btn-save-evaluation');
      if (saveBtn) {
        const origText = saveBtn.getAttribute('data-orig-text') || saveBtn.textContent;
        saveBtn.setAttribute('data-orig-text', origText);
        saveBtn.textContent = 'Saved';
        saveBtn.classList.add('saved');
        setTimeout(() => {
          saveBtn.textContent = origText;
          saveBtn.classList.remove('saved');
        }, 2000);
      }

      const statusEl = document.getElementById('simSaveStatus');
      if (statusEl) {
        statusEl.textContent = `Last saved: ${latestEntry.dateStr} · ${latestEntry.total} / ${latestEntry.outOf}`;
      }

      this.renderHistoryList(portalKey, topicId);
    },

    renderHistoryList(portalKey, topicId) {
      const container = document.getElementById('simHistoryList');
      if (!container) return;
      const history = this.getHistory(portalKey, topicId);
      if (!history.length) {
        container.innerHTML = '<div style="font-size:0.75rem; color:var(--text-muted); padding:8px 0;">No saved attempts yet.</div>';
        return;
      }
      container.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
          <span style="font-size:0.75rem; font-weight:700; color:var(--text-muted); text-transform:uppercase;">Past Attempts (${history.length}/10)</span>
          <button style="background:none; border:none; color:var(--accent-crimson, #ef4444); font-size:0.72rem; cursor:pointer;" onclick="window.BdsSimulator.clearAll('${portalKey}', '${topicId}')">Clear all</button>
        </div>
        <div style="display:flex; flex-direction:column; gap:6px;">
          ${history.map(item => `
            <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 10px; background:var(--bg-surface-2); border:1px solid var(--border-color); border-radius:6px; font-size:0.78rem;">
              <div>
                <span style="font-weight:700; color:var(--text-primary);">${item.total} / ${item.outOf}</span>
                <span style="color:var(--text-muted); margin-left:6px;">${item.dateStr}</span>
                ${item.gradeLabel ? `<span style="font-size:0.7rem; color:var(--accent-primary); margin-left:6px;">${item.gradeLabel}</span>` : ''}
              </div>
              <div style="display:flex; gap:6px;">
                <button style="background:none; border:1px solid var(--border-color); color:var(--text-secondary); border-radius:4px; padding:2px 8px; font-size:0.72rem; cursor:pointer;" onclick="window.BdsSimulator.loadEvaluation('${portalKey}', '${topicId}', '${item.id}')">Load</button>
                <button style="background:none; border:none; color:var(--text-muted); cursor:pointer; padding:2px; display:inline-flex; align-items:center;" title="Delete" onclick="window.BdsSimulator.deleteEvaluation('${portalKey}', '${topicId}', '${item.id}')"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
              </div>
            </div>
          `).join('')}
        </div>
      `;
    },

    loadEvaluation(portalKey, topicId, entryId) {
      const history = this.getHistory(portalKey, topicId);
      const entry = history.find(e => e.id === entryId);
      if (!entry) return;

      if (typeof window.applyLoadedEvaluationScores === 'function') {
        window.applyLoadedEvaluationScores(entry.scores);
        BdsToast.show(`Loaded attempt from ${entry.dateStr} (${entry.total}/${entry.outOf})`, 'info');
      }
    }
  };

  CoreEngine.showToast = (msg, type, dur) => BdsToast.show(msg, type, dur);
  CoreEngine.confirm = (title, msg, fn) => BdsToast.confirm(title, msg, fn);
  CoreEngine.TopicTabs = TopicTabs;
  CoreEngine.Simulator = BdsSimulator;

  window.CoreEngine = CoreEngine;
  window.BdsTimer = BdsTimer;
  window.BdsToast = BdsToast;
  window.BdsSimulator = BdsSimulator;
  window.TopicTabs = TopicTabs;
  window.openFeedbackModal = () => CoreEngine.openFeedbackModal();
  window.closeFeedbackModal = () => CoreEngine.closeFeedbackModal();
  window.showToast = (msg, type, dur) => BdsToast.show(msg, type, dur);
  window.alert = (msg) => BdsToast.show(String(msg), 'info', 4000);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => BdsTimer.init());
  } else {
    BdsTimer.init();
  }
})(window);
