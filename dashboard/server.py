#!/usr/bin/env python3
"""
Venator-class Star Destroyer Dashboard — Imperial Operations Command
Nestor / OpenClaw Intelligence Interface
"""
import http.server, json, os, sys
sys.path.insert(0, '/home/node/.openclaw/workspace/automation/printify')

PORT = 18790
WORKSPACE = '/home/node/.openclaw/workspace'

HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Venator Command — Imperial Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;900&family=Share+Tech+Mono&display=swap" rel="stylesheet"/>
<style>
/* ─── RESET & BASE ─────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --imp-black:    #060a10;
  --imp-dark:     #0a1020;
  --imp-navy:     #0d1525;
  --imp-blue:     #142040;
  --imp-accent:   #1a4080;
  --imp-glow:     #2a7fff;
  --imp-bright:   #4db8ff;
  --imp-text:     #a8c8f0;
  --imp-dim:      #4a6080;
  --imp-red:      #ff3030;
  --imp-gold:     #f0b830;
  --imp-green:    #30ff80;
  --scan-color:   rgba(0,60,120,0.08);
  --font-main:    'Orbitron', sans-serif;
  --font-mono:    'Share Tech Mono', monospace;
}
html, body {
  background: var(--imp-black);
  color: var(--imp-text);
  font-family: var(--font-main);
  height: 100%;
  overflow: hidden;
}
body { display: flex; flex-direction: column; }

/* ─── SCANLINES OVERLAY ─────────────────────────────────────────────────── */
body::after {
  content: '';
  position: fixed; inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    var(--scan-color) 2px,
    var(--scan-color) 4px
  );
  pointer-events: none;
  z-index: 9999;
}

/* ─── METRICS BAR ───────────────────────────────────────────────────────── */
#metrics-bar {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(90deg, #050d1a 0%, #0a1830 50%, #050d1a 100%);
  border-bottom: 1px solid var(--imp-accent);
  padding: 6px 20px;
  font-family: var(--font-main);
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  position: relative;
  z-index: 100;
}
#metrics-bar::before {
  content: '';
  position: absolute; bottom: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--imp-glow), transparent);
  opacity: 0.6;
}
.metric-item {
  display: flex; align-items: center; gap: 8px;
}
.metric-label {
  color: var(--imp-dim);
  font-size: 9px;
}
.metric-value {
  color: var(--imp-bright);
  font-weight: 600;
  font-size: 11px;
  text-shadow: 0 0 8px var(--imp-glow);
}
.metric-value.pulse {
  animation: metricPulse 2s ease-in-out infinite;
}
@keyframes metricPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
.metric-sep {
  color: var(--imp-accent);
  opacity: 0.6;
  font-size: 14px;
}
#metrics-bar .logo-text {
  font-size: 11px;
  font-weight: 900;
  color: var(--imp-bright);
  letter-spacing: 0.2em;
  text-shadow: 0 0 12px var(--imp-glow);
}

/* ─── STAR WARS CRAWL ───────────────────────────────────────────────────── */
#crawl-overlay {
  position: fixed; inset: 0;
  background: #000;
  z-index: 5000;
  display: flex; flex-direction: column;
  align-items: center;
  overflow: hidden;
}
#crawl-canvas {
  position: absolute; inset: 0;
  width: 100%; height: 100%;
}
#crawl-skip {
  position: absolute; bottom: 30px; right: 30px;
  background: transparent;
  border: 1px solid rgba(255,220,0,0.5);
  color: rgba(255,220,0,0.7);
  font-family: var(--font-main);
  font-size: 10px;
  letter-spacing: 0.15em;
  padding: 8px 18px;
  cursor: pointer;
  z-index: 5100;
  transition: all 0.3s;
  text-transform: uppercase;
}
#crawl-skip:hover {
  background: rgba(255,220,0,0.1);
  border-color: rgba(255,220,0,0.9);
  color: rgba(255,220,0,1);
}
#crawl-logo {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  z-index: 5100;
  animation: logoFade 3s ease-in-out forwards;
}
#crawl-logo .logo-a {
  font-family: var(--font-main);
  font-size: clamp(20px, 5vw, 60px);
  font-weight: 900;
  color: #ffd700;
  letter-spacing: 0.3em;
  text-shadow: 0 0 30px #ffd700;
}
#crawl-logo .logo-b {
  font-family: var(--font-main);
  font-size: clamp(10px, 2vw, 22px);
  color: rgba(255,215,0,0.6);
  letter-spacing: 0.5em;
  margin-top: 4px;
}
@keyframes logoFade {
  0% { opacity: 0; transform: translate(-50%, -50%) scale(1.4); }
  30% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
  70% { opacity: 1; }
  100% { opacity: 0; pointer-events: none; }
}
#crawl-perspective {
  position: absolute;
  width: 60%;
  bottom: 0; left: 20%;
  perspective: 300px;
  perspective-origin: 50% 100%;
  overflow: hidden;
  height: 80%;
  display: none;
}
#crawl-text {
  transform: rotateX(25deg);
  transform-origin: 50% 100%;
  padding: 0 5%;
  text-align: justify;
  animation: crawlMove 40s linear forwards;
  animation-play-state: paused;
}
#crawl-text h1 {
  font-family: var(--font-main);
  font-size: clamp(12px, 2vw, 26px);
  color: #ffd700;
  text-align: center;
  letter-spacing: 0.3em;
  margin-bottom: 0.8em;
  text-transform: uppercase;
}
#crawl-text p {
  font-family: var(--font-main);
  font-size: clamp(9px, 1.4vw, 17px);
  line-height: 1.8;
  color: #ffd700;
  margin-bottom: 1em;
  letter-spacing: 0.08em;
}
@keyframes crawlMove {
  0%   { transform: rotateX(25deg) translateY(100%); }
  100% { transform: rotateX(25deg) translateY(-300%); }
}

/* ─── MAIN LAYOUT ───────────────────────────────────────────────────────── */
#main {
  flex: 1;
  display: grid;
  grid-template-rows: 1fr auto;
  overflow: hidden;
  position: relative;
}
#venator-wrap {
  position: relative;
  overflow: hidden;
  flex: 1;
}
#venator-svg {
  width: 100%;
  height: 100%;
  display: block;
}

/* ─── DECK OVERLAYS ─────────────────────────────────────────────────────── */
.deck-overlay {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  pointer-events: none;
  transition: opacity 0.3s;
}
.holo-screen {
  background: linear-gradient(135deg, #020e1e 0%, #041530 50%, #020e1e 100%);
  border: 1px solid var(--imp-accent);
  border-radius: 3px;
  padding: 5px 7px;
  font-family: var(--font-mono);
  font-size: 8px;
  color: var(--imp-bright);
  min-width: 90px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 10px rgba(42,127,255,0.25), inset 0 0 10px rgba(0,30,80,0.5);
}
.holo-screen::after {
  content: '';
  position: absolute; inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 3px,
    rgba(42,127,255,0.04) 3px,
    rgba(42,127,255,0.04) 4px
  );
  animation: scanAnim 4s linear infinite;
}
@keyframes scanAnim {
  0% { background-position: 0 0; }
  100% { background-position: 0 100px; }
}
.holo-title {
  font-size: 7px;
  color: var(--imp-glow);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  margin-bottom: 3px;
  font-family: var(--font-main);
}
.holo-line {
  color: var(--imp-text);
  opacity: 0.85;
  line-height: 1.5;
  font-size: 7.5px;
}
.console-dots {
  display: flex; flex-direction: column; gap: 3px;
}
.cdot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--imp-glow);
  box-shadow: 0 0 5px var(--imp-glow);
  animation: dotBlink 1.5s ease-in-out infinite;
}
.cdot:nth-child(2) { animation-delay: 0.3s; background: var(--imp-green); box-shadow: 0 0 5px var(--imp-green); }
.cdot:nth-child(3) { animation-delay: 0.6s; background: var(--imp-gold); box-shadow: 0 0 5px var(--imp-gold); }
@keyframes dotBlink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

/* ─── CHARACTER SVG SIZING ──────────────────────────────────────────────── */
.char-svg { width: 40px; height: 64px; flex-shrink: 0; }
.char-svg-sm { width: 32px; height: 52px; flex-shrink: 0; }
.char-svg-bridge { width: 44px; height: 70px; flex-shrink: 0; }

