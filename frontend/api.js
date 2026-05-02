/* GamePilot frontend → backend wiring.
   Talks to the FastAPI server in gamepilot/app/api/server.py:
     GET  /health          — liveness
     GET  /state           — blackboard snapshot
     GET  /safety          — emergency_stop flag
     POST /command {text}  — natural-language command
     POST /stop            — emergency stop on
     POST /resume          — emergency stop off
     POST /demo/predict    — sample state → goal/policy/action

   Exposed as window.GamePilotAPI; call .bind(root) once after DOM is ready. */

(function () {
  const API_BASE = (window.GAMEPILOT_API_BASE || '').replace(/\/$/, '');
  const url = (p) => `${API_BASE}${p}`;

  async function jget(path) {
    const r = await fetch(url(path), { headers: { Accept: 'application/json' } });
    if (!r.ok) throw new Error(`${path} → ${r.status}`);
    return r.json();
  }

  async function jpost(path, body) {
    const r = await fetch(url(path), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: body == null ? null : JSON.stringify(body),
    });
    if (!r.ok) throw new Error(`${path} → ${r.status}`);
    return r.json();
  }

  const api = {
    health: () => jget('/health'),
    state: () => jget('/state'),
    safety: () => jget('/safety'),
    command: (text) => jpost('/command', { text }),
    stop: () => jpost('/stop'),
    resume: () => jpost('/resume'),
    predict: (sample) => jpost('/demo/predict', sample || {}),
    news: (limit = 10, refresh = false) =>
      jget(`/news?limit=${encodeURIComponent(limit)}${refresh ? '&refresh=true' : ''}`),
  };

  function setText(el, text) {
    if (el && el.textContent !== text) el.textContent = text;
  }

  // Update the live "Vision online · Xms" pill(s) and any [data-gp-status] hooks.
  function reflectStatus(root, { online, latencyMs, emergencyStop, goal }) {
    root.querySelectorAll('.pill.live').forEach((pill) => {
      const dot = pill.querySelector('.dot');
      if (emergencyStop) {
        pill.style.color = 'var(--gp-danger)';
        pill.style.borderColor = 'var(--gp-danger)';
        if (dot) dot.style.background = 'var(--gp-danger)';
        const tail = pill.childNodes[pill.childNodes.length - 1];
        if (tail && tail.nodeType === 3) tail.textContent = ' Emergency stop · armed';
      } else {
        pill.style.color = '';
        pill.style.borderColor = '';
        if (dot) dot.style.background = '';
        const tail = pill.childNodes[pill.childNodes.length - 1];
        if (tail && tail.nodeType === 3) {
          tail.textContent = online
            ? ` Vision online · ${latencyMs ?? '—'}ms`
            : ' Vision offline';
        }
      }
    });
    root.querySelectorAll('[data-gp-goal]').forEach((el) => setText(el, goal || '—'));
    root.querySelectorAll('[data-gp-emergency]').forEach((el) =>
      setText(el, emergencyStop ? 'ARMED' : 'standby')
    );
  }

  async function refresh(root) {
    const t0 = performance.now();
    try {
      const [h, s] = await Promise.all([api.health(), api.state().catch(() => ({}))]);
      const latency = Math.round(performance.now() - t0);
      reflectStatus(root, {
        online: h && h.status === 'ok',
        latencyMs: latency,
        emergencyStop: !!s.emergency_stop,
        goal: s.current_goal,
      });
    } catch (_e) {
      reflectStatus(root, { online: false, latencyMs: null, emergencyStop: false });
    }
  }

  // Append a system message into a coach chat body, if present.
  function logSystem(root, text) {
    const body = root.querySelector('.chat-body');
    if (!body) return;
    const wrap = document.createElement('div');
    wrap.className = 'msg system';
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = `// ${text}`;
    wrap.appendChild(bubble);
    body.appendChild(wrap);
    body.scrollTop = body.scrollHeight;
  }

  function logUser(root, text) {
    const body = root.querySelector('.chat-body');
    if (!body) return;
    const wrap = document.createElement('div');
    wrap.className = 'msg user';
    const meta = document.createElement('div');
    meta.className = 'meta';
    meta.textContent = `You · ${new Date().toLocaleTimeString()}`;
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;
    wrap.append(meta, bubble);
    body.appendChild(wrap);
    body.scrollTop = body.scrollHeight;
  }

  async function sendCommand(root, text) {
    if (!text || !text.trim()) return;
    logUser(root, text);
    try {
      const res = await api.command(text);
      logSystem(
        root,
        `goal=${res.goal ?? '—'} · stop=${res.emergency_stop ? 'on' : 'off'}`
      );
    } catch (e) {
      logSystem(root, `command failed · ${e.message}`);
    }
    refresh(root);
  }

  function bindChat(root) {
    const input = root.querySelector('.chat-input input');
    const send = root.querySelector('.chat-input button');
    if (!input || !send) return;
    const fire = () => {
      const v = input.value;
      input.value = '';
      sendCommand(root, v);
    };
    send.addEventListener('click', fire);
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') fire();
    });
    root.querySelectorAll('.quick').forEach((q) => {
      q.addEventListener('click', () => {
        const text = (q.textContent || '').replace(/^\s*\/\/\s*/, '').trim();
        sendCommand(root, text);
      });
    });
  }

  function navTo(root, screen) {
    const nav = root.querySelector(`.nav-item[data-screen="${screen}"]`);
    if (nav) nav.click();
  }

  function commandForButtonText(text) {
    const t = (text || '').toLowerCase();

    if (t.includes('engage autopilot') || t.includes('start autopilot')) return 'beat boss';
    if (t.includes('download') && t.includes('validate')) return 'download model';
    if (t.includes('install model')) return 'install model';
    if (t.includes('start training')) return 'train model';
    if (t.includes('accept') && t.includes('register')) return 'register model';

    return null;
  }

  function bindEngage(root) {
    root.querySelectorAll('.btn-engage').forEach((btn) => {
      if (btn.dataset.gpBoundEngage) return;
      btn.dataset.gpBoundEngage = '1';

      btn.addEventListener('click', async (e) => {
        const label = (btn.textContent || '').trim();

        if (label.toLowerCase().includes('create new')) {
          e.preventDefault();
          navTo(root, 'creator');
          logSystem(root, 'creator opened');
          return;
        }

        const commandText = commandForButtonText(label);

        if (!commandText) return;

        e.preventDefault();

        try {
          if (commandText === 'beat boss') await api.resume();

          await api.command(commandText);

          logSystem(root, `command sent · ${commandText.replace(/\s+/g, '_')}`);
        } catch (err) {
          logSystem(root, `action failed · ${err.message}`);
        }

        refresh(root);
      });
    });
  }

  function bindStop(root) {
    // Visible "End coach" / Cancel buttons → /stop
    root.querySelectorAll('.btn-primary, .btn-danger').forEach((btn) => {
      const t = (btn.textContent || '').toLowerCase();
      if (t.includes('end coach') || t.includes('stop') || t.includes('cancel')) {
        btn.addEventListener('click', async (e) => {
          e.preventDefault();
          await api.stop().catch(() => {});
          logSystem(root, 'EMERGENCY_STOP · user-triggered');
          refresh(root);
        });
      }
    });
    // Global hotkey: Ctrl + Shift + Esc → /stop
    window.addEventListener('keydown', async (e) => {
      if (e.ctrlKey && e.shiftKey && (e.key === 'Escape' || e.code === 'Escape')) {
        e.preventDefault();
        await api.stop().catch(() => {});
        logSystem(root, 'EMERGENCY_STOP · hotkey');
        refresh(root);
      }
    });
  }

  // ---------- News tab (Discover) ----------------------------------------
  // Renders the payload from GET /news into the markup defined in app.html.
  // Hooks: [data-news-sync] [data-news-banner] [data-count=KEY]
  //        [data-news-heroes] [data-news-rows] [data-news-trending]
  //        [data-news-refresh] [data-filter=KEY]

  function fmtNumber(n) {
    if (n == null || isNaN(n)) return '—';
    return Number(n).toLocaleString('en-US');
  }

  function fmtAge(seconds) {
    if (seconds == null || isNaN(seconds)) return '—';
    if (seconds < 60) return `${seconds}s ago`;
    const m = Math.floor(seconds / 60);
    if (m < 60) return `${m}m ago`;
    const h = Math.floor(m / 60);
    return `${h}h ago`;
  }

  const TIER_LABEL = {
    supported: 'Supported',
    beta: 'Beta',
    trainable: 'Trainable',
    locked: 'Locked',
  };

  const TIER_CTA = {
    supported: { label: 'Install Pilot', mini: 'Install', cls: 'btn-engage', icon: 'zap' },
    beta: { label: 'Try Beta', mini: 'Try Beta', cls: 'btn-primary', icon: 'flask-conical' },
    trainable: { label: 'Train a Model', mini: 'Train', cls: 'btn-primary', icon: 'sparkles' },
    locked: { label: 'Locked', mini: 'Locked', cls: 'btn-ghost', icon: 'lock' },
  };

  function compatPill(tier) {
    const safe = TIER_LABEL[tier] ? tier : 'trainable';
    const label = TIER_LABEL[safe];
    return `<span class="compat-pill compat-${safe}"><span class="dot"></span>${label}</span>`;
  }

  function placeholderSparkline(seed) {
    // Cheap deterministic sparkline so the UI looks alive even when Steam
    // doesn't ship a 24h history per app. Real history is a follow-up.
    const pts = [];
    let s = (seed || 1) % 97 || 1;
    for (let i = 0; i <= 10; i++) {
      s = (s * 9301 + 49297) % 233280;
      const y = 6 + (s % 18);
      pts.push(`${i * 20},${y}`);
    }
    const line = pts.join(' ');
    const fill = `${line} 200,28 0,28`;
    return `<svg class="spark" viewBox="0 0 200 28" preserveAspectRatio="none">
      <polyline points="${line}" fill="none" stroke="#0EA5E9" stroke-width="1.5"/>
      <polyline points="${fill}" fill="rgba(14,165,233,.12)" stroke="none"/>
    </svg>`;
  }

  function heroCardHTML(game, idx) {
    const tier = (game.compatibility && game.compatibility.tier) || 'trainable';
    const cta = TIER_CTA[tier] || TIER_CTA.trainable;
    const cover = game.header_image
      ? `<div class="cover" style="background-image:url('${game.header_image}')">`
      : `<div class="cover g${(idx % 3) + 1}">`;
    const genres = (game.genres || []).slice(0, 3)
      .map((g) => `<span class="gen-tag">${escapeHTML(g)}</span>`).join('');
    const rank = String(game.rank || idx + 1).padStart(2, '0');
    const players = fmtNumber(game.current_players);
    return `
      <div class="hero-card" data-tier="${tier}" data-appid="${game.appid}">
        ${cover}
          <div class="rank">#${rank}</div>
          ${compatPill(tier).replace('compat-pill', 'compat-pill top-pill')}
        </div>
        <div class="body">
          <h3>${escapeHTML(game.name || 'Unknown')}</h3>
          <div class="gen">${genres || '<span class="gen-tag">Steam</span>'}</div>
          <div class="stat"><span class="num">${players}</span><span class="lbl">// playing now</span></div>
          ${placeholderSparkline(game.appid)}
          <div class="ctas">
            <button class="btn ${cta.cls}" ${tier === 'locked' ? 'disabled style="opacity:.5;cursor:not-allowed;"' : ''} data-news-action="${tier}" data-appid="${game.appid}">
              <i data-lucide="${cta.icon}"></i>${cta.label}
            </button>
            <a class="btn btn-ghost" href="${game.store_url}" target="_blank" rel="noopener">
              <i data-lucide="external-link"></i>Steam
            </a>
          </div>
        </div>
      </div>`;
  }

  function rowHTML(game, idx) {
    const tier = (game.compatibility && game.compatibility.tier) || 'trainable';
    const cta = TIER_CTA[tier] || TIER_CTA.trainable;
    const thumbStyle = game.header_image
      ? `style="background-image:url('${game.header_image}')"`
      : '';
    const thumbCls = game.header_image ? 'game-thumb' : `game-thumb g${4 + ((idx) % 7)}`;
    const rk = String(game.rank || idx + 1).padStart(2, '0');
    const meta = escapeHTML(game.meta_line || '—');
    const players = fmtNumber(game.current_players);
    const peak = fmtNumber(game.peak_players_today);
    const genre = escapeHTML(game.primary_genre || '—');
    const action = tier === 'locked'
      ? `<button class="btn btn-ghost mini" disabled style="opacity:.5;cursor:not-allowed;">Locked</button>`
      : `<button class="btn ${cta.cls} mini" data-news-action="${tier}" data-appid="${game.appid}">${cta.mini}</button>`;
    let html = `
      <tr data-tier="${tier}" data-appid="${game.appid}">
        <td class="rk">${rk}</td>
        <td>
          <div class="game-cell">
            <div class="${thumbCls}" ${thumbStyle}></div>
            <div class="info">
              <div class="name">${escapeHTML(game.name || 'Unknown')}</div>
              <div class="meta">${meta}</div>
            </div>
          </div>
        </td>
        <td><span class="gen-tag">${genre}</span></td>
        <td><span class="players-cell">${players}</span></td>
        <td>${peak}</td>
        <td>${compatPill(tier)}</td>
        <td><div class="row-actions">${action}</div></td>
      </tr>`;
    if (tier === 'locked') {
      const reason = (game.compatibility && game.compatibility.reason)
        || 'automation blocked for this title';
      html += `<tr data-tier="locked-note" data-appid="${game.appid}">
        <td colspan="7" style="background: rgba(244,63,94,.04); border-bottom: none; padding: 0;">
          <div class="lock-reason">// #${rk} locked · ${escapeHTML(reason)}</div>
        </td>
      </tr>`;
    }
    return html;
  }

  function escapeHTML(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, (c) => (
      { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
    ));
  }

  function applyFilter(root, key) {
    root.querySelectorAll('[data-news-rows] tr[data-tier]').forEach((tr) => {
      const tier = tr.dataset.tier;
      const visible = key === 'all' || tier === key || tier === `${key}-note`;
      tr.style.display = visible ? '' : 'none';
    });
    root.querySelectorAll('[data-news-heroes] [data-tier]').forEach((card) => {
      const tier = card.dataset.tier;
      const visible = key === 'all' || tier === key;
      card.style.display = visible ? '' : 'none';
    });
    root.querySelectorAll('[data-news-filter] .news-chip').forEach((chip) => {
      chip.classList.toggle('active', chip.dataset.filter === key);
    });
  }

  function renderNews(root, payload) {
    if (!payload) return;
    const heroes = payload.games.slice(0, 3);
    const rest = payload.games.slice(3);

    const heroesEl = root.querySelector('[data-news-heroes]');
    if (heroesEl) {
      heroesEl.innerHTML = heroes.map(heroCardHTML).join('') || '';
    }

    const rowsEl = root.querySelector('[data-news-rows]');
    if (rowsEl) {
      if (rest.length === 0) {
        rowsEl.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 22px; color: var(--gp-fg-3); font-family: var(--gp-font-mono); font-size: 11px;">// no further ranks returned</td></tr>`;
      } else {
        rowsEl.innerHTML = rest.map((g, i) => rowHTML(g, i + 3)).join('');
      }
    }

    // Filter counts
    (payload.filters || []).forEach((f) => {
      const el = root.querySelector(`[data-count="${f.key}"]`);
      if (el) el.textContent = f.count;
    });

    // Trending Up — top 3 by descending current_players among supported/beta
    const trendingEl = root.querySelector('[data-news-trending]');
    if (trendingEl) {
      const trending = [...payload.games]
        .filter((g) => ['supported', 'beta'].includes((g.compatibility || {}).tier))
        .sort((a, b) => (b.current_players || 0) - (a.current_players || 0))
        .slice(0, 3);
      if (trending.length === 0) {
        trendingEl.innerHTML = `<div class="trend-row" style="opacity:.6;"><span class="name">No supported titles in current ranks</span></div>`;
      } else {
        trendingEl.innerHTML = trending.map((g, i) => {
          const thumb = g.header_image
            ? `<div class="game-thumb" style="background-image:url('${g.header_image}')"></div>`
            : `<div class="game-thumb g${4 + (i % 7)}"></div>`;
          const players = fmtNumber(g.current_players);
          return `<div class="trend-row">${thumb}<span class="name">${escapeHTML(g.name || '—')}</span><span class="pct">${players}</span></div>`;
        }).join('');
      }
    }

    // Sync stamp + status banner
    const sync = root.querySelector('[data-news-sync]');
    if (sync) {
      const ageSec = payload.age_seconds != null
        ? payload.age_seconds
        : Math.max(0, Math.floor(Date.now() / 1000 - (payload.fetched_at || 0)));
      sync.textContent = `// last sync · ${fmtAge(ageSec)} · index v${payload.compat_index_version || '0'}`;
    }
    const banner = root.querySelector('[data-news-banner]');
    if (banner) {
      if (payload.status === 'stale') {
        banner.hidden = false;
        banner.textContent = `// Steam charts unreachable · showing cached data from ${fmtAge(payload.age_seconds)}`;
      } else if (payload.status === 'error') {
        banner.hidden = false;
        banner.textContent = `// Steam charts unreachable · ${payload.error || 'no cached data'}`;
      } else {
        banner.hidden = true;
        banner.textContent = '';
      }
    }

    if (window.lucide && typeof window.lucide.createIcons === 'function') {
      window.lucide.createIcons();
    }

    bindNewsActions(root);
  }

  function bindNewsActions(root) {
    root.querySelectorAll('[data-news-action]').forEach((btn) => {
      if (btn.dataset.bound) return;
      btn.dataset.bound = '1';
      btn.addEventListener('click', () => {
        const tier = btn.dataset.newsAction;
        const appid = btn.dataset.appid;
        if (tier === 'locked' || !appid) return;
        const verb = tier === 'trainable' ? 'train' : tier === 'beta' ? 'try beta' : 'install';
        sendCommand(root, `${verb} appid ${appid}`);
      });
    });
  }

  async function loadNews(root, { force = false } = {}) {
    try {
      const payload = await api.news(10, force);
      renderNews(root, payload);
    } catch (e) {
      const banner = root.querySelector('[data-news-banner]');
      if (banner) {
        banner.hidden = false;
        banner.textContent = `// Steam charts unreachable · ${e.message}`;
      }
    }
  }

  function bindNews(root) {
    const screen = root.querySelector('[data-screen="news"]');
    if (!screen) return;

    root.querySelectorAll('[data-news-filter] .news-chip').forEach((chip) => {
      chip.addEventListener('click', () => applyFilter(root, chip.dataset.filter));
    });

    const refreshBtn = root.querySelector('[data-news-refresh]');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => loadNews(root, { force: true }));
    }

    let loaded = false;
    const trigger = () => {
      if (loaded || !screen.classList.contains('active')) return;
      loaded = true;
      loadNews(root);
    };

    // Load when the user navigates into the News screen.
    root.querySelectorAll('.nav-item[data-screen="news"]').forEach((nav) => {
      nav.addEventListener('click', () => setTimeout(trigger, 0));
    });

    // Or immediately if it's already the active screen on load (e.g. #news).
    trigger();

    // Honor the deep-link hash from the sidebar entry.
    if (window.location.hash === '#news') {
      const navEl = root.querySelector('.nav-item[data-screen="news"]');
      if (navEl) navEl.click();
    }
  }

  function bind(root) {
    bindChat(root);
    bindEngage(root);
    bindStop(root);
    bindNews(root);
    refresh(root);
    setInterval(() => refresh(root), 3000);
  }

  window.GamePilotAPI = Object.assign(api, { bind, loadNews });
})();
