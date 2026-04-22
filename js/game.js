// Golf Game Engine

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
  let canvas, ctx, W, H;
  const FRICTION_GREEN  = 0.985;
  const FRICTION_ROUGH  = 0.94;
  const FRICTION_BUNKER = 0.82;
  const BALL_RADIUS = 9;
  const HOLE_RADIUS = 14;
  const MAX_POWER   = 18;
  const SLOPE_GRID  = 60;

  let state = {};
  let animId = null;
  let onStageClear = null;
  let onGameOver   = null;
  let drag = { active: false, startX: 0, startY: 0, curX: 0, curY: 0 };

  const STAGES = [
    { par:3, ball:{x:0.5,y:0.75}, hole:{x:0.5,y:0.25},
      zones:[{type:'green',x:0,y:0,w:1,h:1}],
      slopes:[{ax:0,ay:0}], obstacles:[] },
    { par:3, ball:{x:0.5,y:0.78}, hole:{x:0.5,y:0.22},
      zones:[{type:'green',x:0,y:0,w:1,h:1}],
      slopes:[{ax:0.018,ay:0}], obstacles:[] },
    { par:3, ball:{x:0.5,y:0.8}, hole:{x:0.5,y:0.18},
      zones:[{type:'green',x:0,y:0,w:1,h:1},{type:'bunker',x:0.35,y:0.42,w:0.3,h:0.2}],
      slopes:[{ax:0,ay:0}], obstacles:[] },
    { par:4, ball:{x:0.15,y:0.8}, hole:{x:0.82,y:0.2},
      zones:[{type:'green',x:0,y:0,w:1,h:1},{type:'bunker',x:0.4,y:0.38,w:0.25,h:0.22}],
      slopes:[{ax:0.022,ay:0.01}], obstacles:[] },
    { par:4, ball:{x:0.5,y:0.85}, hole:{x:0.5,y:0.15},
      zones:[{type:'green',x:0,y:0,w:1,h:1},{type:'water',x:0.25,y:0.42,w:0.5,h:0.18}],
      slopes:[{ax:0,ay:0}], obstacles:[] },
    { par:4, ball:{x:0.12,y:0.85}, hole:{x:0.88,y:0.15},
      zones:[{type:'green',x:0,y:0,w:1,h:0.5},{type:'green',x:0,y:0.5,w:1,h:0.5}],
      slopes:[{ax:0.02,ay:0.015},{ax:-0.02,ay:-0.015}], obstacles:[] },
    { par:4, ball:{x:0.5,y:0.88}, hole:{x:0.5,y:0.12},
      zones:[{type:'green',x:0,y:0,w:1,h:1},{type:'water',x:0.15,y:0.44,w:0.3,h:0.15},{type:'bunker',x:0.55,y:0.44,w:0.3,h:0.15}],
      slopes:[{ax:0,ay:0}], obstacles:[] },
    { par:5, ball:{x:0.1,y:0.88}, hole:{x:0.9,y:0.12},
      zones:[{type:'green',x:0,y:0,w:1,h:1},{type:'water',x:0.3,y:0.55,w:0.4,h:0.12}],
      slopes:[{ax:0.025,ay:-0.005},{ax:-0.005,ay:-0.025}], obstacles:[] },
    { par:5, ball:{x:0.5,y:0.9}, hole:{x:0.5,y:0.1},
      zones:[{type:'green',x:0,y:0,w:1,h:1},{type:'bunker',x:0.1,y:0.35,w:0.3,h:0.32},{type:'bunker',x:0.6,y:0.35,w:0.3,h:0.32}],
      slopes:[{ax:0,ay:0.012}], obstacles:[] },
    { par:5, ball:{x:0.5,y:0.92}, hole:{x:0.5,y:0.08},
      zones:[{type:'green',x:0,y:0,w:1,h:1},{type:'water',x:0.15,y:0.42,w:0.28,h:0.18},{type:'water',x:0.57,y:0.42,w:0.28,h:0.18},{type:'bunker',x:0.38,y:0.28,w:0.24,h:0.14}],
      slopes:[{ax:0.02,ay:-0.01},{ax:-0.02,ay:-0.01}], obstacles:[] }
  ];

  const ZONE_COLORS = { green:'#2d8a4e', rough:'#4a7a2a', bunker:'#d4b483', water:'#1565c0' };
  const ZONE_BORDER = { green:'#1a5c32', rough:'#2d5c14', bunker:'#b8975a', water:'#0d47a1' };

  function init(canvasEl, callbacks) {
    canvas = canvasEl;
    ctx = canvas.getContext('2d');
    onStageClear = callbacks.onStageClear;
    onGameOver   = callbacks.onGameOver;
    resize();
    window.addEventListener('resize', resize);
    canvas.addEventListener('touchstart', onTouchStart, { passive: false });
    canvas.addEventListener('touchmove',  onTouchMove,  { passive: false });
    canvas.addEventListener('touchend',   onTouchEnd,   { passive: false });
    canvas.addEventListener('mousedown', onMouseDown);
    canvas.addEventListener('mousemove', onMouseMove);
    canvas.addEventListener('mouseup',   onMouseUp);
  }

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function start(stageIndex, score, lives) {
    const def = STAGES[Math.min(stageIndex, STAGES.length - 1)];
    drag = { active: false, startX: 0, startY: 0, curX: 0, curY: 0 };
    state = {
      stageIndex, stageDef: def, par: def.par, strokes: 0, score, lives,
      ball: { x: def.ball.x * W, y: def.ball.y * H, vx: 0, vy: 0, moving: false },
      hole: { x: def.hole.x * W, y: def.hole.y * H },
      phase: 'ready', flagAnim: 0
    };
    if (animId) cancelAnimationFrame(animId);
    loop();
  }

  function stop() { if (animId) cancelAnimationFrame(animId); animId = null; }

  function beginDrag(x, y) {
    if (state.phase !== 'ready') return;
    drag = { active: true, startX: x, startY: y, curX: x, curY: y };
    state.phase = 'aiming';
    document.getElementById('controls-hint').classList.add('hidden');
    document.getElementById('power-bar-container').classList.add('visible');
  }
  function moveDrag(x, y) { if (!drag.active) return; drag.curX = x; drag.curY = y; updatePowerBar(); }
  function endDrag() { if (!drag.active) return; drag.active = false; shoot(); }

  function onTouchStart(e) { e.preventDefault(); const t = e.touches[0]; beginDrag(t.clientX, t.clientY); }
  function onTouchMove(e)  { e.preventDefault(); const t = e.touches[0]; moveDrag(t.clientX, t.clientY); }
  function onTouchEnd(e)   { e.preventDefault(); endDrag(); }
  function onMouseDown(e)  { beginDrag(e.clientX, e.clientY); }
  function onMouseMove(e)  { moveDrag(e.clientX, e.clientY); }
  function onMouseUp()     { endDrag(); }

  function shoot() {
    if (state.phase !== 'aiming') return;
    const dx = drag.startX - drag.curX, dy = drag.startY - drag.curY;
    const dist = Math.sqrt(dx*dx + dy*dy);
    const maxDrag = Math.min(W, H) * 0.35;
    const power = Math.min(dist / maxDrag, 1);
    if (power < 0.03) {
      state.phase = 'ready';
      document.getElementById('power-bar-container').classList.remove('visible');
      return;
    }
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
    const dx = drag.startX - drag.curX, dy = drag.startY - drag.curY;
    const dist = Math.sqrt(dx*dx + dy*dy);
    const pct = Math.min(dist / (Math.min(W,H)*0.35) * 100, 100);
    const fill = document.getElementById('power-bar-fill');
    const label = document.getElementById('power-label');
    if (fill) fill.style.width = pct + '%';
    if (label) label.textContent = Math.round(pct) + '%';
  }

  function getZoneAt(bx, by) {
    const def = state.stageDef;
    let hit = 'green';
    for (const z of def.zones) {
      const rx = z.x*W, ry = z.y*H, rw = z.w*W, rh = z.h*H;
      if (bx >= rx && bx <= rx+rw && by >= ry && by <= ry+rh && z.type !== 'green') hit = z.type;
    }
    return hit;
  }

  function getSlopeAt() {
    const def = state.stageDef;
    let ax = 0, ay = 0;
    for (const s of def.slopes) { ax += s.ax; ay += s.ay; }
    return { ax, ay };
  }

  function updatePhysics() {
    if (state.phase !== 'rolling') return;
    const ball = state.ball;
    const zone = getZoneAt(ball.x, ball.y);
    let friction = FRICTION_GREEN;
    if (zone === 'rough')  friction = FRICTION_ROUGH;
    if (zone === 'bunker') friction = FRICTION_BUNKER;

    const slope = getSlopeAt();
    ball.vx += slope.ax;
    ball.vy += slope.ay;
    ball.vx *= friction;
    ball.vy *= friction;
    ball.x += ball.vx;
    ball.y += ball.vy;

    if (zone === 'water') { waterPenalty(); return; }

    if (ball.x < BALL_RADIUS)       { ball.x = BALL_RADIUS;       ball.vx =  Math.abs(ball.vx)*0.5; }
    if (ball.x > W - BALL_RADIUS)   { ball.x = W - BALL_RADIUS;   ball.vx = -Math.abs(ball.vx)*0.5; }
    if (ball.y < BALL_RADIUS)       { ball.y = BALL_RADIUS;       ball.vy =  Math.abs(ball.vy)*0.5; }
    if (ball.y > H - BALL_RADIUS)   { ball.y = H - BALL_RADIUS;   ball.vy = -Math.abs(ball.vy)*0.5; }

    const dist = Math.sqrt((ball.x-state.hole.x)**2 + (ball.y-state.hole.y)**2);
    const speed = Math.sqrt(ball.vx**2 + ball.vy**2);
    if (dist < HOLE_RADIUS && speed < 6) { ballInHole(); return; }

    if (speed < 0.08) {
      ball.vx = 0; ball.vy = 0; ball.moving = false;
      if (state.strokes >= state.par + 3) loseLife();
      else state.phase = 'ready';
    }
  }

  function waterPenalty() {
    const def = state.stageDef;
    state.ball.x = def.ball.x * W; state.ball.y = def.ball.y * H;
    state.ball.vx = 0; state.ball.vy = 0;
    state.strokes++;
    document.getElementById('hud-strokes').textContent = state.strokes;
    state.phase = 'ready';
    showToast('💧 워터 해저드! +1타');
    if (state.strokes >= state.par + 3) setTimeout(loseLife, 500);
  }

  function loseLife() {
    state.lives--;
    document.querySelectorAll('.life-icon').forEach((el,i) => el.classList.toggle('lost', i >= state.lives));
    if (state.lives <= 0) { state.phase='cleared'; stop(); onGameOver({stage:state.stageIndex+1, score:state.score}); }
    else {
      showToast('❤️ 목숨 -1! 다시 시도');
      const def = state.stageDef;
      state.ball.x = def.ball.x*W; state.ball.y = def.ball.y*H;
      state.ball.vx = 0; state.ball.vy = 0; state.strokes = 0; state.phase = 'ready';
      document.getElementById('hud-strokes').textContent = 0;
    }
  }

  function ballInHole() {
    state.phase = 'cleared'; state.ball.vx = 0; state.ball.vy = 0;
    const diff = state.strokes - state.par;
    let label = 'Par ⛳', points = 100;
    if (state.strokes === 1)  { label = 'Hole in One! 🎯'; points = 1000; }
    else if (diff <= -3)      { label = 'Albatross 🦅🦅🦅'; points = 700; }
    else if (diff === -2)     { label = 'Eagle 🦅🦅'; points = 500; }
    else if (diff === -1)     { label = 'Birdie 🐦'; points = 300; }
    else if (diff === 0)      { label = 'Par ⛳'; points = 100; }
    else if (diff === 1)      { label = 'Bogey'; points = 50; }
    else if (diff === 2)      { label = 'Double Bogey'; points = 20; }
    else                      { label = 'Triple+ Bogey'; points = 5; }

    const ddx = state.hole.x - state.stageDef.ball.x*W;
    const ddy = state.hole.y - state.stageDef.ball.y*H;
    points += Math.round(Math.sqrt(ddx*ddx+ddy*ddy)/10);
    state.score += points;
    document.getElementById('hud-score').textContent = state.score;
    stop();
    onStageClear({ strokes:state.strokes, par:state.par, result:label, points, score:state.score, lives:state.lives, stage:state.stageIndex });
  }

  function render() {
    ctx.clearRect(0, 0, W, H);
    drawCourse(); drawSlopeArrows(); drawHole(); drawBall();
    if (state.phase === 'aiming' && drag.active) drawAimLine();
  }

  function drawCourse() {
    const def = state.stageDef;
    ctx.fillStyle = '#3a5c22'; ctx.fillRect(0, 0, W, H);
    for (const z of def.zones) {
      const rx=z.x*W, ry=z.y*H, rw=z.w*W, rh=z.h*H;
      ctx.fillStyle = ZONE_COLORS[z.type] || '#2d8a4e';
      ctx.beginPath(); ctx.roundRect(rx,ry,rw,rh,6); ctx.fill();
      ctx.beginPath(); ctx.roundRect(rx,ry,rw,rh,6);
      ctx.strokeStyle = ZONE_BORDER[z.type] || '#1a5c32'; ctx.lineWidth = 2; ctx.stroke();
      if (z.type === 'water')  drawWaterRipple(rx, ry, rw, rh);
      if (z.type === 'bunker') drawBunkerDots(rx, ry, rw, rh);
    }
  }

  function drawWaterRipple(rx, ry, rw, rh) {
    ctx.save();
    ctx.globalAlpha = 0.25 + 0.1 * Math.sin(Date.now()/400);
    ctx.strokeStyle = '#90caf9'; ctx.lineWidth = 1.5;
    const cx = rx+rw/2, cy = ry+rh/2;
    for (let r = 10; r < Math.min(rw,rh)/2; r += 14) {
      ctx.beginPath(); ctx.ellipse(cx,cy,r,r*0.4,0,0,Math.PI*2); ctx.stroke();
    }
    ctx.restore();
  }

  function drawBunkerDots(rx, ry, rw, rh) {
    ctx.save(); ctx.globalAlpha = 0.3; ctx.fillStyle = '#a08040';
    for (let i = 0; i < 18; i++) {
      ctx.beginPath(); ctx.arc(rx+((i*137.5)%rw), ry+((i*97.3)%rh), 2, 0, Math.PI*2); ctx.fill();
    }
    ctx.restore();
  }

  function drawSlopeArrows() {
    const def = state.stageDef;
    const tax = def.slopes.reduce((s,sl)=>s+sl.ax,0);
    const tay = def.slopes.reduce((s,sl)=>s+sl.ay,0);
    const mag = Math.sqrt(tax**2+tay**2);
    if (mag < 0.001) return;
    ctx.save(); ctx.globalAlpha = 0.22;
    for (let gx=SLOPE_GRID/2; gx<W; gx+=SLOPE_GRID) {
      for (let gy=SLOPE_GRID/2; gy<H; gy+=SLOPE_GRID) {
        const len=18*Math.min(mag/0.02,1.5), nx=tax/mag, ny=tay/mag;
        const ex=gx+nx*len, ey=gy+ny*len;
        const t=Math.min(mag/0.04,1);
        const col=`rgb(${Math.round(lerp(100,255,t))},${Math.round(lerp(200,80,t))},${Math.round(lerp(100,60,t))})`;
        ctx.strokeStyle=col; ctx.fillStyle=col; ctx.lineWidth=1.5;
        ctx.beginPath(); ctx.moveTo(gx,gy); ctx.lineTo(ex,ey); ctx.stroke();
        const ang=Math.atan2(ey-gy,ex-gx);
        ctx.save(); ctx.translate(ex,ey); ctx.rotate(ang);
        ctx.beginPath(); ctx.moveTo(0,0); ctx.lineTo(-5,-2.5); ctx.lineTo(-5,2.5); ctx.closePath(); ctx.fill();
        ctx.restore();
      }
    }
    ctx.restore();
  }

  function drawHole() {
    const hx=state.hole.x, hy=state.hole.y;
    state.flagAnim = (state.flagAnim+0.05)%(Math.PI*2);
    ctx.save(); ctx.globalAlpha=0.4; ctx.fillStyle='#000';
    ctx.beginPath(); ctx.ellipse(hx,hy+4,HOLE_RADIUS,HOLE_RADIUS*0.4,0,0,Math.PI*2); ctx.fill(); ctx.restore();
    ctx.fillStyle='#111'; ctx.beginPath(); ctx.arc(hx,hy,HOLE_RADIUS,0,Math.PI*2); ctx.fill();
    ctx.strokeStyle='#333'; ctx.lineWidth=2; ctx.stroke();
    ctx.strokeStyle='#ccc'; ctx.lineWidth=2;
    ctx.beginPath(); ctx.moveTo(hx,hy); ctx.lineTo(hx,hy-36); ctx.stroke();
    const wave=Math.sin(state.flagAnim)*2;
    ctx.fillStyle='#e53935'; ctx.beginPath();
    ctx.moveTo(hx,hy-36);
    ctx.quadraticCurveTo(hx+9,hy-36+wave-5,hx+18,hy-36+wave);
    ctx.quadraticCurveTo(hx+9,hy-36+wave+5,hx,hy-26);
    ctx.closePath(); ctx.fill();
  }

  function drawBall() {
    const bx=state.ball.x, by=state.ball.y;
    ctx.save(); ctx.globalAlpha=0.35; ctx.fillStyle='#000';
    ctx.beginPath(); ctx.ellipse(bx+2,by+4,BALL_RADIUS*0.8,BALL_RADIUS*0.4,0,0,Math.PI*2); ctx.fill(); ctx.restore();
    const grad=ctx.createRadialGradient(bx-3,by-3,1,bx,by,BALL_RADIUS);
    grad.addColorStop(0,'#fff'); grad.addColorStop(0.6,'#e8e8e8'); grad.addColorStop(1,'#bbb');
    ctx.fillStyle=grad; ctx.beginPath(); ctx.arc(bx,by,BALL_RADIUS,0,Math.PI*2); ctx.fill();
    ctx.strokeStyle='rgba(150,150,150,0.4)'; ctx.lineWidth=0.8;
    ctx.beginPath(); ctx.arc(bx,by,BALL_RADIUS*0.55,0,Math.PI*2); ctx.stroke();
  }

  function drawAimLine() {
    const bx=state.ball.x, by=state.ball.y;
    const dx=drag.startX-drag.curX, dy=drag.startY-drag.curY;
    const dist=Math.sqrt(dx*dx+dy*dy);
    if (dist < 5) return;
    const power=Math.min(dist/(Math.min(W,H)*0.35),1);
    const len=power*120, nx=dx/dist, ny=dy/dist;
    ctx.save(); ctx.strokeStyle='rgba(255,255,255,0.7)'; ctx.lineWidth=2; ctx.setLineDash([6,6]);
    ctx.beginPath(); ctx.moveTo(bx,by); ctx.lineTo(bx+nx*len,by+ny*len); ctx.stroke();
    ctx.setLineDash([]);
    ctx.strokeStyle=`rgba(245,197,24,${0.5+power*0.5})`; ctx.lineWidth=2;
    ctx.beginPath(); ctx.arc(drag.curX,drag.curY,14,0,Math.PI*2); ctx.stroke();
    ctx.restore();
  }

  function loop() { updatePhysics(); render(); animId = requestAnimationFrame(loop); }
  function lerp(a,b,t) { return a+(b-a)*t; }

  function showToast(msg) {
    let t = document.querySelector('.toast');
    if (!t) { t = document.createElement('div'); t.className='toast'; document.body.appendChild(t); }
    t.textContent = msg; t.classList.add('show');
    clearTimeout(t._tid);
    t._tid = setTimeout(() => t.classList.remove('show'), 2200);
  }

  function getTotalStages() { return STAGES.length; }
  function getState()       { return state; }

  return { init, start, stop, getTotalStages, getState, showToast };
})();