/* ─── MOUSE DROID ───────────────────────────────────────────────────────── */
#mouse-droid {
  position: absolute;
  width: 22px; height: 14px;
  background: linear-gradient(90deg, #111 0%, #222 50%, #111 100%);
  border: 1px solid #444;
  border-radius: 3px 6px 3px 3px;
  box-shadow: 0 0 6px rgba(100,100,200,0.4), inset 0 1px 0 rgba(255,255,255,0.1);
  pointer-events: none;
  z-index: 200;
  transition: none;
}
#mouse-droid::before {
  content: '';
  position: absolute;
  top: 2px; left: 3px;
  width: 5px; height: 5px;
  background: var(--imp-glow);
  border-radius: 50%;
  box-shadow: 0 0 4px var(--imp-glow);
  animation: eyeBlink 0.8s linear infinite;
}
@keyframes eyeBlink {
  0%, 90%, 100% { opacity: 1; }
  95% { opacity: 0; }
}

/* ─── MISSIONS PANEL ────────────────────────────────────────────────────── */
#missions-tab {
  position: fixed;
  right: 0; top: 50%;
  transform: translateY(-50%) translateX(0);
  z-index: 1000;
}
#missions-tab-btn {
  writing-mode: vertical-rl;
  text-orientation: mixed;
  background: linear-gradient(180deg, var(--imp-blue) 0%, var(--imp-navy) 100%);
  border: 1px solid var(--imp-accent);
  border-right: none;
  color: var(--imp-bright);
  font-family: var(--font-main);
  font-size: 9px;
  letter-spacing: 0.2em;
  padding: 16px 8px;
  cursor: pointer;
  text-transform: uppercase;
  transition: background 0.3s;
  box-shadow: -3px 0 12px rgba(42,127,255,0.2);
}
#missions-tab-btn:hover {
  background: linear-gradient(180deg, var(--imp-accent) 0%, var(--imp-blue) 100%);
}
#missions-panel {
  position: fixed;
  right: -340px; top: 0; bottom: 0;
  width: 340px;
  background: linear-gradient(135deg, #050d1a 0%, #0a1830 100%);
  border-left: 1px solid var(--imp-accent);
  z-index: 999;
  transition: right 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex; flex-direction: column;
  box-shadow: -8px 0 30px rgba(0,0,0,0.8);
  overflow-y: auto;
  padding: 0;
}
#missions-panel.open { right: 0; }
.missions-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--imp-accent);
  background: linear-gradient(90deg, var(--imp-navy) 0%, var(--imp-blue) 100%);
}
.missions-header h2 {
  font-size: 12px;
  letter-spacing: 0.3em;
  color: var(--imp-bright);
  text-shadow: 0 0 10px var(--imp-glow);
}
.missions-close {
  float: right;
  background: none;
  border: 1px solid var(--imp-accent);
  color: var(--imp-text);
  font-family: var(--font-main);
  font-size: 9px;
  padding: 4px 8px;
  cursor: pointer;
  letter-spacing: 0.1em;
  margin-top: -2px;
}
.mission-tier {
  padding: 14px 20px;
  border-bottom: 1px solid rgba(42,64,96,0.4);
}
.mission-tier-label {
  font-size: 9px;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  margin-bottom: 10px;
  font-weight: 600;
}
.mission-tier.p1 .mission-tier-label { color: var(--imp-red); text-shadow: 0 0 6px var(--imp-red); }
.mission-tier.p2 .mission-tier-label { color: var(--imp-gold); text-shadow: 0 0 6px var(--imp-gold); }
.mission-tier.p3 .mission-tier-label { color: var(--imp-dim); }
.mission-item {
  display: flex; align-items: flex-start; gap: 8px;
  margin-bottom: 8px;
  font-family: var(--font-mono);
  font-size: 10px;
  line-height: 1.5;
  color: var(--imp-text);
}
.mission-bullet {
  flex-shrink: 0;
  width: 6px; height: 6px;
  border-radius: 50%;
  margin-top: 4px;
}
.p1 .mission-bullet { background: var(--imp-red); box-shadow: 0 0 4px var(--imp-red); }
.p2 .mission-bullet { background: var(--imp-gold); box-shadow: 0 0 4px var(--imp-gold); }
.p3 .mission-bullet { background: var(--imp-dim); }

