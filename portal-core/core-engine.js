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
       FOCUS TIMER (25m / 50m — Synchronized Cross-Tab Engine)
    ------------------------------------------------------------- */
    initTimer() {
      if (window.BdsTimer) {
        window.BdsTimer.init();
      }
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

  /* =============================================================
     BDS CLINICAL VAULT — UNIVERSAL SYNCHRONIZED FOCUS TIMER
     Persists across BDS Vault Hub, Surgery, Medicine & Pathology
     ============================================================= */
  const BdsTimer = {
    STORAGE_KEY: 'bds.focus.timer',
    localInterval: null,
    walkInterval: null,
    audioCtx: null,

    getState() {
      try {
        const raw = localStorage.getItem(this.STORAGE_KEY);
        if (raw) {
          return JSON.parse(raw);
        }
      } catch (e) {}
      return {
        status: 'idle', // 'running' | 'paused' | 'idle'
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
        if (e.key === this.STORAGE_KEY) {
          this.render();
        }
      });

      if (this.localInterval) clearInterval(this.localInterval);
      this.localInterval = setInterval(() => this.tick(), 500);

      // Wire up any focus-timer trigger button with data-testid="focus-timer"
      const timerBtn = document.querySelector('[data-testid="focus-timer"]');
      if (timerBtn && !timerBtn.hasAttribute('data-bds-bound')) {
        timerBtn.setAttribute('data-bds-bound', 'true');
        timerBtn.addEventListener('click', (e) => {
          // If on hub, popover is handled by index.html; if in portal, toggle directly
          if (typeof window.toggleTimerPopover !== 'function') {
            this.toggle();
          }
        });
      }
    },

    tick() {
      const state = this.getState();
      if (state.status === 'running') {
        const now = Date.now();
        const remaining = Math.max(0, Math.round((state.targetEndTime - now) / 1000));
        this.updateAllDisplays(remaining, true, false);

        if (remaining <= 0) {
          state.status = 'idle';
          state.remainingSeconds = (state.durationMinutes || 25) * 60;
          state.targetEndTime = null;
          this.saveState(state);
          this.triggerReward();
        }
      } else {
        this.updateAllDisplays(state.remainingSeconds, false, state.status === 'paused');
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
      if (state.status === 'running') {
        this.pause();
      } else {
        this.start();
      }
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

    updateAllDisplays(seconds, isRunning, isPaused) {
      const timeStr = this.formatTime(seconds);

      // Hub Displays
      const navTimerDisp = document.getElementById('navTimerDisplay');
      if (navTimerDisp) navTimerDisp.textContent = timeStr;
      
      const timerMainDigits = document.getElementById('timerMainDigits');
      if (timerMainDigits) timerMainDigits.textContent = timeStr;

      const navPill = document.getElementById('navTimerPill');
      if (navPill) {
        if (isRunning) navPill.classList.add('running');
        else navPill.classList.remove('running');
      }

      const navStateText = document.getElementById('navTimerStateText');
      if (navStateText) {
        navStateText.textContent = isRunning ? 'Active' : (isPaused ? 'Paused' : 'Focus');
      }

      const timerStartBtn = document.getElementById('timerStartBtn');
      if (timerStartBtn) {
        timerStartBtn.textContent = isRunning ? 'Pause Focus' : (isPaused ? 'Resume Focus' : 'Start Focus');
      }

      // Portal Displays (General Surgery, General Medicine, Oral Pathology)
      const portalDisp = document.getElementById('focusTimerDisplay');
      if (portalDisp) portalDisp.textContent = timeStr;

      const portalBtn = document.getElementById('btnFocusTimer');
      if (portalBtn) {
        if (isRunning) portalBtn.classList.add('running');
        else portalBtn.classList.remove('running');
      }
    },

    render() {
      const state = this.getState();
      if (state.status === 'running') {
        const remaining = Math.max(0, Math.round((state.targetEndTime - Date.now()) / 1000));
        this.updateAllDisplays(remaining, true, false);
      } else {
        this.updateAllDisplays(state.remainingSeconds, false, state.status === 'paused');
      }
    },

    playChime() {
      try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return;
        const ctx = new AudioContext();
        const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6 chord
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
      } catch (e) {
        console.warn('Audio chime unable to play:', e);
      }
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
          <div class="bds-reward-icon-badge">💧</div>
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
            letter-spacing: -0.01em;
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

  window.CoreEngine = CoreEngine;
  window.BdsTimer = BdsTimer;

  // Auto-initialize BdsTimer on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => BdsTimer.init());
  } else {
    BdsTimer.init();
  }
})(window);

