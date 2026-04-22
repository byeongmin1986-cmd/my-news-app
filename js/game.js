// ─── Golf Game Engine ───────────────────────────────────────────────────────

// roundRect polyfill for older browsers
if (!CanvasRenderingContext2D.prototype.roundRect) {
  CanvasRenderingContext2D.prototype.roundRect = function (x, y, w, h, r) {
    r = Math.min(r, w / 2, h / 2);
    this.moveTo(x + r, y);
    this.arcTo(x + w, y,     x + w, y + h, r);
    this.arcTo(x + w, y + h, x,     y + h, r);
    this.arcTo(x,     y + h, x,     y,     r);
    this.arcTo(x,     y,     x + w, y,     r);
    this.closePath();
    return this;
  };
}

const Game = (() => {
  // ── Canvas & Context
  let canvas, ctx, W, H;

  // ── Physics constants
  const FRICTION_GREEN  = 0.985;
  const FRICTION_ROUGH  = 0.94;
  const FRICTION_BUNKER = 0.82;
  const BALL_RADIUS     = 9;
  const HOLE_RADIUS     = 14;
  const MAX_POWER       = 18;
  const SLOPE_FORCE     = 0.04;

  // ── Game state
  let state = {};
  let animId = null;
  let onStageClear = null;
  let onGameOver   = null;

  // ── Touch/drag state
  let drag = { active: false, startX: 0, startY: 0, curX: 0, curY: 0 };

  // ── Stage definitions
  const STAGES = [
    // Stage 1 – flat short
    {
      par: 3,
      ball: { x: 0.5, y: 0.75 },
      hole: { x: 0.5, y: 0.25 },
      zones: [
        { type: 'green', x: 0, y: 0, w: 1, h: 1 }
      ],
      slopes: [{ x: 0.5, y: 0.5, ax: 0, ay: 0 }],
      obstacles: []
    },
    // Stage 2 – gentle slope right
    {
      par: 3,
      ball: { x: 0.5, y: 0.78 },
      hole: { x: 0.5, y: 0.22 },
      zones: [
        { type: 'green', x: 0, y: 0, w: 1, h: 1 }
      ],
      slopes: [{ x: 0.5, y: 0.5, ax: 0.018, ay: 0 }],
      obstacles: []
    },
    // Stage 3 – bunker center
    {
      par: 3,
      ball: { x: 0.5, y: 0.8 },
      hole: { x: 0.5, y: 0.18 },
      zones: [
        { type: 'green',  x: 0,    y: 0,    w: 1,   h: 1 },
        { type: 'bunker', x: 0.35, y: 0.42, w: 0.3, h: 0.2 }
      ],
      slopes: [{ x: 0.5, y: 0.5, ax: 0, ay: 0 }],
      obstacles: []
    },
    // Stage 4 – slope + bunker
    {
      par: 4,
      ball: { x: 0.15, y: 0.8 },
      hole: { x: 0.82, y: 0.2 },
      zones: [
        { type: 'green',  x: 0,    y: 0,    w: 1,   h: 1 },
        { type: 'bunker', x: 0.4,  y: 0.38, w: 0.25, h: 0.22 }
      ],
      slopes: [{ x: 0.5, y: 0.5, ax: 0.022, ay: 0.01 }],
      obstacles: []
    },
    // Stage 5 – water hazard
    {
      par: 4,
      ball: { x: 0.5, y: 0.85 },
      hole: { x: 0.5, y: 0.15 },
      zones: [
        { type: 'green', x: 0,    y: 0,    w: 1,   h: 1 },
        { type: 'water', x: 0.25, y: 0.42, w: 0.5, h: 0.18 }
      ],
      slopes: [{ x: 0.5, y: 0.5, ax: 0, ay: 0 }],
      obstacles: []
    },
    // Stage 6 – double slope
    {
      par: 4,
      ball: { x: 0.12, y: 0.85 },
      hole: { x: 0.88, y: 0.15 },
      zones: [
        { type: 'green', x: 0, y: 0,   w: 1, h: 0.5 },
        { type: 'green', x: 0, y: 0.5, w: 1, h: 0.5 }
      ],
      slopes: [
        { x: 0.25, y: 0.25, ax: 0.02,  ay: 0.015 },
        { x: 0.75, y: 0.75, ax: -0.02, ay: -0.015 }
      ],
      obstacles: []
    },
    // Stage 7 – water + bunker
    {
      par: 4,
      ball: { x: 0.5, y: 0.88 },
      hole: { x: 0.5, y: 0.12 },
      zones: [
        { type: 'green',  x: 0,    y: 0,    w: 1,   h: 1 },
        { type: 'water',  x: 0.15, y: 0.44, w: 0.3, h: 0.15 },
        { type: 'bunker', x: 0.55, y: 0.44, w: 0.3, h: 0.15 }
      ],
      slopes: [{ x: 0.5, y: 0.5, ax: 0, ay: 0 }],
      obstacles: []
    },
    // Stage 8 – winding slope
    {
      par: 5,
      ball: { x: 0.1, y: 0.88 },
      hole: { x: 0.9, y: 0.12 },
      zones: [
        { type: 'green', x: 0, y: 0, w: 1, h: 1 },
        { type: 'water', x: 0.3, y: 0.55, w: 0.4, h: 0.12 }
      ],
      slopes: [
        { x: 0.2, y: 0.7, ax: 0.025,  ay: -0.005 },
        { x: 0.8, y: 0.3, ax: -0.005, ay: -0.025 }
      ],
      obstacles: []
    },
    // Stage 9 – tight corridor
    {
      par: 5,
      ball: { x: 0.5, y: 0.9 },
      hole: { x: 0.5, y: 0.1 },
      zones: [
        { type: 'green',  x: 0,    y: 0,    w: 1,   h: 1 },
        { type: 'bunker', x: 0.1,  y: 0.35, w: 0.3, h: 0.32 },
        { type: 'bunker', x: 0.6,  y: 0.35, w: 0.3, h: 0.32 }
      ],
      slopes: [{ x: 0.5, y: 0.5, ax: 0, ay: 0.012 }],
      obstacles: []
    },
    // Stage 10 – final boss
    {
      par: 5,
      ball: { x: 0.5, y: 0.92 },
      hole: { x: 0.5, y: 0.08 },
      zones: [
        { type: 'green',  x: 0,    y: 0,    w: 1,   h: 1 },
        { type: 'water',  x: 0.15, y: 0.42, w: 0.28, h: 0.18 },
        { type: 'water',  x: 0.57, y: 0.42, w: 0.28, h: 0.18 },
        { type: 'bunker', x: 0.38, y: 0.28, w: 0.24, h: 0.14 }
      ],
      slopes: [
        { x: 0.3, y: 0.6, ax: 0.02,  ay: -0.01 },
        { x: 0.7, y: 0.4, ax: -0.02, ay: -0.01 }
      ],
      obstacles: []
    }
  ];

  // ── Colour helpers for terrain
  const ZONE_COLORS = {
    green:  '#2d8a4e',
    rough:  '#4a7a2a',
    bunker: '#d4b483',
    water:  '#1565c0'
  };
  const ZONE_BORDER = {
    green:  '#1a5c32',
    rough:  '#2d5c14',
    bunker: '#b8975a',
    water:  '#0d47a1'
  };

  // ── Slope field cell size
  const SLOPE_GRID = 60;

  // ──────────────────────────────────────────────────────────────────────────
  // Init
  // ──────────────────────────────────────────────────────────────────────────
  function init(canvasEl, callbacks) {
    canvas = canvasEl;
    ctx    = canvas.getContext('2d');
    onStageClear = callbacks.onStageClear;
    onGameOver   = callbacks.onGameOver;

    resize();
    window.addEventListener('resize', resize);

    canvas.addEventListener('touchstart', onTouchStart, { passive: false });
    canvas.addEventListener('touchmove',  onTouchMove,  { passive: false });
    canvas.addEventListener('touchend',   onTouchEnd,   { passive: false });
    // Mouse fallback for desktop testing
    canvas.addEventListener('mousedown', onMouseDown);
    canvas.addEventListener('mousemove', onMouseMove);
    canvas.addEventListener('mouseup',   onMouseUp);
  }

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  // ──────────────────────────────────────────────────────────────────────────
  // Start / Reset
  // ──────────────────────────────────────────────────────────────────────────
  function start(stageIndex, score, lives) {
    const def = STAGES[Math.min(stageIndex, STAGES.length - 1)];
    drag = { active: false, startX: 0, startY: 0, curX: 0, curY: 0 };

    state = {
      stageIndex,
      stageDef: def,
      par:      def.par,
      strokes:  0,
      score,
      lives,
      ball: { x: def.ball.x * W, y: def.ball.y * H, vx: 0, vy: 0, moving: false },
      hole: { x: def.hole.x * W, y: def.hole.y * H },
      phase:    'ready',    // ready | aiming | rolling | water_penalty | cleared
      waterPenalty: false,
      flagAnim: 0
    };

    if (animId) cancelAnimationFrame(animId);
    loop();
  }

  function stop() {
    if (animId) cancelAnimationFrame(animId);
    animId = null;
  }

  // ──────────────────────────────────────────────────────────────────────────
  // Touch / Mouse handlers
  // ──────────────────────────────────────────────────────────────────────────
  function beginDrag(x, y) {
    if (state.phase !== 'ready') return;
    drag.active = true;
    drag.startX = x;
    drag.startY = y;
    drag.curX   = x;
    drag.curY   = y;
    state.phase = 'aiming';
    document.getElementById('controls-hint').classList.add('hidden');
    document.getElementById('power-bar-container').classList.add('visible');
  }
  function moveDrag(x, y) {
    if (!drag.active) return;
    drag.curX = x;
    drag.curY = y;
    updatePowerBar();
  }
  function endDrag() {
    if (!drag.active) return;
    drag.active = false;
    shoot();
  }

  function onTouchStart(e) { e.preventDefault(); const t = e.touches[0]; beginDrag(t.clientX, t.clientY); }
  function onTouchMove(e)  { e.preventDefault(); const t = e.touches[0]; moveDrag(t.clientX, t.clientY); }
  function onTouchEnd(e)   { e.preventDefault(); endDrag(); }
  function onMouseDown(e)  { beginDrag(e.clientX, e.clientY); }
  function onMouseMove(e)  { moveDrag(e.clientX, e.clientY); }
  function onMouseUp()     { endDrag(); }

  function shoot() {
    if (state.phase !== 'aiming') return;
    const dx   = drag.startX - drag.curX;
    const dy   = drag.startY - drag.curY;
    const dist = Math.sqrt(dx * dx + dy * dy);
    const maxDrag = Math.min(W, H) * 0.35;
    const power = Math.min(dist / maxDrag, 1);

    if (power < 0.03) { state.phase = 'ready'; document.getElementById('power-bar-container').classList.remove('visible'); return; }

    const speed = power * MAX_POWER;
    state.ball.vx = (dx / dist) * speed;
    state.ball.vy = (dy / dist) * speed;
    state.ball.moving = true;
    state.strokes++;
    state.phase = 'rolling';
    document.getElementById('power-bar-container').classList.remove('visible');
    document.getElementById('hud-strokes').textContent = state.strokes;
  }

  function updatePowerBar() {
    const dx   = drag.startX - drag.curX;
    const dy   = drag.startY - drag.curY;
    const dist = Math.sqrt(dx * dx + dy * dy);
    const maxDrag = Math.min(W, H) * 0.35;
    const pct = Math.min(dist / maxDrag * 100, 100);
    const fill = document.getElementById('power-bar-fill');
    const label = document.getElementById('power-label');
    if (fill) fill.style.width = pct + '%';
    if (label) label.textContent = Math.round(pct) + '%';
  }

  // ──────────────────────────────────────────────────────────────────────────
  // Zone helpers
  // ──────────────────────────────────────────────────────────────────────────
  function getZoneAt(bx, by) {
    const def = state.stageDef;
    let hit = 'green';
    for (const z of def.zones) {
      const rx = z.x * W, ry = z.y * H, rw = z.w * W, rh = z.h * H;
      if (bx >= rx && bx <= rx + rw && by >= ry && by <= ry + rh) {
        if (z.type !== 'green') hit = z.type;
      }
    }
    return hit;
  }

  function getSlopeAt(bx, by) {
    const def = state.stageDef;
    let ax = 0, ay = 0;
    for (const s of def.slopes) {
      ax += s.ax;
      ay += s.ay;
    }
    return { ax, ay };
  }

  // ──────────────────────────────────────────────────────────────────────────
  // Physics update
  // ──────────────────────────────────────────────────────────────────────────
  function updatePhysics() {
    if (state.phase !== 'rolling') return;

    const ball = state.ball;
    const zone = getZoneAt(ball.x, ball.y);

    // Friction
    let friction = FRICTION_GREEN;
    if (zone === 'rough')  friction = FRICTION_ROUGH;
    if (zone === 'bunker') friction = FRICTION_BUNKER;

    // Slope acceleration
    const slope = getSlopeAt(ball.x, ball.y);
    ball.vx += slope.ax;
    ball.vy += slope.ay;

    ball.vx *= friction;
    ball.vy *= friction;

    ball.x += ball.vx;
    ball.y += ball.vy;

    // Water hazard
    if (zone === 'water') {
      waterPenalty();
      return;
    }

    // Wall bouncing (keep ball in canvas)
    if (ball.x < BALL_RADIUS) { ball.x = BALL_RADIUS; ball.vx = Math.abs(ball.vx) * 0.5; }
    if (ball.x > W - BALL_RADIUS) { ball.x = W - BALL_RADIUS; ball.vx = -Math.abs(ball.vx) * 0.5; }
    if (ball.y < BALL_RADIUS) { ball.y = BALL_RADIUS; ball.vy = Math.abs(ball.vy) * 0.5; }
    if (ball.y > H - BALL_RADIUS) { ball.y = H - BALL_RADIUS; ball.vy = -Math.abs(ball.vy) * 0.5; }

    // Hole-in check
    const hx = state.hole.x, hy = state.hole.y;
    const distToHole = Math.sqrt((ball.x - hx) ** 2 + (ball.y - hy) ** 2);
    const speed = Math.sqrt(ball.vx ** 2 + ball.vy ** 2);
    if (distToHole < HOLE_RADIUS && speed < 6) {
      ballInHole();
      return;
    }

    // Ball stopped
    if (speed < 0.08) {
      ball.vx = 0;
      ball.vy = 0;
      ball.moving = false;

      // Check stroke limit
      if (state.strokes >= state.par + 3) {
        loseLife();
      } else {
        state.phase = 'ready';
      }
    }
  }

  function waterPenalty() {
    // Reset ball to start, add 1 stroke penalty
    const def = state.stageDef;
    state.ball.x  = def.ball.x * W;
    state.ball.y  = def.ball.y * H;
    state.ball.vx = 0;
    state.ball.vy = 0;
    state.ball.moving = false;
    state.strokes++;
    document.getElementById('hud-strokes').textContent = state.strokes;
    state.phase = 'ready';
    showToast('💧 워터 해저드! +1타');

    if (state.strokes >= state.par + 3) {
      setTimeout(loseLife, 500);
    }
  }

  function loseLife() {
    state.lives--;
    updateLivesHUD();
    if (state.lives <= 0) {
      state.phase = 'cleared';
      stop();
      onGameOver({ stage: state.stageIndex + 1, score: state.score });
    } else {
      showToast('❤️ 목숨 -1! 다시 시도');
      // restart same stage stroke count
      const def = state.stageDef;
      state.ball.x  = def.ball.x * W;
      state.ball.y  = def.ball.y * H;
      state.ball.vx = 0;
      state.ball.vy = 0;
      state.strokes = 0;
      state.phase   = 'ready';
      document.getElementById('hud-strokes').textContent = 0;
    }
  }

  function ballInHole() {
    state.phase = 'cleared';
    state.ball.vx = 0;
    state.ball.vy = 0;

    // Scoring
    const diff   = state.strokes - state.par;
    let label    = 'パー';
    let points   = 100;
    if (state.strokes === 1)       { label = 'Hole in One! 🎯'; points = 1000; }
    else if (diff <= -3)           { label = 'Albatross 🦅🦅🦅'; points = 700; }
    else if (diff === -2)          { label = 'Eagle 🦅🦅';        points = 500; }
    else if (diff === -1)          { label = 'Birdie 🐦';          points = 300; }
    else if (diff === 0)           { label = 'Par ⛳';             points = 100; }
    else if (diff === 1)           { label = 'Bogey';               points = 50; }
    else if (diff === 2)           { label = 'Double Bogey';        points = 20; }
    else                           { label = 'Triple+ Bogey';       points = 5; }

    // Distance bonus
    const dx = state.hole.x - state.stageDef.ball.x * W;
    const dy = state.hole.y - state.stageDef.ball.y * H;
    const distPx = Math.sqrt(dx * dx + dy * dy);
    const distBonus = Math.round(distPx / 10);
    points += distBonus;

    state.score += points;
    document.getElementById('hud-score').textContent = state.score;

    stop();
    onStageClear({
      strokes: state.strokes,
      par:     state.par,
      result:  label,
      points,
      score:   state.score,
      lives:   state.lives,
      stage:   state.stageIndex
    });
  }

  function updateLivesHUD() {
    const icons = document.querySelectorAll('.life-icon');
    icons.forEach((el, i) => {
      el.classList.toggle('lost', i >= state.lives);
    });
  }

  // ──────────────────────────────────────────────────────────────────────────
  // Render
  // ──────────────────────────────────────────────────────────────────────────
  function render() {
    ctx.clearRect(0, 0, W, H);
    drawCourse();
    drawSlopeArrows();
    drawHole();
    drawBall();
    if (state.phase === 'aiming' && drag.active) drawAimLine();
  }

  function drawCourse() {
    const def = state.stageDef;
    // Background rough
    ctx.fillStyle = '#3a5c22';
    ctx.fillRect(0, 0, W, H);

    // Zones
    for (const z of def.zones) {
      const rx = z.x * W, ry = z.y * H, rw = z.w * W, rh = z.h * H;
      ctx.fillStyle = ZONE_COLORS[z.type] || '#2d8a4e';
      ctx.beginPath();
      ctx.roundRect(rx, ry, rw, rh, 6);
      ctx.fill();

      // Border
      ctx.beginPath();
      ctx.roundRect(rx, ry, rw, rh, 6);
      ctx.strokeStyle = ZONE_BORDER[z.type] || '#1a5c32';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Water ripple
      if (z.type === 'water') {
        drawWaterRipple(rx, ry, rw, rh);
      }
      // Bunker texture
      if (z.type === 'bunker') {
        drawBunkerDots(rx, ry, rw, rh);
      }
    }
  }

  function drawWaterRipple(rx, ry, rw, rh) {
    ctx.save();
    ctx.globalAlpha = 0.25 + 0.1 * Math.sin(Date.now() / 400);
    ctx.strokeStyle = '#90caf9';
    ctx.lineWidth = 1.5;
    const cx = rx + rw / 2, cy = ry + rh / 2;
    for (let r = 10; r < Math.min(rw, rh) / 2; r += 14) {
      ctx.beginPath();
      ctx.ellipse(cx, cy, r, r * 0.4, 0, 0, Math.PI * 2);
      ctx.stroke();
    }
    ctx.globalAlpha = 1;
    ctx.restore();
  }

  function drawBunkerDots(rx, ry, rw, rh) {
    ctx.save();
    ctx.globalAlpha = 0.3;
    ctx.fillStyle = '#a08040';
    for (let i = 0; i < 18; i++) {
      const bx = rx + (((i * 137.5) % rw));
      const by = ry + (((i * 97.3) % rh));
      ctx.beginPath();
      ctx.arc(bx, by, 2, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
    ctx.restore();
  }

  function drawSlopeArrows() {
    const def = state.stageDef;
    const totalAx = def.slopes.reduce((s, sl) => s + sl.ax, 0);
    const totalAy = def.slopes.reduce((s, sl) => s + sl.ay, 0);
    const mag = Math.sqrt(totalAx ** 2 + totalAy ** 2);
    if (mag < 0.001) return;

    ctx.save();
    ctx.globalAlpha = 0.22;
    const step = SLOPE_GRID;
    for (let gx = step / 2; gx < W; gx += step) {
      for (let gy = step / 2; gy < H; gy += step) {
        const len = 18 * Math.min(mag / 0.02, 1.5);
        const nx  = totalAx / mag;
        const ny  = totalAy / mag;
        const ex  = gx + nx * len;
        const ey  = gy + ny * len;

        // Arrow colour by slope strength
        const t = Math.min(mag / 0.04, 1);
        const r = Math.round(lerp(100, 255, t));
        const g = Math.round(lerp(200, 80,  t));
        const b = Math.round(lerp(100, 60,  t));
        ctx.strokeStyle = `rgb(${r},${g},${b})`;
        ctx.fillStyle   = `rgb(${r},${g},${b})`;
        ctx.lineWidth   = 1.5;

        ctx.beginPath();
        ctx.moveTo(gx, gy);
        ctx.lineTo(ex, ey);
        ctx.stroke();
        drawArrowHead(ctx, gx, gy, ex, ey, 5);
      }
    }
    ctx.globalAlpha = 1;
    ctx.restore();
  }

  function drawArrowHead(c, sx, sy, ex, ey, size) {
    const angle = Math.atan2(ey - sy, ex - sx);
    c.save();
    c.translate(ex, ey);
    c.rotate(angle);
    c.beginPath();
    c.moveTo(0, 0);
    c.lineTo(-size, -size / 2);
    c.lineTo(-size, size / 2);
    c.closePath();
    c.fill();
    c.restore();
  }

  function drawHole() {
    const hx = state.hole.x, hy = state.hole.y;
    state.flagAnim = (state.flagAnim + 0.05) % (Math.PI * 2);

    // Hole shadow
    ctx.save();
    ctx.globalAlpha = 0.4;
    ctx.fillStyle = '#000';
    ctx.beginPath();
    ctx.ellipse(hx, hy + 4, HOLE_RADIUS, HOLE_RADIUS * 0.4, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1;
    ctx.restore();

    // Hole cup
    ctx.fillStyle = '#111';
    ctx.beginPath();
    ctx.arc(hx, hy, HOLE_RADIUS, 0, Math.PI * 2);
    ctx.fill();

    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Flag pole
    ctx.strokeStyle = '#ccc';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(hx, hy);
    ctx.lineTo(hx, hy - 36);
    ctx.stroke();

    // Waving flag
    ctx.fillStyle = '#e53935';
    ctx.beginPath();
    const fw = 18, fh = 10;
    const wave = Math.sin(state.flagAnim) * 2;
    ctx.moveTo(hx, hy - 36);
    ctx.quadraticCurveTo(hx + fw / 2, hy - 36 + wave - fh / 2, hx + fw, hy - 36 + wave);
    ctx.quadraticCurveTo(hx + fw / 2, hy - 36 + wave + fh / 2, hx, hy - 26);
    ctx.closePath();
    ctx.fill();
  }

  function drawBall() {
    const bx = state.ball.x, by = state.ball.y;

    // Shadow
    ctx.save();
    ctx.globalAlpha = 0.35;
    ctx.fillStyle = '#000';
    ctx.beginPath();
    ctx.ellipse(bx + 2, by + 4, BALL_RADIUS * 0.8, BALL_RADIUS * 0.4, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1;
    ctx.restore();

    // Ball gradient
    const grad = ctx.createRadialGradient(bx - 3, by - 3, 1, bx, by, BALL_RADIUS);
    grad.addColorStop(0, '#ffffff');
    grad.addColorStop(0.6, '#e8e8e8');
    grad.addColorStop(1, '#bbbbbb');
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(bx, by, BALL_RADIUS, 0, Math.PI * 2);
    ctx.fill();

    // Dimple hint
    ctx.strokeStyle = 'rgba(150,150,150,0.4)';
    ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.arc(bx, by, BALL_RADIUS * 0.55, 0, Math.PI * 2);
    ctx.stroke();
  }

  function drawAimLine() {
    const bx = state.ball.x, by = state.ball.y;
    const dx  = drag.startX - drag.curX;
    const dy  = drag.startY - drag.curY;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist < 5) return;

    const maxDrag = Math.min(W, H) * 0.35;
    const power   = Math.min(dist / maxDrag, 1);
    const nx = dx / dist, ny = dy / dist;
    const len = power * 120;

    // Dashed guide line
    ctx.save();
    ctx.strokeStyle = 'rgba(255,255,255,0.7)';
    ctx.lineWidth   = 2;
    ctx.setLineDash([6, 6]);
    ctx.beginPath();
    ctx.moveTo(bx, by);
    ctx.lineTo(bx + nx * len, by + ny * len);
    ctx.stroke();
    ctx.setLineDash([]);

    // Power indicator circle at drag point
    ctx.strokeStyle = `rgba(245,197,24,${0.5 + power * 0.5})`;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(drag.curX, drag.curY, 14, 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();
  }

  // ──────────────────────────────────────────────────────────────────────────
  // Main Loop
  // ──────────────────────────────────────────────────────────────────────────
  function loop() {
    updatePhysics();
    render();
    animId = requestAnimationFrame(loop);
  }

  // ──────────────────────────────────────────────────────────────────────────
  // Helpers
  // ──────────────────────────────────────────────────────────────────────────
  function lerp(a, b, t) { return a + (b - a) * t; }
  function showToast(msg) {
    const t = document.querySelector('.toast') || (() => {
      const el = document.createElement('div');
      el.className = 'toast';
      document.body.appendChild(el);
      return el;
    })();
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(t._tid);
    t._tid = setTimeout(() => t.classList.remove('show'), 2200);
  }

  function getTotalStages() { return STAGES.length; }
  function getState()       { return state; }

  return { init, start, stop, getTotalStages, getState, showToast };
})();