/* ─── INTEL TICKER ──────────────────────────────────────────────────────── */
#ticker-wrap {
  flex-shrink: 0;
  background: linear-gradient(90deg, #030810 0%, #05101e 50%, #030810 100%);
  border-top: 1px solid var(--imp-accent);
  height: 26px;
  overflow: hidden;
  position: relative;
  z-index: 100;
}
#ticker-wrap::before {
  content: 'INTEL';
  position: absolute; left: 0; top: 0; bottom: 0;
  width: 58px;
  background: var(--imp-blue);
  border-right: 1px solid var(--imp-accent);
  display: flex; align-items: center; justify-content: center;
  font-size: 8px;
  letter-spacing: 0.2em;
  color: var(--imp-bright);
  font-family: var(--font-main);
  z-index: 2;
  line-height: 26px;
  text-align: center;
  padding-left: 58px;
}
#ticker-track {
  display: flex;
  align-items: center;
  height: 100%;
  padding-left: 68px;
  white-space: nowrap;
  animation: tickerScroll 60s linear infinite;
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--imp-text);
  letter-spacing: 0.06em;
}
@keyframes tickerScroll {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
.ticker-sep { color: var(--imp-accent); margin: 0 20px; }

/* ─── ANIMATIONS ────────────────────────────────────────────────────────── */
@keyframes holoGlow {
  0%, 100% { opacity: 0.6; filter: drop-shadow(0 0 4px #2a7fff); }
  50% { opacity: 1; filter: drop-shadow(0 0 10px #4db8ff); }
}
@keyframes holoTablePulse {
  0%, 100% { opacity: 0.5; rx: 28; ry: 7; }
  50% { opacity: 0.9; rx: 32; ry: 9; }
}
@keyframes windowFlicker {
  0%, 95%, 100% { opacity: 0.7; }
  97% { opacity: 0.2; }
}
@keyframes lightPanelGlow {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}
</style>
</head>
<body>

<!-- ══════════════════════════════════════════════════════════
     CRAWL OVERLAY
══════════════════════════════════════════════════════════ -->
<div id="crawl-overlay">
  <canvas id="crawl-canvas"></canvas>
  <div id="crawl-logo">
    <div class="logo-a">VENATOR</div>
    <div class="logo-b">COMMAND DIVISION</div>
  </div>
  <div id="crawl-perspective">
    <div id="crawl-text">
      <h1>Episode IV</h1>
      <h1>A NEW LISTING</h1>
      <p>The IMPERIAL COMMERCE NETWORK has expanded its reach across the galaxy. Sales operations aboard the Venator-class Star Destroyer RELENTLESS continue under Commander NESTOR's watchful intelligence.</p>
      <p>With active listings multiplying across Printify, Etsy, and allied platforms, the Republic's remnant forces scramble to keep pace with fulfillment logistics stretching from the Outer Rim to the Core Worlds.</p>
      <p>Meanwhile, deep in the ship's operations center, Grand Admiral THRAWN reviews tactical projections on the holographic table. Agent CASSIAN monitors field intelligence. Senator PADMÉ coordinates diplomatic channels. Even young ANAKIN has proven useful — for certain… errands.</p>
      <p>As days count down to the May 11th campaign launch, the crew of the RELENTLESS stands ready. The Force — and the fulfillment pipeline — will be with us. Always.</p>
    </div>
  </div>
  <button id="crawl-skip" onclick="skipCrawl()">SKIP ▶</button>
</div>

<!-- ══════════════════════════════════════════════════════════
     METRICS BAR
══════════════════════════════════════════════════════════ -->
<div id="metrics-bar">
  <div class="metric-item">
    <span class="logo-text">⚙ RELENTLESS</span>
  </div>
  <div class="metric-item">
    <span class="metric-label">ACTIVE LISTINGS</span>
    <span class="metric-value pulse" id="m-listings">--</span>
  </div>
  <span class="metric-sep">|</span>
  <div class="metric-item">
    <span class="metric-label">CREDITS</span>
    <span class="metric-value" id="m-credits">0¢</span>
  </div>
  <span class="metric-sep">|</span>
  <div class="metric-item">
    <span class="metric-label">DAYS TO MAY 11</span>
    <span class="metric-value" id="m-days">--</span>
  </div>
  <span class="metric-sep">|</span>
  <div class="metric-item">
    <span class="metric-label">PLATFORMS</span>
    <span class="metric-value">3</span>
  </div>
  <span class="metric-sep">|</span>
  <div class="metric-item">
    <span class="metric-label">FLEET STATUS</span>
    <span class="metric-value" style="color:var(--imp-green);text-shadow:0 0 8px var(--imp-green);">OPERATIONAL</span>
  </div>
</div>

<!-- ══════════════════════════════════════════════════════════
     MAIN CONTENT
══════════════════════════════════════════════════════════ -->
<div id="main">
  <div id="venator-wrap">

    <!-- SVG VENATOR CROSS-SECTION -->
    <svg id="venator-svg" viewBox="0 -60 1400 680" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">
      <defs>
        <!-- Hull clip path -->
        <clipPath id="hull-clip">
          <polygon points="20,580 20,160 650,100 1380,300 1380,580"/>
        </clipPath>
        <!-- Bridge clip -->
        <clipPath id="bridge-clip">
          <polygon points="240,162 760,162 760,-60 240,-60"/>
        </clipPath>
        <!-- Glow filter -->
        <filter id="glow-blue" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="3" result="blur"/>
          <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
        <filter id="glow-strong" x="-100%" y="-100%" width="300%" height="300%">
          <feGaussianBlur stdDeviation="6" result="blur"/>
          <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
        <!-- Holo table radial -->
        <radialGradient id="holo-grad" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#4db8ff" stop-opacity="0.8"/>
          <stop offset="60%" stop-color="#2a7fff" stop-opacity="0.4"/>
          <stop offset="100%" stop-color="#0a3070" stop-opacity="0.1"/>
        </radialGradient>
        <!-- Deck gradient -->
        <linearGradient id="deck1-grad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#0f1e35"/>
          <stop offset="100%" stop-color="#0a1525"/>
        </linearGradient>
        <linearGradient id="deck2-grad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#0d1c30"/>
          <stop offset="100%" stop-color="#091422"/>
        </linearGradient>
        <linearGradient id="deck3-grad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#0b1a2c"/>
          <stop offset="100%" stop-color="#08121e"/>
        </linearGradient>
        <linearGradient id="deck4-grad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#091528"/>
          <stop offset="100%" stop-color="#060e1a"/>
        </linearGradient>
        <!-- Space gradient -->
        <radialGradient id="space-grad" cx="70%" cy="30%" r="80%">
          <stop offset="0%" stop-color="#050d1e"/>
          <stop offset="100%" stop-color="#010306"/>
        </radialGradient>
        <!-- Light panel gradient -->
        <linearGradient id="lp-grad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#2a7fff" stop-opacity="0"/>
          <stop offset="50%" stop-color="#2a7fff" stop-opacity="0.7"/>
          <stop offset="100%" stop-color="#2a7fff" stop-opacity="0"/>
        </linearGradient>
      </defs>

      <!-- ── SPACE BACKGROUND ── -->
      <rect x="0" y="-60" width="1400" height="740" fill="url(#space-grad)"/>
      <!-- Stars -->
      <g id="stars" opacity="0.7">
        <circle cx="45" cy="-40" r="1" fill="white" opacity="0.8"/>
        <circle cx="120" cy="-20" r="0.8" fill="white" opacity="0.6"/>
        <circle cx="200" cy="-50" r="1.2" fill="white" opacity="0.9"/>
        <circle cx="340" cy="-35" r="0.7" fill="white" opacity="0.5"/>
        <circle cx="480" cy="-55" r="1" fill="white" opacity="0.8"/>
        <circle cx="580" cy="-15" r="0.8" fill="white"/>
        <circle cx="700" cy="-45" r="1.1" fill="white" opacity="0.7"/>
        <circle cx="820" cy="-28" r="0.9" fill="white" opacity="0.6"/>
        <circle cx="950" cy="-52" r="1" fill="white" opacity="0.8"/>
        <circle cx="1080" cy="-18" r="0.7" fill="white" opacity="0.5"/>
        <circle cx="1200" cy="-42" r="1.2" fill="white" opacity="0.9"/>
        <circle cx="1320" cy="-30" r="0.8" fill="white" opacity="0.7"/>
        <circle cx="1380" cy="-55" r="1" fill="white"/>
        <circle cx="90" cy="70" r="0.6" fill="white" opacity="0.4"/>
        <circle cx="160" cy="85" r="0.8" fill="white" opacity="0.5"/>
        <circle cx="1300" cy="80" r="0.7" fill="#aaddff" opacity="0.5"/>
        <circle cx="1350" cy="120" r="0.9" fill="white" opacity="0.6"/>
      </g>

      <!-- ── HULL WEDGE ── -->
      <polygon points="20,580 20,160 650,100 1380,300 1380,580"
               fill="#0d1525" stroke="#2a3d55" stroke-width="1.5"/>

      <!-- ── DECK BANDS (clipped to hull) ── -->
      <g clip-path="url(#hull-clip)">

        <!-- Deck 1 — Cassian (Operations) -->
        <rect x="20" y="170" width="1360" height="88"
              fill="url(#deck1-grad)" opacity="0.95"/>
        <!-- Deck 2 — Padmé (Diplomacy) -->
        <rect x="20" y="263" width="1360" height="107"
              fill="url(#deck2-grad)" opacity="0.95"/>
        <!-- Deck 3 — Anakin (Engineering) -->
        <rect x="20" y="375" width="1360" height="85"
              fill="url(#deck3-grad)" opacity="0.95"/>
        <!-- Deck 4 — 3PO + R2 (Logistics) -->
        <rect x="20" y="465" width="1360" height="113"
              fill="url(#deck4-grad)" opacity="0.95"/>

        <!-- ── DECK SEPARATORS / GRATING ── -->
        <!-- Sep 1-2 -->
        <rect x="20" y="258" width="1360" height="5" fill="#1a2e48"/>
        <line x1="20" y1="259" x2="1380" y2="259" stroke="#2a4060" stroke-width="0.5"/>
        <line x1="20" y1="262" x2="1380" y2="262" stroke="#1a3050" stroke-width="0.5"/>
        <!-- Grating marks on sep 1-2 -->
        <g stroke="#2a4060" stroke-width="0.5" opacity="0.5">
          <line x1="100" y1="258" x2="100" y2="263"/>
          <line x1="200" y1="258" x2="200" y2="263"/>
          <line x1="300" y1="258" x2="300" y2="263"/>
          <line x1="400" y1="258" x2="400" y2="263"/>
          <line x1="500" y1="258" x2="500" y2="263"/>
          <line x1="600" y1="258" x2="600" y2="263"/>
          <line x1="700" y1="258" x2="700" y2="263"/>
          <line x1="800" y1="258" x2="800" y2="263"/>
          <line x1="900" y1="258" x2="900" y2="263"/>
          <line x1="1000" y1="258" x2="1000" y2="263"/>
          <line x1="1100" y1="258" x2="1100" y2="263"/>
          <line x1="1200" y1="258" x2="1200" y2="263"/>
          <line x1="1300" y1="258" x2="1300" y2="263"/>
        </g>
        <!-- Sep 2-3 -->
        <rect x="20" y="370" width="1360" height="5" fill="#182840"/>
        <line x1="20" y1="371" x2="1380" y2="371" stroke="#2a4060" stroke-width="0.5"/>
        <line x1="20" y1="374" x2="1380" y2="374" stroke="#1a3050" stroke-width="0.5"/>
        <g stroke="#2a4060" stroke-width="0.5" opacity="0.5">
          <line x1="150" y1="370" x2="150" y2="375"/>
          <line x1="300" y1="370" x2="300" y2="375"/>
          <line x1="450" y1="370" x2="450" y2="375"/>
          <line x1="600" y1="370" x2="600" y2="375"/>
          <line x1="750" y1="370" x2="750" y2="375"/>
          <line x1="900" y1="370" x2="900" y2="375"/>
          <line x1="1050" y1="370" x2="1050" y2="375"/>
          <line x1="1200" y1="370" x2="1200" y2="375"/>
          <line x1="1350" y1="370" x2="1350" y2="375"/>
        </g>
        <!-- Sep 3-4 -->
        <rect x="20" y="460" width="1360" height="5" fill="#141e30"/>
        <line x1="20" y1="461" x2="1380" y2="461" stroke="#2a4060" stroke-width="0.5"/>
        <line x1="20" y1="464" x2="1380" y2="464" stroke="#1a3050" stroke-width="0.5"/>
        <g stroke="#2a4060" stroke-width="0.5" opacity="0.5">
          <line x1="200" y1="460" x2="200" y2="465"/>
          <line x1="400" y1="460" x2="400" y2="465"/>
          <line x1="600" y1="460" x2="600" y2="465"/>
          <line x1="800" y1="460" x2="800" y2="465"/>
          <line x1="1000" y1="460" x2="1000" y2="465"/>
          <line x1="1200" y1="460" x2="1200" y2="465"/>
        </g>

        <!-- ── VERTICAL LIGHT PANELS — LEFT WALL ── -->
        <rect x="22" y="172" width="4" height="84"
              fill="url(#lp-grad)"
              style="animation: lightPanelGlow 2.1s ease-in-out infinite;"/>
        <rect x="22" y="265" width="4" height="103"
              fill="url(#lp-grad)"
              style="animation: lightPanelGlow 2.4s ease-in-out infinite; animation-delay:0.3s;"/>
        <rect x="22" y="377" width="4" height="81"
              fill="url(#lp-grad)"
              style="animation: lightPanelGlow 1.9s ease-in-out infinite; animation-delay:0.6s;"/>
        <rect x="22" y="467" width="4" height="109"
              fill="url(#lp-grad)"
              style="animation: lightPanelGlow 2.6s ease-in-out infinite; animation-delay:0.1s;"/>

        <!-- ── VERTICAL LIGHT PANELS — RIGHT WALL ── -->
        <rect x="1374" y="300" width="4" height="84"
              fill="url(#lp-grad)"
              style="animation: lightPanelGlow 2.1s ease-in-out infinite; animation-delay:1.0s;"/>
        <rect x="1374" y="390" width="4" height="70"
              fill="url(#lp-grad)"
              style="animation: lightPanelGlow 2.4s ease-in-out infinite; animation-delay:0.5s;"/>
        <rect x="1374" y="466" width="4" height="108"
              fill="url(#lp-grad)"
              style="animation: lightPanelGlow 2.0s ease-in-out infinite; animation-delay:1.2s;"/>

        <!-- ── DECK LABELS ── -->
        <text x="680" y="220" font-family="'Orbitron',sans-serif" font-size="11"
              fill="#2a7fff" opacity="0.6" letter-spacing="4" text-anchor="middle">
          DECK 1 — OPERATIONS / INTELLIGENCE
        </text>
        <text x="750" y="323" font-family="'Orbitron',sans-serif" font-size="11"
              fill="#2a7fff" opacity="0.6" letter-spacing="4" text-anchor="middle">
          DECK 2 — DIPLOMACY / COMMS
        </text>
        <text x="820" y="425" font-family="'Orbitron',sans-serif" font-size="11"
              fill="#2a7fff" opacity="0.6" letter-spacing="4" text-anchor="middle">
          DECK 3 — ENGINEERING / HANGAR
        </text>
        <text x="870" y="528" font-family="'Orbitron',sans-serif" font-size="11"
              fill="#2a7fff" opacity="0.6" letter-spacing="4" text-anchor="middle">
          DECK 4 — LOGISTICS / DROIDS
        </text>

      </g><!-- end hull-clip -->

      <!-- ── HULL OUTLINE OVERLAY ── -->
      <polygon points="20,580 20,160 650,100 1380,300 1380,580"
               fill="none" stroke="#2a4060" stroke-width="1.5" opacity="0.7"/>

      <!-- ── BRIDGE TOWER TIERS ── -->
      <!-- Tier 1 (base) -->
      <polygon points="240,162 330,108 670,108 760,162"
               fill="#131f30" stroke="#2a4060" stroke-width="1"/>
      <!-- Tier 2 -->
      <polygon points="330,108 375,68 625,68 670,108"
               fill="#101828" stroke="#2a4060" stroke-width="1"/>
      <!-- Tier 3 -->
      <polygon points="375,68 410,38 590,38 625,68"
               fill="#0d1422" stroke="#2a4060" stroke-width="1"/>

      <!-- ── BRIDGE ROOM ── -->
      <rect x="430" y="-20" width="140" height="58"
            fill="#0e1c2e" stroke="#2a4060" stroke-width="1.5"
            rx="2"/>
      <!-- Bridge windows (showing stars) -->
      <rect x="440" y="-14" width="14" height="8" fill="#0a2040" stroke="#2a5080" stroke-width="0.5" rx="1"
            style="animation: windowFlicker 8s ease-in-out infinite;"/>
      <rect x="459" y="-14" width="14" height="8" fill="#0a2040" stroke="#2a5080" stroke-width="0.5" rx="1"
            style="animation: windowFlicker 8s ease-in-out infinite; animation-delay:1.1s;"/>
      <rect x="478" y="-14" width="14" height="8" fill="#0a2040" stroke="#2a5080" stroke-width="0.5" rx="1"
            style="animation: windowFlicker 8s ease-in-out infinite; animation-delay:2.3s;"/>
      <rect x="497" y="-14" width="14" height="8" fill="#0a2040" stroke="#2a5080" stroke-width="0.5" rx="1"
            style="animation: windowFlicker 8s ease-in-out infinite; animation-delay:0.7s;"/>
      <rect x="516" y="-14" width="14" height="8" fill="#0a2040" stroke="#2a5080" stroke-width="0.5" rx="1"
            style="animation: windowFlicker 8s ease-in-out infinite; animation-delay:3.1s;"/>
      <rect x="535" y="-14" width="14" height="8" fill="#0a2040" stroke="#2a5080" stroke-width="0.5" rx="1"
            style="animation: windowFlicker 8s ease-in-out infinite; animation-delay:1.8s;"/>
      <rect x="554" y="-14" width="14" height="8" fill="#0a2040" stroke="#2a5080" stroke-width="0.5" rx="1"
            style="animation: windowFlicker 8s ease-in-out infinite; animation-delay:4.2s;"/>
      <!-- Stars visible through windows -->
      <g clip-path="url(#bridge-clip)">
        <circle cx="444" cy="-11" r="0.7" fill="white" opacity="0.8"/>
        <circle cx="452" cy="-8" r="0.5" fill="white" opacity="0.6"/>
        <circle cx="466" cy="-12" r="0.7" fill="white" opacity="0.9"/>
        <circle cx="482" cy="-9" r="0.5" fill="white" opacity="0.7"/>
        <circle cx="504" cy="-13" r="0.8" fill="white" opacity="0.5"/>
        <circle cx="521" cy="-10" r="0.6" fill="white" opacity="0.8"/>
        <circle cx="538" cy="-12" r="0.7" fill="#aaddff" opacity="0.7"/>
        <circle cx="558" cy="-9" r="0.5" fill="white" opacity="0.6"/>
      </g>

      <!-- ── HOLOGRAPHIC TABLE ── -->
      <ellipse cx="500" cy="30" rx="30" ry="8"
               fill="url(#holo-grad)"
               filter="url(#glow-blue)"
               style="animation: holoGlow 2s ease-in-out infinite;"/>
      <!-- Table base -->
      <rect x="494" y="30" width="12" height="8" fill="#0a2040" stroke="#1a4060" stroke-width="0.5"/>
      <rect x="488" y="37" width="24" height="3" fill="#0d2845" stroke="#1a4060" stroke-width="0.5" rx="1"/>

      <!-- ── BRIDGE GLOW ACCENT ── -->
      <line x1="240" y1="162" x2="760" y2="162" stroke="#2a7fff" stroke-width="0.8" opacity="0.4"/>
      <line x1="330" y1="108" x2="670" y2="108" stroke="#2a7fff" stroke-width="0.8" opacity="0.3"/>
      <line x1="375" y1="68" x2="625" y2="68" stroke="#2a7fff" stroke-width="0.8" opacity="0.3"/>
      <line x1="410" y1="38" x2="590" y2="38" stroke="#2a7fff" stroke-width="0.8" opacity="0.3"/>

    </svg><!-- end venator-svg -->

    <!-- ── HTML OVERLAYS ── -->

    <!-- Bridge: Thrawn -->
    <div class="deck-overlay" id="ov-bridge">
      <!-- Thrawn SVG pixel art -->
      <svg class="char-svg-bridge" viewBox="0 0 44 70" xmlns="http://www.w3.org/2000/svg">
        <!-- Head -->
        <rect x="15" y="2" width="14" height="14" fill="#2468b0" rx="2"/>
        <!-- Eyes (red) -->
        <rect x="17" y="7" width="3" height="3" fill="#ff2020"/>
        <rect x="24" y="7" width="3" height="3" fill="#ff2020"/>
        <!-- Eyebrow lines -->
        <rect x="17" y="5" width="3" height="1" fill="#1a4080"/>
        <rect x="24" y="5" width="3" height="1" fill="#1a4080"/>
        <!-- Mouth / chin -->
        <rect x="19" y="13" width="6" height="2" fill="#1e558a"/>
        <!-- Neck -->
        <rect x="19" y="16" width="6" height="4" fill="#2060a0"/>
        <!-- Body (white uniform) -->
        <rect x="12" y="20" width="20" height="22" fill="#d8e8f8" rx="2"/>
        <!-- Uniform details / rank bars -->
        <rect x="14" y="22" width="6" height="3" fill="#a0b8d0"/>
        <rect x="14" y="22" width="2" height="3" fill="#ff2020"/>
        <rect x="16" y="22" width="2" height="3" fill="#ff2020"/>
        <rect x="18" y="22" width="2" height="3" fill="#ffd700"/>
        <!-- Belt -->
        <rect x="12" y="40" width="20" height="3" fill="#9aa8b8"/>
        <!-- Legs -->
        <rect x="14" y="43" width="7" height="18" fill="#c0d0e0" rx="1"/>
        <rect x="23" y="43" width="7" height="18" fill="#c0d0e0" rx="1"/>
        <!-- Boots -->
        <rect x="13" y="58" width="9" height="5" fill="#2a3a4a" rx="1"/>
        <rect x="22" y="58" width="9" height="5" fill="#2a3a4a" rx="1"/>
        <!-- Arm left -->
        <rect x="5" y="20" width="7" height="16" fill="#d8e8f8" rx="1"/>
        <rect x="4" y="36" width="8" height="5" fill="#2468b0" rx="1"/>
        <!-- Arm right (holding datapad) -->
        <rect x="32" y="20" width="7" height="16" fill="#d8e8f8" rx="1"/>
        <rect x="31" y="33" width="9" height="7" fill="#0a2040" rx="1" stroke="#2a7fff" stroke-width="0.5"/>
      </svg>
      <div class="holo-screen" style="min-width:100px;">
        <div class="holo-title">BRIDGE / THRAWN</div>
        <div class="holo-line" id="bridge-status">TACTICAL ANALYSIS</div>
        <div class="holo-line">STATUS: COMMANDING</div>
        <div class="holo-line">ART DATABASE: LINKED</div>
      </div>
      <div class="console-dots">
        <div class="cdot"></div>
        <div class="cdot"></div>
        <div class="cdot"></div>
      </div>
    </div>

    <!-- Deck 1: Cassian -->
    <div class="deck-overlay" id="ov-deck1">
      <!-- Cassian SVG pixel art -->
      <svg class="char-svg" viewBox="0 0 40 64" xmlns="http://www.w3.org/2000/svg">
        <!-- Head -->
        <rect x="13" y="1" width="14" height="14" fill="#9a6a44" rx="2"/>
        <!-- Hair (dark) -->
        <rect x="13" y="1" width="14" height="5" fill="#2a1a0a" rx="2"/>
        <!-- Eyes -->
        <rect x="15" y="7" width="3" height="3" fill="#2a1800"/>
        <rect x="22" y="7" width="3" height="3" fill="#2a1800"/>
        <!-- Mouth -->
        <rect x="17" y="12" width="6" height="2" fill="#7a4a2a"/>
        <!-- Neck -->
        <rect x="17" y="15" width="6" height="4" fill="#8a5a34"/>
        <!-- Body (dark jacket) -->
        <rect x="10" y="19" width="20" height="22" fill="#1e2a38" rx="2"/>
        <!-- Jacket details -->
        <rect x="19" y="19" width="2" height="22" fill="#161e28"/>
        <rect x="12" y="21" width="5" height="2" fill="#2a3848"/>
        <!-- Belt w buckle -->
        <rect x="10" y="39" width="20" height="3" fill="#3a2a18"/>
        <rect x="18" y="39" width="4" height="3" fill="#6a5030"/>
        <!-- Legs (dark pants) -->
        <rect x="12" y="42" width="7" height="16" fill="#162030" rx="1"/>
        <rect x="21" y="42" width="7" height="16" fill="#162030" rx="1"/>
        <!-- Boots -->
        <rect x="11" y="55" width="9" height="5" fill="#1a1008" rx="1"/>
        <rect x="20" y="55" width="9" height="5" fill="#1a1008" rx="1"/>
        <!-- Arms -->
        <rect x="3" y="19" width="7" height="16" fill="#1e2a38" rx="1"/>
        <rect x="30" y="19" width="7" height="16" fill="#1e2a38" rx="1"/>
        <!-- Hands -->
        <rect x="3" y="35" width="7" height="5" fill="#9a6a44" rx="1"/>
        <rect x="30" y="35" width="7" height="5" fill="#9a6a44" rx="1"/>
      </svg>
      <div class="holo-screen">
        <div class="holo-title">CASSIAN / INTEL</div>
        <div class="holo-line" id="deck1-status">MONITORING</div>
        <div class="holo-line">FIELD REPORTS: LIVE</div>
      </div>
      <div class="console-dots">
        <div class="cdot"></div>
        <div class="cdot"></div>
        <div class="cdot"></div>
      </div>
    </div>

    <!-- Deck 2: Padmé -->
    <div class="deck-overlay" id="ov-deck2">
      <!-- Padmé SVG pixel art -->
      <svg class="char-svg" viewBox="0 0 40 64" xmlns="http://www.w3.org/2000/svg">
        <!-- Hair (dark brown, elaborate) -->
        <rect x="12" y="0" width="16" height="8" fill="#3a2010" rx="3"/>
        <rect x="9" y="3" width="5" height="10" fill="#3a2010" rx="2"/>
        <rect x="26" y="3" width="5" height="10" fill="#3a2010" rx="2"/>
        <!-- Head (fair skin) -->
        <rect x="13" y="4" width="14" height="13" fill="#f5d0a8" rx="2"/>
        <!-- Eyes -->
        <rect x="15" y="9" width="3" height="3" fill="#3a2010"/>
        <rect x="22" y="9" width="3" height="3" fill="#3a2010"/>
        <!-- Lips -->
        <rect x="17" y="14" width="6" height="2" fill="#c0604a"/>
        <!-- Neck -->
        <rect x="17" y="17" width="6" height="4" fill="#f0c898"/>
        <!-- Dress / robe (white/cream) -->
        <rect x="9" y="21" width="22" height="26" fill="#f5f0e0" rx="3"/>
        <!-- Dress detail center panel -->
        <rect x="17" y="21" width="6" height="26" fill="#e8e0cc"/>
        <!-- Brooch/necklace -->
        <ellipse cx="20" cy="24" rx="3" ry="2" fill="#c8a840" stroke="#a08020" stroke-width="0.5"/>
        <!-- Sleeves -->
        <rect x="3" y="21" width="6" height="18" fill="#f0ebd8" rx="2"/>
        <rect x="31" y="21" width="6" height="18" fill="#f0ebd8" rx="2"/>
        <!-- Hands -->
        <rect x="3" y="39" width="6" height="5" fill="#f5d0a8" rx="1"/>
        <rect x="31" y="39" width="6" height="5" fill="#f5d0a8" rx="1"/>
        <!-- Skirt bottom -->
        <rect x="9" y="47" width="22" height="12" fill="#f5f0e0" rx="2"/>
        <!-- Feet/shoes -->
        <rect x="11" y="57" width="8" height="4" fill="#c8a840" rx="1"/>
        <rect x="21" y="57" width="8" height="4" fill="#c8a840" rx="1"/>
      </svg>
      <div class="holo-screen">
        <div class="holo-title">PADMÉ / COMMS</div>
        <div class="holo-line" id="deck2-status">DIPLOMACY ACTIVE</div>
        <div class="holo-line">CHANNEL: SECURE</div>
      </div>
      <div class="console-dots">
        <div class="cdot"></div>
        <div class="cdot"></div>
        <div class="cdot"></div>
      </div>
    </div>

    <!-- Deck 3: Anakin -->
    <div class="deck-overlay" id="ov-deck3">
      <!-- Anakin SVG pixel art -->
      <svg class="char-svg" viewBox="0 0 40 64" xmlns="http://www.w3.org/2000/svg">
        <!-- Hair (sandy brown) -->
        <rect x="13" y="1" width="14" height="6" fill="#8a6830" rx="2"/>
        <!-- Head (fair) -->
        <rect x="13" y="4" width="14" height="13" fill="#f0c898" rx="2"/>
        <!-- Eyes (blue-grey) -->
        <rect x="15" y="10" width="3" height="3" fill="#3a5080"/>
        <rect x="22" y="10" width="3" height="3" fill="#3a5080"/>
        <!-- Mouth -->
        <rect x="17" y="14" width="6" height="2" fill="#c09070"/>
        <!-- Neck -->
        <rect x="17" y="17" width="6" height="4" fill="#e8b888"/>
        <!-- Body (dark navy tabard over tan) -->
        <rect x="11" y="21" width="18" height="22" fill="#c8a870"/><!-- undershirt tan -->
        <rect x="13" y="21" width="14" height="22" fill="#1a2840" rx="1"/><!-- tabard dark -->
        <!-- Tabard stitching -->
        <rect x="18" y="21" width="4" height="22" fill="#161e30"/>
        <!-- Belt -->
        <rect x="11" y="41" width="18" height="3" fill="#3a2808"/>
        <rect x="17" y="41" width="6" height="3" fill="#6a4818"/>
        <!-- Legs (tan/brown) -->
        <rect x="13" y="44" width="6" height="15" fill="#b89858" rx="1"/>
        <rect x="21" y="44" width="6" height="15" fill="#b89858" rx="1"/>
        <!-- Boots -->
        <rect x="12" y="56" width="8" height="5" fill="#281808" rx="1"/>
        <rect x="20" y="56" width="8" height="5" fill="#281808" rx="1"/>
        <!-- Arms (tan undershirt, right has glove) -->
        <rect x="4" y="21" width="7" height="16" fill="#c8a870" rx="1"/>
        <rect x="29" y="21" width="7" height="16" fill="#281808" rx="1"/><!-- gloved arm -->
        <!-- Lightsaber (blue) -->
        <rect x="32" y="1" width="3" height="22" fill="#4db8ff" rx="1" opacity="0.9"
              style="filter: drop-shadow(0 0 4px #2a7fff);"/>
        <rect x="31" y="20" width="5" height="5" fill="#6a5020" rx="1"/><!-- hilt -->
        <!-- Left hand -->
        <rect x="3" y="37" width="8" height="5" fill="#f0c898" rx="1"/>
      </svg>
      <div class="holo-screen">
        <div class="holo-title">ANAKIN / ENGINEERING</div>
        <div class="holo-line" id="deck3-status">HYPERDRIVE: ONLINE</div>
        <div class="holo-line">MIDI-CHLORIANS: HIGH</div>
      </div>
      <div class="console-dots">
        <div class="cdot"></div>
        <div class="cdot"></div>
        <div class="cdot"></div>
      </div>
    </div>

    <!-- Deck 4: 3PO + R2 -->
    <div class="deck-overlay" id="ov-deck4" style="gap:6px;">
      <!-- C-3PO SVG pixel art -->
      <svg class="char-svg-sm" viewBox="0 0 32 52" xmlns="http://www.w3.org/2000/svg">
        <!-- Head (gold) -->
        <rect x="9" y="1" width="14" height="12" fill="#daa520" rx="6"/>
        <!-- Eyes (yellow-white) -->
        <ellipse cx="12" cy="7" rx="2.5" ry="2.5" fill="#ffffa0"/>
        <ellipse cx="20" cy="7" rx="2.5" ry="2.5" fill="#ffffa0"/>
        <!-- Mouth grille -->
        <rect x="11" y="11" width="10" height="2" fill="#b8880a" rx="1"/>
        <!-- Neck -->
        <rect x="13" y="13" width="6" height="4" fill="#c89010"/>
        <!-- Torso (gold) -->
        <rect x="7" y="17" width="18" height="18" fill="#daa520" rx="2"/>
        <!-- Chest panel -->
        <rect x="11" y="19" width="10" height="9" fill="#b8880a" rx="1"/>
        <rect x="12" y="20" width="3" height="2" fill="#ff8800" opacity="0.7"/>
        <rect x="17" y="20" width="3" height="2" fill="#ff4400" opacity="0.7"/>
        <!-- Waist -->
        <rect x="9" y="33" width="14" height="4" fill="#b8880a"/>
        <!-- Legs -->
        <rect x="9" y="37" width="6" height="12" fill="#daa520" rx="1"/>
        <rect x="17" y="37" width="6" height="12" fill="#daa520" rx="1"/>
        <!-- Feet -->
        <rect x="8" y="47" width="8" height="4" fill="#c89010" rx="1"/>
        <rect x="16" y="47" width="8" height="4" fill="#c89010" rx="1"/>
        <!-- Arms -->
        <rect x="1" y="17" width="6" height="14" fill="#daa520" rx="1"/>
        <rect x="25" y="17" width="6" height="14" fill="#daa520" rx="1"/>
      </svg>
      <!-- R2-D2 SVG pixel art -->
      <svg class="char-svg-sm" viewBox="0 0 32 52" xmlns="http://www.w3.org/2000/svg">
        <!-- Dome (white with blue) -->
        <ellipse cx="16" cy="12" rx="12" ry="12" fill="#e8eef8"/>
        <ellipse cx="16" cy="12" rx="12" ry="12" fill="none" stroke="#4080c0" stroke-width="1.5"/>
        <!-- Dome blue arcs -->
        <path d="M 6 12 A 10 10 0 0 1 26 12" fill="none" stroke="#4080c0" stroke-width="3"/>
        <!-- Eye lens -->
        <circle cx="16" cy="10" r="3" fill="#4080c0"/>
        <circle cx="16" cy="10" r="1.5" fill="#80b8ff"/>
        <!-- Side eyes -->
        <circle cx="9" cy="9" r="2" fill="#4080c0"/>
        <circle cx="23" cy="9" r="2" fill="#4080c0"/>
        <!-- Body (white/blue panels) -->
        <rect x="6" y="22" width="20" height="22" fill="#e8eef8" rx="3"/>
        <!-- Blue panel stripes -->
        <rect x="6" y="24" width="20" height="4" fill="#4080c0" rx="1"/>
        <rect x="6" y="32" width="20" height="4" fill="#4080c0" rx="1"/>
        <!-- Center panel -->
        <rect x="12" y="28" width="8" height="8" fill="#c8d8f0"/>
        <!-- Lights on body -->
        <circle cx="9" cy="36" r="1.5" fill="#ff4040" opacity="0.9"/>
        <circle cx="12" cy="38" r="1.5" fill="#40ff80" opacity="0.9"/>
        <!-- Legs (chunky) -->
        <rect x="7" y="43" width="7" height="7" fill="#d0d8e8" rx="2"/>
        <rect x="18" y="43" width="7" height="7" fill="#d0d8e8" rx="2"/>
        <!-- Feet -->
        <rect x="5" y="48" width="10" height="3" fill="#b0b8c8" rx="1"/>
        <rect x="17" y="48" width="10" height="3" fill="#b0b8c8" rx="1"/>
      </svg>
      <div class="holo-screen">
        <div class="holo-title">DROIDS / LOGISTICS</div>
        <div class="holo-line" id="deck4-status">3PO: TRANSLATING</div>
        <div class="holo-line">R2: INTERFACING</div>
      </div>
      <div class="console-dots">
        <div class="cdot"></div>
        <div class="cdot"></div>
        <div class="cdot"></div>
      </div>
    </div>

    <!-- ── MOUSE DROID ── -->
    <div id="mouse-droid"></div>

  </div><!-- end venator-wrap -->

  <!-- ── INTEL TICKER ── -->
  <div id="ticker-wrap">
    <div id="ticker-track" id="ticker-inner">
      <span>FLEET STATUS: ALL SYSTEMS NOMINAL</span>
      <span class="ticker-sep">◆</span>
      <span>PRINTIFY OPERATIONS: SYNCHRONIZED</span>
      <span class="ticker-sep">◆</span>
      <span>GRAND ADMIRAL THRAWN REPORTS: COMMERCE OFFENSIVE ON SCHEDULE</span>
      <span class="ticker-sep">◆</span>
      <span id="ticker-days">DAYS UNTIL CAMPAIGN LAUNCH: CALCULATING...</span>
      <span class="ticker-sep">◆</span>
      <span>CASSIAN: FIELD INTEL UPDATED</span>
      <span class="ticker-sep">◆</span>
      <span>PADMÉ: DIPLOMATIC CHANNELS SECURE</span>
      <span class="ticker-sep">◆</span>
      <span>ANAKIN: HYPERDRIVE MAINTENANCE COMPLETE — AGAIN</span>
      <span class="ticker-sep">◆</span>
      <span>3PO: FLUENT IN OVER SIX MILLION FORMS OF COMMERCE</span>
      <span class="ticker-sep">◆</span>
      <span>R2-D2 BEEPS AFFIRMATIVELY AT FULFILLMENT METRICS</span>
      <span class="ticker-sep">◆</span>
      <span>FLEET STATUS: ALL SYSTEMS NOMINAL</span>
      <span class="ticker-sep">◆</span>
      <span>PRINTIFY OPERATIONS: SYNCHRONIZED</span>
      <span class="ticker-sep">◆</span>
      <span>GRAND ADMIRAL THRAWN REPORTS: COMMERCE OFFENSIVE ON SCHEDULE</span>
      <span class="ticker-sep">◆</span>
      <span id="ticker-days-2">DAYS UNTIL CAMPAIGN LAUNCH: CALCULATING...</span>
      <span class="ticker-sep">◆</span>
      <span>NESTOR INTELLIGENCE SYSTEM: ACTIVE</span>
      <span class="ticker-sep">◆</span>
    </div>
  </div>

</div><!-- end main -->

<!-- ── MISSIONS PANEL ── -->
<div id="missions-tab">
  <button id="missions-tab-btn" onclick="toggleMissions()">MISSIONS</button>
</div>

<div id="missions-panel">
  <div class="missions-header">
    <button class="missions-close" onclick="toggleMissions()">✕ CLOSE</button>
    <h2>⚡ MISSION ORDERS</h2>
  </div>

  <div class="mission-tier p1">
    <div class="mission-tier-label">🔴 PRIORITY ONE</div>
    <div class="mission-item">
      <div class="mission-bullet"></div>
      <span>Launch May 11 campaign — all listings synchronized across platforms</span>
    </div>
    <div class="mission-item">
      <div class="mission-bullet"></div>
      <span>Verify Printify product catalog — active listing count confirmed</span>
    </div>
    <div class="mission-item">
      <div class="mission-bullet"></div>
      <span>Review Cassian intelligence report — field data integration</span>
    </div>
  </div>

  <div class="mission-tier p2">
    <div class="mission-tier-label">🟡 THIS WEEK</div>
    <div class="mission-item">
      <div class="mission-bullet"></div>
      <span>Padmé comms — coordinate with Etsy & secondary platforms</span>
    </div>
    <div class="mission-item">
      <div class="mission-bullet"></div>
      <span>Anakin engineering — optimize fulfillment pipeline throughput</span>
    </div>
    <div class="mission-item">
      <div class="mission-bullet"></div>
      <span>R2 logistics scan — inventory reconciliation across all shops</span>
    </div>
    <div class="mission-item">
      <div class="mission-bullet"></div>
      <span>3PO translation — product descriptions reviewed for 6M+ languages</span>
    </div>
  </div>

  <div class="mission-tier p3">
    <div class="mission-tier-label">🔵 HORIZON</div>
    <div class="mission-item">
      <div class="mission-bullet"></div>
      <span>Expand to outer rim platforms — Amazon Handmade, Redbubble</span>
    </div>
    <div class="mission-item">
      <div class="mission-bullet"></div>
      <span>Thrawn tactical review — Q3 commerce strategy analysis</span>
    </div>
    <div class="mission-item">
      <div class="mission-bullet"></div>
      <span>Deploy automated reorder triggers — Cassian field protocol</span>
    </div>
    <div class="mission-item">
      <div class="mission-bullet"></div>
      <span>Scale hyperdrive capacity — fulfillment speed upgrade</span>
    </div>
    <div class="mission-item">
      <div class="mission-bullet"></div>
      <span>Establish forward base — new platform integrations Phase II</span>
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════════════════════════
     JAVASCRIPT
══════════════════════════════════════════════════════════ -->
<script>
/* ── CONSTANTS ── */
const MAY11 = new Date('2026-05-11T00:00:00');
const SVG_VIEWBOX = { x: 0, y: -60, w: 1400, h: 680 };

/* ── STARFIELD ── */
function initStarfield(canvas) {
  const ctx = canvas.getContext('2d');
  let stars = [];
  function resize() {
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    stars = [];
    for (let i = 0; i < 300; i++) {
      stars.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        r: Math.random() * 1.5 + 0.3,
        speed: Math.random() * 0.3 + 0.05,
        opacity: Math.random() * 0.8 + 0.2
      });
    }
  }
  function draw() {
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    stars.forEach(s => {
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255,255,255,${s.opacity})`;
      ctx.fill();
      s.y += s.speed;
      if (s.y > canvas.height) { s.y = 0; s.x = Math.random() * canvas.width; }
    });
    requestAnimationFrame(draw);
  }
  resize();
  window.addEventListener('resize', resize);
  draw();
}

/* ── CRAWL ── */
let crawlActive = true;
let crawlTextEl, crawlPerspEl, crawlLogoEl, crawlSkip;

function initCrawl() {
  const canvas = document.getElementById('crawl-canvas');
  canvas.style.width = '100%';
  canvas.style.height = '100%';
  initStarfield(canvas);
  crawlLogoEl = document.getElementById('crawl-logo');
  crawlPerspEl = document.getElementById('crawl-perspective');
  crawlTextEl = document.getElementById('crawl-text');

  // Fetch intel for crawl text
  fetch('/api/intel').then(r => r.json()).then(data => {
    if (data.content && data.content !== 'No report on file.') {
      const p = document.createElement('p');
      p.textContent = data.content.slice(0, 300) + '...';
      crawlTextEl.appendChild(p);
    }
  }).catch(() => {});

  // After logo fades (3s), show crawl text
  setTimeout(() => {
    crawlPerspEl.style.display = 'block';
    crawlTextEl.style.animationPlayState = 'running';
  }, 3200);

  // Auto-finish crawl after 44s
  setTimeout(() => { if (crawlActive) finishCrawl(); }, 44000);
}

function skipCrawl() { finishCrawl(); }

function finishCrawl() {
  crawlActive = false;
  const overlay = document.getElementById('crawl-overlay');
  overlay.style.transition = 'opacity 1.2s';
  overlay.style.opacity = '0';
  setTimeout(() => {
    overlay.style.display = 'none';
    positionOverlays();
    startDroidAnimation();
  }, 1250);
}

/* ── SVG COORDINATE → SCREEN PIXEL MAPPING ── */
function svgToScreen(svgX, svgY) {
  const svg = document.getElementById('venator-svg');
  const rect = svg.getBoundingClientRect();
  const wrap = document.getElementById('venator-wrap');
  const wrapRect = wrap.getBoundingClientRect();

  // SVG viewBox: x=0 y=-60 w=1400 h=680
  const vbX = SVG_VIEWBOX.x;
  const vbY = SVG_VIEWBOX.y;
  const vbW = SVG_VIEWBOX.w;
  const vbH = SVG_VIEWBOX.h;

  // Rendered SVG dimensions in screen pixels (preserveAspectRatio: xMidYMid meet)
  const scaleX = rect.width / vbW;
  const scaleY = rect.height / vbH;
  const scale = Math.min(scaleX, scaleY);

  const renderW = vbW * scale;
  const renderH = vbH * scale;
  const offsetX = rect.left - wrapRect.left + (rect.width - renderW) / 2;
  const offsetY = rect.top - wrapRect.top + (rect.height - renderH) / 2;

  const screenX = offsetX + (svgX - vbX) * scale;
  const screenY = offsetY + (svgY - vbY) * scale;
  return { x: screenX, y: screenY, scale: scale };
}

function positionOverlays() {
  const wrap = document.getElementById('venator-wrap');

  // Bridge overlay — inside bridge room SVG coords approx (430, -10)
  positionOverlay('ov-bridge', 360, 0);

  // Deck 1 overlay — Cassian: SVG y=170 to 258, start at x=50
  positionOverlay('ov-deck1', 50, 185);

  // Deck 2 overlay — Padmé: SVG y=263 to 370
  positionOverlay('ov-deck2', 50, 280);

  // Deck 3 overlay — Anakin: SVG y=375 to 460
  positionOverlay('ov-deck3', 50, 390);

  // Deck 4 overlay — 3PO + R2: SVG y=465 to 578
  positionOverlay('ov-deck4', 50, 480);
}

function positionOverlay(id, svgX, svgY) {
  const el = document.getElementById(id);
  if (!el) return;
  const pos = svgToScreen(svgX, svgY);
  el.style.left = pos.x + 'px';
  el.style.top  = pos.y + 'px';
}

window.addEventListener('resize', positionOverlays);

/* ── MOUSE DROID ANIMATION ── */
const DECK_FLOORS = [
  { svgY: 245 },  // Deck 1 floor
  { svgY: 355 },  // Deck 2 floor
  { svgY: 447 },  // Deck 3 floor
  { svgY: 560 },  // Deck 4 floor
];

function startDroidAnimation() {
  animateDroid();
}

function animateDroid() {
  const droid = document.getElementById('mouse-droid');
  if (!droid) return;

  const deck = DECK_FLOORS[Math.floor(Math.random() * DECK_FLOORS.length)];
  const goRight = Math.random() > 0.5;

  // Get screen coordinates for start/end
  const startSvgX = goRight ? 30 : 1360;
  const endSvgX   = goRight ? 1360 : 30;

  const startPos = svgToScreen(startSvgX, deck.svgY - 14);
  const endPos   = svgToScreen(endSvgX, deck.svgY - 14);

  droid.style.transition = 'none';
  droid.style.left = startPos.x + 'px';
  droid.style.top  = startPos.y + 'px';
  droid.style.display = 'block';
  droid.style.transform = goRight ? 'scaleX(1)' : 'scaleX(-1)';

  const duration = 8000 + Math.random() * 6000;
  droid.style.transition = `left ${duration}ms linear, top ${duration}ms linear`;

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      droid.style.left = endPos.x + 'px';
      droid.style.top  = endPos.y + 'px';
    });
  });

  const nextDelay = 15000 + Math.random() * 25000;
  setTimeout(() => {
    droid.style.display = 'none';
    setTimeout(animateDroid, 2000);
  }, duration + 1000);
}

/* ── METRICS ── */
function updateMetrics() {
  // Days to May 11
  const now = new Date();
  const diff = MAY11 - now;
  const days = Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
  document.getElementById('m-days').textContent = days + 'd';
  const tickerDays = document.getElementById('ticker-days');
  const tickerDays2 = document.getElementById('ticker-days-2');
  if (tickerDays) tickerDays.textContent = `DAYS UNTIL CAMPAIGN LAUNCH: ${days}`;
  if (tickerDays2) tickerDays2.textContent = `DAYS UNTIL CAMPAIGN LAUNCH: ${days}`;

  // Listings from API
  fetch('/api/metrics').then(r => r.json()).then(data => {
    const listingsEl = document.getElementById('m-listings');
    if (listingsEl) listingsEl.textContent = data.listings !== undefined ? data.listings : '--';
  }).catch(() => {});
}

/* ── MISSIONS PANEL ── */
let missionsOpen = false;
function toggleMissions() {
  const panel = document.getElementById('missions-panel');
  missionsOpen = !missionsOpen;
  if (missionsOpen) panel.classList.add('open');
  else panel.classList.remove('open');
}

/* ── HOLO STATUS CYCLING ── */
const bridgeLines = [
  'TACTICAL ANALYSIS', 'FLEET DEPLOYMENT', 'COMMERCE REVIEW',
  'ART DATABASE: CROSS-REF', 'ENEMY PATTERNS: NOTED'
];
const cassianLines = [
  'MONITORING', 'FIELD REPORT IN', 'INTEL UPDATED',
  'COMMS ENCRYPTED', 'TARGET ACQUIRED'
];
const padmeLines = [
  'DIPLOMACY ACTIVE', 'TREATY REVIEW', 'COMMS RELAY',
  'SENATE BRIEFING', 'SECURE CHANNEL'
];
const anakinLines = [
  'HYPERDRIVE: ONLINE', 'REPAIRS COMPLETE', 'MISSION READY',
  'FORCE: STRONG', 'ENGINE CHECK: GO'
];
const droidLines = [
  '3PO: TRANSLATING', '3PO: CALCULATING', '3PO: COMPLAINING',
  '3PO: PROTOCOL MODE', '3PO: ALARMED'
];

function cycleLine(elId, lines) {
  const el = document.getElementById(elId);
  if (!el) return;
  let idx = 0;
  setInterval(() => {
    idx = (idx + 1) % lines.length;
    el.style.opacity = '0';
    setTimeout(() => {
      el.textContent = lines[idx];
      el.style.opacity = '1';
    }, 400);
    el.style.transition = 'opacity 0.4s';
  }, 4000 + Math.random() * 2000);
}

/* ── INIT ── */
document.addEventListener('DOMContentLoaded', () => {
  initCrawl();
  updateMetrics();
  setInterval(updateMetrics, 60000);
  cycleLine('bridge-status', bridgeLines);
  cycleLine('deck1-status', cassianLines);
  cycleLine('deck2-status', padmeLines);
  cycleLine('deck3-status', anakinLines);
  cycleLine('deck4-status', droidLines);
});
</script>
</body>
</html>
'''


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress noisy access logs

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))

        elif self.path == '/api/intel':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            try:
                report_path = f'{WORKSPACE}/memory/last-cassian-report.md'
                with open(report_path, encoding='utf-8') as f:
                    content = f.read()
            except FileNotFoundError:
                content = 'No field report on file. Awaiting Cassian transmission.'
            except Exception as e:
                content = f'Report access error: {e}'
            self.wfile.write(json.dumps({'content': content}).encode('utf-8'))

        elif self.path == '/api/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            count = '--'
            try:
                from printify_api import api_request
                products = api_request('GET', '/shops/27174580/products.json')
                if products and isinstance(products, dict):
                    count = len(products.get('data', []))
                elif products and isinstance(products, list):
                    count = len(products)
            except ImportError:
                count = 'N/A'
            except Exception:
                count = '--'
            self.wfile.write(json.dumps({'listings': count}).encode('utf-8'))

        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            import datetime
            self.wfile.write(json.dumps({
                'status': 'operational',
                'server': 'Venator-class Dashboard',
                'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            }).encode('utf-8'))

        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'404 - Sector not found\n')


if __name__ == '__main__':
    server_address = ('0.0.0.0', PORT)
    httpd = http.server.HTTPServer(server_address, Handler)
    print(f'[Venator Dashboard] Serving on http://localhost:{PORT}')
    print(f'[Venator Dashboard] Workspace: {WORKSPACE}')
    print(f'[Venator Dashboard] Press Ctrl+C to stand down.')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n[Venator Dashboard] Standing down. May the Force be with us.')
        httpd.server_close()
