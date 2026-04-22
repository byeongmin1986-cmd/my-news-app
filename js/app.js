// ─── App Controller ──────────────────────────────────────────────────────────

(function () {
  'use strict';

  // ── State
  let currentUser  = null;
  let gameScore    = 0;
  let gameLives    = 3;
  let gameStage    = 0;
  let rankUnsub    = null;

  // ── Firebase refs (populated after SDK loads)
  let auth, db;
  let GoogleAuthProvider, signInWithPopup, signOut, onAuthStateChanged;
  let firestoreDoc, setDoc, getDoc, collection, query, orderBy, limit, onSnapshot, serverTimestamp;

  // ── DOM
  const $ = id => document.getElementById(id);

  // ─────────────────────────────────────────────────────────────────────────
  // Boot – wait for Firebase SDK then set up auth listener
  // ─────────────────────────────────────────────────────────────────────────
  function boot() {
    const fb = window.__firebase;
    if (!fb) { setTimeout(boot, 80); return; }

    auth                = fb.auth;
    db                  = fb.db;
    GoogleAuthProvider  = fb.GoogleAuthProvider;
    signInWithPopup     = fb.signInWithPopup;
    signOut             = fb.signOut;
    onAuthStateChanged  = fb.onAuthStateChanged;
    firestoreDoc        = fb.doc;
    setDoc              = fb.setDoc;
    getDoc              = fb.getDoc;
    collection          = fb.collection;
    query               = fb.query;
    orderBy             = fb.orderBy;
    limit               = fb.limit;
    onSnapshot          = fb.onSnapshot;
    serverTimestamp     = fb.serverTimestamp;

    onAuthStateChanged(auth, user => {
      currentUser = user;
      if (user) showScreen('game');
      else       showScreen('login');
    });

    bindEvents();
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Screen routing
  // ─────────────────────────────────────────────────────────────────────────
  function showScreen(name) {
    ['login', 'game', 'leaderboard'].forEach(id => {
      const el = $('screen-' + id);
      if (!el) return;
      el.classList.toggle('hidden', id !== name);
      el.classList.toggle('active', id === name);
    });

    if (name === 'game') {
      startNewGame();
    } else if (name === 'leaderboard') {
      loadLeaderboard();
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Game management
  // ─────────────────────────────────────────────────────────────────────────
  function startNewGame() {
    gameScore = 0;
    gameLives = 3;
    gameStage = 0;
    resetHUD();

    const canvas = $('game-canvas');
    // Only init once
    if (!canvas._gameInited) {
      Game.init(canvas, {
        onStageClear: handleStageClear,
        onGameOver:   handleGameOver
      });
      canvas._gameInited = true;
    }
    Game.start(gameStage, gameScore, gameLives);
    const initState = Game.getState();
    $('hud-par').textContent = initState.par;
    $('controls-hint').classList.remove('hidden');
  }

  function resetHUD() {
    $('hud-stage').textContent   = 1;
    $('hud-par').textContent     = 3;
    $('hud-strokes').textContent = 0;
    $('hud-score').textContent   = 0;
    const icons = document.querySelectorAll('.life-icon');
    icons.forEach(el => el.classList.remove('lost'));
  }

  function handleStageClear(data) {
    gameScore = data.score;
    gameLives = data.lives;

    $('clear-title').textContent   = data.result;
    $('clear-strokes').textContent = data.strokes;
    $('clear-par').textContent     = data.par;
    $('clear-result').textContent  = data.result;
    $('clear-points').textContent  = '+' + data.points;

    showOverlay('stage-clear');

    // Save best score to Firestore
    saveScore(gameScore, gameStage + 1);
  }

  function handleGameOver(data) {
    $('go-stage').textContent = data.stage;
    $('go-score').textContent = data.score;
    showOverlay('game-over');
    saveScore(data.score, data.stage);
  }

  function nextStage() {
    hideOverlays();
    gameStage++;
    const totalStages = Game.getTotalStages();
    if (gameStage >= totalStages) {
      // All stages cleared – loop with bonus
      gameStage = 0;
      gameScore += 500;
      Game.showToast('🏆 전 코스 클리어! +500점');
    }
    $('hud-stage').textContent   = gameStage + 1;
    $('hud-strokes').textContent = 0;
    Game.start(gameStage, gameScore, gameLives);
    // Update par for new stage
    const st = Game.getState();
    $('hud-par').textContent = st.par;
    $('controls-hint').classList.remove('hidden');
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Overlay helpers
  // ─────────────────────────────────────────────────────────────────────────
  function showOverlay(name) {
    hideOverlays();
    const el = $('overlay-' + name);
    if (el) el.classList.remove('hidden');
  }

  function hideOverlays() {
    ['stage-clear', 'game-over', 'menu'].forEach(n => {
      const el = $('overlay-' + n);
      if (el) el.classList.add('hidden');
    });
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Firestore – save & leaderboard
  // ─────────────────────────────────────────────────────────────────────────
  async function saveScore(score, stage) {
    if (!currentUser) return;
    try {
      const ref   = firestoreDoc(db, 'scores', currentUser.uid);
      const snap  = await getDoc(ref);
      const prev  = snap.exists() ? (snap.data().score || 0) : 0;
      const prevS = snap.exists() ? (snap.data().stage  || 0) : 0;

      if (score > prev || stage > prevS) {
        await setDoc(ref, {
          uid:       currentUser.uid,
          name:      currentUser.displayName || 'Guest',
          photoURL:  currentUser.photoURL    || '',
          score:     Math.max(score, prev),
          stage:     Math.max(stage, prevS),
          updatedAt: serverTimestamp()
        }, { merge: true });
      }
    } catch (e) {
      console.warn('saveScore error', e);
    }
  }

  function loadLeaderboard() {
    if (rankUnsub) { rankUnsub(); rankUnsub = null; }

    const listEl = $('leaderboard-list');
    listEl.innerHTML = '<div class="loading-spinner">불러오는 중...</div>';

    const q = query(collection(db, 'scores'), orderBy('score', 'desc'), limit(50));
    rankUnsub = onSnapshot(q, snap => {
      renderLeaderboard(snap.docs.map(d => d.data()));
    }, err => {
      listEl.innerHTML = '<div class="loading-spinner">로딩 실패. 새로고침 해주세요.</div>';
      console.warn('leaderboard error', err);
    });
  }

  function renderLeaderboard(rows) {
    const listEl = $('leaderboard-list');
    listEl.innerHTML = '';

    const medals = ['🥇', '🥈', '🥉'];
    let myRank = '-', myScore = 0;

    rows.forEach((row, i) => {
      const rank = i + 1;
      const isMe = currentUser && row.uid === currentUser.uid;
      if (isMe) { myRank = rank; myScore = row.score; }

      const item = document.createElement('div');
      item.className = 'rank-item' +
        (isMe ? ' mine' : '') +
        (rank <= 3 ? ' top' + rank : '');

      const numHtml = rank <= 3
        ? `<span class="rank-num medal">${medals[rank - 1]}</span>`
        : `<span class="rank-num">${rank}</span>`;

      const avatarHtml = row.photoURL
        ? `<div class="rank-avatar"><img src="${escapeHtml(row.photoURL)}" alt="" loading="lazy"/></div>`
        : `<div class="rank-avatar">👤</div>`;

      item.innerHTML = `
        ${numHtml}
        ${avatarHtml}
        <div class="rank-info">
          <div class="rank-name">${escapeHtml(row.name || 'Guest')}</div>
          <div class="rank-stage">스테이지 ${row.stage || 1}</div>
        </div>
        <div class="rank-score">${(row.score || 0).toLocaleString()}</div>
      `;
      listEl.appendChild(item);
    });

    if (rows.length === 0) {
      listEl.innerHTML = '<div class="loading-spinner">아직 기록이 없습니다.</div>';
    }

    $('my-rank-value').textContent = myRank;
    $('my-rank-score').textContent = myScore.toLocaleString() + '점';
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Event bindings
  // ─────────────────────────────────────────────────────────────────────────
  function bindEvents() {
    // Login
    $('btn-google-login').addEventListener('click', async () => {
      const errEl = $('login-error');
      errEl.classList.add('hidden');
      try {
        const provider = new GoogleAuthProvider();
        await signInWithPopup(auth, provider);
      } catch (e) {
        errEl.textContent = '로그인 실패: ' + (e.message || e.code);
        errEl.classList.remove('hidden');
      }
    });

    $('btn-guest-play').addEventListener('click', () => {
      currentUser = null;
      showScreen('game');
    });

    // Game – menu button
    $('btn-menu').addEventListener('click', () => {
      Game.stop();
      showOverlay('menu');
    });

    // Menu overlay
    $('btn-resume').addEventListener('click', () => {
      hideOverlays();
      const s = Game.getState();
      Game.start(s.stageIndex, s.score, s.lives);
    });
    $('btn-menu-rank').addEventListener('click', () => {
      hideOverlays();
      Game.stop();
      showScreen('leaderboard');
    });
    $('btn-menu-restart').addEventListener('click', () => {
      hideOverlays();
      startNewGame();
    });
    $('btn-logout').addEventListener('click', async () => {
      hideOverlays();
      if (currentUser) await signOut(auth);
      else showScreen('login');
    });

    // Stage clear overlay
    $('btn-next-stage').addEventListener('click', nextStage);

    // Game over overlay
    $('btn-restart').addEventListener('click', () => {
      hideOverlays();
      startNewGame();
    });
    $('btn-go-rank').addEventListener('click', () => {
      hideOverlays();
      showScreen('leaderboard');
    });

    // Leaderboard screen
    $('btn-back-game').addEventListener('click', () => {
      if (rankUnsub) { rankUnsub(); rankUnsub = null; }
      // Show game screen without resetting – resume current game
      ['login', 'game', 'leaderboard'].forEach(id => {
        const el = $('screen-' + id);
        if (!el) return;
        el.classList.toggle('hidden', id !== 'game');
        el.classList.toggle('active', id === 'game');
      });
      const s = Game.getState();
      if (s && s.phase !== 'cleared') {
        Game.start(s.stageIndex, s.score, s.lives);
      } else {
        startNewGame();
      }
    });
    $('btn-refresh-rank').addEventListener('click', loadLeaderboard);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Utility
  // ─────────────────────────────────────────────────────────────────────────
  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // ─── Boot
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
