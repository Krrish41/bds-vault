/**
 * BDS Clinical Vault — Canonical Core Engine
 * Standardized router, audio engine, focus timer, command palette & storage
 */

(function (window) {
  'use strict';

  const CoreEngine = {
    portalKey: 'vault',
    topics: [],
    currentTopicIndex: 0,
    audioElement: null,
    audioSpeed: 1.0,
    timerInterval: null,
    timerSeconds: 1500,

    init(options) {
      this.portalKey = options.portalKey || 'vault';
      this.topics = options.topics || [];
      this.initTheme();
      this.initRouter();
      this.initAudio();
      this.initTimer();
      this.initCommandPalette();
      this.initProgressSync();
    },

    /* -------------------------------------------------------------
       THEME MANAGEMENT (Dark Obsidian Default)
    ------------------------------------------------------------- */
    initTheme() {
      const savedTheme = localStorage.getItem('bds.theme') || 'dark';
      this.setTheme(savedTheme);

      const toggleBtn = document.querySelector('[data-testid="theme-toggle"]');
      if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
          const current = document.body.classList.contains('light') ? 'light' : 'dark';
          const next = current === 'dark' ? 'light' : 'dark';
          this.setTheme(next);
        });
      }
    },

    setTheme(theme) {
      if (theme === 'light') {
        document.body.classList.remove('dark');
        document.body.classList.add('light');
        document.documentElement.setAttribute('data-theme', 'light');
      } else {
        document.body.classList.remove('light');
        document.body.classList.add('dark');
        document.documentElement.setAttribute('data-theme', 'dark');
      }
      localStorage.setItem('bds.theme', theme);
    },

    /* -------------------------------------------------------------
       UNIFIED HASH ROUTER
    ------------------------------------------------------------- */
    initRouter() {
      window.addEventListener('hashchange', () => this.handleRoute());
      // Handle initial route on cold load
      window.addEventListener('DOMContentLoaded', () => this.handleRoute());
      if (document.readyState === 'complete' || document.readyState === 'interactive') {
        this.handleRoute();
      }
    },

    handleRoute() {
      const hash = window.location.hash || '';
      if (!hash || hash === '#' || hash === '#/') {
        this.showDashboard();
        return;
      }

      if (hash.startsWith('#/topic/')) {
        const slug = hash.replace('#/topic/', '').trim();
        this.openTopicBySlug(slug);
        return;
      }

      if (hash === '#/spotters') {
        if (typeof window.openDiagramSpotterFromDashboard === 'function') {
          window.openDiagramSpotterFromDashboard();
        }
        return;
      }

      if (hash === '#/simulator') {
        if (typeof window.launchExamSimFromDashboard === 'function') {
          window.launchExamSimFromDashboard();
        }
        return;
      }

      if (hash === '#/flashcards') {
        if (typeof window.launchFlashcardSession === 'function') {
          window.launchFlashcardSession();
        }
        return;
      }

      if (hash === '#/cheatsheet') {
        // Open the cheat sheet chapter
        const csIdx = this.topics.findIndex(t => (t.type === 'cheat-sheet' || (t.title && t.title.toLowerCase().includes('cheat sheet'))));
        if (csIdx !== -1) {
          this.selectChapter(csIdx);
        }
      }
    },

    showDashboard() {
      const dashView = document.getElementById('dashboardView');
      const topicView = document.getElementById('topicView');
      if (dashView && topicView) {
        dashView.style.display = 'block';
        topicView.style.display = 'none';
        window.scrollTo({ top: 0, behavior: 'instant' });
      }
      document.querySelectorAll('.topic-item').forEach(el => el.classList.remove('active'));
    },

    openTopicBySlug(slug) {
      const cleanSlug = slug.toLowerCase();
      let index = this.topics.findIndex(t => (t.id && t.id.toLowerCase() === cleanSlug));
      
      // Fallback search by title slug or number
      if (index === -1) {
        index = this.topics.findIndex(t => {
          const tSlug = (t.title || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
          return tSlug === cleanSlug || tSlug.includes(cleanSlug);
        });
      }

      if (index !== -1) {
        this.selectChapter(index);
      } else {
        console.warn('Topic slug not found:', slug);
        this.showTopicNotFound(slug);
      }
    },

    selectChapter(index) {
      this.currentTopicIndex = index;
      if (typeof window.selectChapter === 'function') {
        window.selectChapter(index);
      }

      const topic = this.topics[index];
      if (topic) {
        const slug = topic.id || (topic.title || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
        if (window.location.hash !== `#/topic/${slug}`) {
          history.pushState(null, '', `#/topic/${slug}`);
        }
        document.title = `${topic.title} — ${document.title.split('—')[0].trim()}`;
      }
    },

    showTopicNotFound(slug) {
      const topicView = document.getElementById('topicView');
      const dashView = document.getElementById('dashboardView');
      if (dashView && topicView) {
        dashView.style.display = 'none';
        topicView.style.display = 'block';
        topicView.innerHTML = `
          <div class="not-found-card p-8 text-center max-w-xl mx-auto my-12 bg-[#101322] border border-white/10 rounded-2xl">
            <h2 class="text-2xl font-bold text-white mb-2">Topic Not Found</h2>
            <p class="text-slate-400 text-sm mb-6">The requested topic slug "<code>${slug}</code>" could not be located in this curriculum.</p>
            <a href="#/" class="nav-pill-btn primary-accent inline-flex">Return to Dashboard</a>
          </div>
        `;
      }
    },

    /* -------------------------------------------------------------
       AUDIO WALKTHROUGH ENGINE
    ------------------------------------------------------------- */
    initAudio() {
      let dock = document.getElementById('audioWalkDock');
      if (!dock) {
        dock = document.createElement('div');
        dock.id = 'audioWalkDock';
        dock.className = 'audio-dock-overlay';
        dock.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span style="width: 8px; height: 8px; border-radius: 50%; background: var(--accent-primary);"></span>
              <strong style="font-size: 0.85rem; color: #ffffff;">Audio Walkthrough</strong>
            </div>
            <button onclick="CoreEngine.toggleAudioDock()" style="background: transparent; border: none; color: var(--text-muted); cursor: pointer; font-size: 1.1rem;">✕</button>
          </div>
          <div id="audioTrackTitle" style="font-size: 0.82rem; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
            Ready to Play
          </div>
          <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
            <button id="btnAudioPlayPause" onclick="CoreEngine.toggleAudioPlay()" class="nav-pill-btn primary-accent" style="padding: 6px 14px; font-size: 0.8rem;">
              ▶ Play
            </button>
            <div style="display: flex; gap: 4px;">
              <button class="audio-speed-btn active" onclick="CoreEngine.setAudioSpeed(1.0, this)">1x</button>
              <button class="audio-speed-btn" onclick="CoreEngine.setAudioSpeed(1.25, this)">1.25x</button>
              <button class="audio-speed-btn" onclick="CoreEngine.setAudioSpeed(1.5, this)">1.5x</button>
              <button class="audio-speed-btn" onclick="CoreEngine.setAudioSpeed(2.0, this)">2x</button>
            </div>
          </div>
        `;
        document.body.appendChild(dock);
      }

      const audioBtn = document.querySelector('[data-testid="audio-walkthrough"]');
      if (audioBtn) {
        audioBtn.addEventListener('click', () => this.toggleAudioDock());
      }
    },

    toggleAudioDock() {
      const dock = document.getElementById('audioWalkDock');
      if (dock) dock.classList.toggle('active');
    },

    toggleAudioPlay() {
      const btn = document.getElementById('btnAudioPlayPause');
      if (!this.audioElement) {
        this.audioElement = new Audio();
      }

      if (this.audioElement.paused) {
        // Find track for current topic if available
        const currentTopic = this.topics[this.currentTopicIndex];
        const trackTitle = document.getElementById('audioTrackTitle');
        if (currentTopic && trackTitle) {
          trackTitle.innerText = currentTopic.title || 'Curriculum Overview';
        }
        this.audioElement.playbackRate = this.audioSpeed;
        btn.innerHTML = '⏸ Pause';
      } else {
        this.audioElement.pause();
        btn.innerHTML = '▶ Play';
      }
    },

    setAudioSpeed(speed, btn) {
      this.audioSpeed = speed;
      if (this.audioElement) {
        this.audioElement.playbackRate = speed;
      }
      document.querySelectorAll('.audio-speed-btn').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
    },

    /* -------------------------------------------------------------
       FOCUS TIMER (25m / 50m)
    ------------------------------------------------------------- */
    initTimer() {
      const timerBtn = document.querySelector('[data-testid="focus-timer"]');
      if (timerBtn) {
        timerBtn.addEventListener('click', () => {
          this.toggleTimerPrompt();
        });
      }
    },

    toggleTimerPrompt() {
      if (this.timerInterval) {
        clearInterval(this.timerInterval);
        this.timerInterval = null;
        const timerBtn = document.querySelector('[data-testid="focus-timer"]');
        if (timerBtn) timerBtn.classList.remove('running');
        alert('Focus timer paused.');
      } else {
        this.timerSeconds = 25 * 60;
        this.startTimer();
      }
    },

    startTimer() {
      const timerBtn = document.querySelector('[data-testid="focus-timer"]');
      if (timerBtn) timerBtn.classList.add('running');
      this.timerInterval = setInterval(() => {
        this.timerSeconds--;
        if (this.timerSeconds <= 0) {
          clearInterval(this.timerInterval);
          this.timerInterval = null;
          alert('Focus block complete! Great progress.');
        }
      }, 1000);
    },

    /* -------------------------------------------------------------
       COMMAND PALETTE (Ctrl+K)
    ------------------------------------------------------------- */
    initCommandPalette() {
      window.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
          e.preventDefault();
          this.togglePalette();
        }
        if (e.key === 'Escape') {
          this.closePalette();
        }
      });

      const paletteTrigger = document.querySelector('[data-testid="palette"]');
      if (paletteTrigger) {
        paletteTrigger.addEventListener('click', () => this.togglePalette());
      }
    },

    togglePalette() {
      let modal = document.getElementById('cmdkModal');
      if (!modal) {
        modal = document.createElement('div');
        modal.id = 'cmdkModal';
        modal.className = 'cmdk-backdrop active';
        modal.innerHTML = `
          <div class="cmdk-box">
            <input type="text" id="cmdkInput" class="cmdk-search-input" placeholder="Search essays, spotters, cheat sheets (Ctrl+K)..." autofocus />
            <div id="cmdkResults" style="max-height: 360px; overflow-y: auto; padding: 8px;"></div>
          </div>
        `;
        document.body.appendChild(modal);
        modal.addEventListener('click', (e) => {
          if (e.target === modal) this.closePalette();
        });

        const input = document.getElementById('cmdkInput');
        input.addEventListener('input', (e) => this.renderPaletteResults(e.target.value));
      } else {
        modal.classList.toggle('active');
      }

      if (modal.classList.contains('active')) {
        const input = document.getElementById('cmdkInput');
        if (input) {
          input.value = '';
          input.focus();
          this.renderPaletteResults('');
        }
      }
    },

    closePalette() {
      const modal = document.getElementById('cmdkModal');
      if (modal) modal.classList.remove('active');
    },

    renderPaletteResults(query) {
      const container = document.getElementById('cmdkResults');
      if (!container) return;

      const q = (query || '').toLowerCase().trim();
      const matches = this.topics.filter(t => !q || (t.title && t.title.toLowerCase().includes(q))).slice(0, 8);

      if (matches.length === 0) {
        container.innerHTML = '<div style="padding: 16px; color: var(--text-muted); font-size: 0.85rem; text-align: center;">No matching topics found.</div>';
        return;
      }

      container.innerHTML = matches.map((t, i) => `
        <div onclick="CoreEngine.selectChapter(${this.topics.indexOf(t)}); CoreEngine.closePalette();"
             style="padding: 10px 14px; border-radius: 8px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); font-size: 0.86rem; color: var(--text-primary);"
             onmouseover="this.style.background='rgba(255,255,255,0.06)'"
             onmouseout="this.style.background='transparent'">
          <div>
            <strong>${t.title}</strong>
            <div style="font-size: 0.72rem; color: var(--text-muted);">${t.section || 'Exam Monograph'}</div>
          </div>
          <span style="font-size: 0.75rem; color: var(--accent-primary);">Open →</span>
        </div>
      `).join('');
    },

    /* -------------------------------------------------------------
       NAMESPACED PROGRESS STORAGE
    ------------------------------------------------------------- */
    initProgressSync() {
      // Listen to cross-tab storage changes
      window.addEventListener('storage', (e) => {
        if (e.key && e.key.startsWith('bds.')) {
          this.updateProgressDisplays();
        }
      });
    },

    markTopicComplete(topicIndex) {
      const key = `bds.${this.portalKey}.progress`;
      let completed = [];
      try {
        completed = JSON.parse(localStorage.getItem(key)) || [];
      } catch (e) {
        completed = [];
      }

      if (!completed.includes(topicIndex)) {
        completed.push(topicIndex);
        localStorage.setItem(key, JSON.stringify(completed));
      }
      this.updateProgressDisplays();
    },

    updateProgressDisplays() {
      const key = `bds.${this.portalKey}.progress`;
      let completed = [];
      try {
        completed = JSON.parse(localStorage.getItem(key)) || [];
      } catch (e) {
        completed = [];
      }

      const countEl = document.getElementById('completedCountDisplay');
      if (countEl) countEl.innerText = completed.length;

      const pctEl = document.getElementById('completedPercentDisplay');
      if (pctEl && this.topics.length > 0) {
        const pct = Math.round((completed.length / this.topics.length) * 100);
        pctEl.innerText = `${pct}%`;
      }
    }
  };

  window.CoreEngine = CoreEngine;
})(window);
