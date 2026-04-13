import streamlit as st
import requests
import socket
import subprocess
import platform
import re
import time
import psutil
import math
import json
import hashlib
from datetime import datetime
import ipaddress
from functools import lru_cache

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NetPulse v4 · Network Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ════════════════════════════════════════════════════════════════════════════
# THEME STATE (Light / Dark toggle)
# ════════════════════════════════════════════════════════════════════════════
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True

# ════════════════════════════════════════════════════════════════════════════
# LIVE MONITOR STATE
# ════════════════════════════════════════════════════════════════════════════
if "monitor_running" not in st.session_state:
    st.session_state["monitor_running"] = False
if "monitor_history" not in st.session_state:
    st.session_state["monitor_history"] = []
if "monitor_tick" not in st.session_state:
    st.session_state["monitor_tick"] = 0

# ════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM + ANIMATIONS  (v4 — Upgraded)
# ════════════════════════════════════════════════════════════════════════════
def get_css(dark=True):
    if dark:
        vars_css = """
  --bg:      #020810;
  --bg2:     #050d1e;
  --bg3:     #081228;
  --surf:    #0b1730;
  --surf2:   #0f1e3a;
  --border:  #182c4e;
  --border2: #223a66;
  --blue:    #3b82f6;
  --blue2:   #60a5fa;
  --cyan:    #06b6d4;
  --green:   #10b981;
  --green2:  #34d399;
  --amber:   #f59e0b;
  --red:     #ef4444;
  --purple:  #8b5cf6;
  --pink:    #ec4899;
  --orange:  #f97316;
  --text:    #cbd5e1;
  --text2:   #94a3b8;
  --bright:  #f1f5f9;
  --dim:     #475569;
"""
    else:
        vars_css = """
  --bg:      #f0f4ff;
  --bg2:     #e8eef8;
  --bg3:     #dde5f5;
  --surf:    #ffffff;
  --surf2:   #f5f8ff;
  --border:  #c3d1ea;
  --border2: #a3b8d8;
  --blue:    #2563eb;
  --blue2:   #1d4ed8;
  --cyan:    #0891b2;
  --green:   #059669;
  --green2:  #047857;
  --amber:   #d97706;
  --red:     #dc2626;
  --purple:  #7c3aed;
  --pink:    #db2777;
  --orange:  #ea580c;
  --text:    #1e293b;
  --text2:   #334155;
  --bright:  #0f172a;
  --dim:     #64748b;
"""
    bg_effects = """
.stApp::before{
  content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
  background:
    radial-gradient(ellipse 70% 50% at 15% 8%,  rgba(59,130,246,.09)  0%,transparent 55%),
    radial-gradient(ellipse 50% 60% at 85% 92%,  rgba(139,92,246,.08)  0%,transparent 55%),
    radial-gradient(ellipse 40% 35% at 65% 50%,  rgba(6,182,212,.05)   0%,transparent 50%),
    radial-gradient(ellipse 30% 25% at 50% 20%,  rgba(236,72,153,.04)  0%,transparent 45%);
  animation:bgPulse 14s ease-in-out infinite alternate}
""" if dark else """
.stApp::before{
  content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
  background:
    radial-gradient(ellipse 70% 50% at 15% 8%,  rgba(37,99,235,.06)  0%,transparent 55%),
    radial-gradient(ellipse 50% 60% at 85% 92%,  rgba(124,58,237,.05)  0%,transparent 55%);
  animation:bgPulse 14s ease-in-out infinite alternate}
"""
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500;600&display=swap');

:root {{
{vars_css}
}}

*,*::before,*::after{{box-sizing:border-box}}
html,body,[class*="css"]{{font-family:'Space Grotesk',sans-serif!important;background:var(--bg)!important;color:var(--text)!important}}
.stApp{{background:var(--bg)!important}}
.block-container{{padding:0 1.5rem 3rem 1.5rem!important;max-width:1520px}}
#MainMenu,footer,header,[data-testid="stToolbar"],.stDeployButton{{display:none!important;visibility:hidden!important}}
::-webkit-scrollbar{{width:5px;height:5px}}
::-webkit-scrollbar-track{{background:var(--bg)}}
::-webkit-scrollbar-thumb{{background:var(--border2);border-radius:3px}}
::-webkit-scrollbar-thumb:hover{{background:var(--blue)}}

/* ── BG EFFECTS ── */
{bg_effects}
@keyframes bgPulse{{0%{{opacity:.5}}100%{{opacity:1}}}}

/* Particle grid */
.stApp::after{{
  content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
  background-image:
    linear-gradient(rgba(59,130,246,.03) 1px,transparent 1px),
    linear-gradient(90deg,rgba(59,130,246,.03) 1px,transparent 1px);
  background-size:44px 44px;
  animation:gridDrift 20s linear infinite}}
@keyframes gridDrift{{0%{{transform:translateY(0)}}100%{{transform:translateY(44px)}}}}

/* ── KEYFRAMES ── */
@keyframes fadeDown {{from{{opacity:0;transform:translateY(-20px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes fadeUp   {{from{{opacity:0;transform:translateY(20px)}} to{{opacity:1;transform:translateY(0)}}}}
@keyframes fadeIn   {{from{{opacity:0}}to{{opacity:1}}}}
@keyframes slideIn  {{from{{opacity:0;transform:translateX(-20px)}}to{{opacity:1;transform:translateX(0)}}}}
@keyframes slideRight{{from{{opacity:0;transform:translateX(20px)}} to{{opacity:1;transform:translateX(0)}}}}
@keyframes scaleIn  {{from{{opacity:0;transform:scale(.9)}} to{{opacity:1;transform:scale(1)}}}}
@keyframes popIn    {{from{{opacity:0;transform:scale(.7)}}to{{opacity:1;transform:scale(1)}}}}
@keyframes barGrow  {{from{{width:0!important}}}}
@keyframes spin     {{to{{transform:rotate(360deg)}}}}
@keyframes spinSlow {{to{{transform:rotate(360deg)}}}}
@keyframes pulseDot {{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.3;transform:scale(.65)}}}}
@keyframes glowRing {{0%,100%{{box-shadow:0 0 20px rgba(59,130,246,.25),0 0 50px rgba(59,130,246,.1)}}
                     50%{{box-shadow:0 0 35px rgba(59,130,246,.5),0 0 80px rgba(59,130,246,.2)}}}}
@keyframes neonPulse{{0%,100%{{text-shadow:0 0 8px rgba(96,165,250,.6)}}
                     50%{{text-shadow:0 0 20px rgba(96,165,250,1),0 0 40px rgba(6,182,212,.5)}}}}
@keyframes scanLine {{0%{{top:-2px}}100%{{top:100%}}}}
@keyframes typewrite{{from{{width:0}}to{{width:100%}}}}
@keyframes dash     {{to{{stroke-dashoffset:0}}}}
@keyframes countUp  {{from{{opacity:0;transform:scale(.4) translateY(20px)}}to{{opacity:1;transform:scale(1) translateY(0)}}}}
@keyframes shimmer  {{0%{{background-position:-600px 0}}100%{{background-position:600px 0}}}}
@keyframes float    {{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-6px)}}}}
@keyframes orbit    {{0%{{transform:rotate(0deg) translateX(28px) rotate(0deg)}}
                     100%{{transform:rotate(360deg) translateX(28px) rotate(-360deg)}}}}

/* ── HERO ── */
.hero-wrap{{
  position:relative;z-index:10;padding:1.8rem 0 1.6rem;
  border-bottom:1px solid var(--border);margin-bottom:2rem;
  display:flex;align-items:center;justify-content:space-between;
  animation:fadeDown .7s cubic-bezier(.22,1,.36,1) both}}
.hero-logo{{display:flex;align-items:center;gap:1.2rem}}
.hero-icon-outer{{position:relative;width:68px;height:68px;animation:float 4s ease-in-out infinite}}
.hero-ring1{{
  position:absolute;inset:-8px;border-radius:50%;
  border:1.5px solid transparent;
  background:linear-gradient(var(--bg),var(--bg)) padding-box,
             conic-gradient(from 0deg,var(--blue),var(--purple),var(--cyan),var(--blue)) border-box;
  animation:spin 6s linear infinite}}
.hero-ring2{{
  position:absolute;inset:-16px;border-radius:50%;
  border:1px solid transparent;
  background:linear-gradient(var(--bg),var(--bg)) padding-box,
             conic-gradient(from 180deg,var(--pink),var(--blue),var(--cyan),var(--pink)) border-box;
  animation:spin 10s linear infinite reverse;opacity:.4}}
.hero-orbit-dot{{
  position:absolute;top:50%;left:50%;width:7px;height:7px;
  margin:-3.5px 0 0 -3.5px;border-radius:50%;
  background:var(--cyan);box-shadow:0 0 10px var(--cyan);
  animation:orbit 3s linear infinite}}
.hero-core{{
  width:68px;height:68px;border-radius:18px;
  background:linear-gradient(135deg,#1d4ed8,var(--blue),var(--cyan));
  display:flex;align-items:center;justify-content:center;font-size:1.8rem;
  box-shadow:0 0 40px rgba(59,130,246,.5);animation:glowRing 4s ease infinite}}
.hero-name{{
  font-size:2.2rem;font-weight:700;letter-spacing:-.04em;line-height:1;
  background:linear-gradient(135deg,var(--bright) 30%,var(--blue2),var(--cyan));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  animation:neonPulse 4s ease infinite}}
.hero-tagline{{
  font-family:'JetBrains Mono',monospace;font-size:.62rem;color:var(--dim);
  letter-spacing:.22em;text-transform:uppercase;margin-top:5px}}
.hero-badges{{display:flex;gap:.5rem;margin-top:8px}}
.hbadge{{
  font-family:'JetBrains Mono',monospace;font-size:.58rem;
  padding:2px 8px;border-radius:100px;letter-spacing:.08em;text-transform:uppercase}}
.hb-blue{{background:rgba(59,130,246,.12);color:var(--blue2);border:1px solid rgba(59,130,246,.25)}}
.hb-green{{background:rgba(16,185,129,.12);color:var(--green2);border:1px solid rgba(16,185,129,.25)}}
.hb-purple{{background:rgba(139,92,246,.12);color:#a78bfa;border:1px solid rgba(139,92,246,.25)}}
.hb-orange{{background:rgba(249,115,22,.12);color:#fb923c;border:1px solid rgba(249,115,22,.25)}}
.hero-right{{display:flex;align-items:center;gap:.7rem}}
.live-badge{{
  display:flex;align-items:center;gap:7px;
  background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.2);
  padding:7px 16px;border-radius:100px;
  font-family:'JetBrains Mono',monospace;font-size:.68rem;color:var(--green2);
  animation:fadeIn 1.2s ease .5s both}}
.pulse-dot{{
  width:8px;height:8px;border-radius:50%;background:var(--green2);
  box-shadow:0 0 10px var(--green);animation:pulseDot 2s infinite}}
.time-badge{{
  font-family:'JetBrains Mono',monospace;font-size:.68rem;color:var(--dim);
  background:var(--surf);border:1px solid var(--border);border-radius:9px;padding:7px 14px;
  position:relative;overflow:hidden}}
.time-badge::after{{
  content:'';position:absolute;top:0;left:-100%;width:60%;height:100%;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.04),transparent);
  animation:shimmer 3s infinite 2s}}

/* ── THEME TOGGLE ── */
.theme-toggle{{
  display:flex;align-items:center;gap:8px;
  background:var(--surf);border:1px solid var(--border);border-radius:100px;
  padding:5px 12px;cursor:pointer;font-family:'JetBrains Mono',monospace;
  font-size:.68rem;color:var(--text2);transition:all .2s;
  user-select:none}}
.theme-toggle:hover{{border-color:var(--blue);color:var(--blue2)}}

/* ── SCAN LINE EFFECT on hero ── */
.hero-wrap::before{{
  content:'';position:absolute;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(59,130,246,.6),transparent);
  animation:scanLine 6s linear infinite;z-index:1}}

/* ── SIDEBAR ── */
[data-testid="stSidebar"]{{background:var(--bg2)!important;border-right:1px solid var(--border)!important}}
[data-testid="stSidebar"] .block-container{{padding:1.2rem .8rem!important}}
.sb-sec{{
  font-family:'JetBrains Mono',monospace;font-size:.58rem;color:var(--dim);
  letter-spacing:.22em;text-transform:uppercase;margin:1.2rem 0 .6rem;
  padding-bottom:5px;border-bottom:1px solid var(--border)}}
.sb-host{{font-family:'JetBrains Mono',monospace;font-size:.73rem;line-height:2.2;color:var(--text2)}}
.sb-host span{{color:var(--bright)}}
.rbar-wrap{{margin-bottom:12px}}
.rbar-lbl{{
  font-family:'JetBrains Mono',monospace;font-size:.68rem;color:var(--text2);
  display:flex;justify-content:space-between;margin-bottom:5px}}
.rbar-track{{height:4px;background:var(--bg3);border-radius:2px;overflow:hidden}}
.rbar-fill{{height:100%;border-radius:2px;animation:barGrow 1.2s cubic-bezier(.22,1,.36,1) both}}
.rbar-cpu {{background:linear-gradient(90deg,var(--blue),var(--cyan))}}
.rbar-ram {{background:linear-gradient(90deg,var(--green),var(--cyan))}}
.rbar-disk{{background:linear-gradient(90deg,var(--purple),var(--pink))}}
.rbar-net {{background:linear-gradient(90deg,var(--orange),var(--amber))}}

/* ── CARDS ── */
.card{{
  background:linear-gradient(145deg,var(--surf),var(--surf2));
  border:1px solid var(--border);border-radius:16px;
  padding:1.3rem 1.5rem;margin-bottom:1rem;
  position:relative;overflow:hidden;
  transition:border-color .3s,box-shadow .3s,transform .25s;
  animation:scaleIn .5s cubic-bezier(.22,1,.36,1) both}}
.card:hover{{
  border-color:rgba(59,130,246,.4);
  box-shadow:0 12px 40px rgba(59,130,246,.15),0 0 0 1px rgba(59,130,246,.08) inset;
  transform:translateY(-3px)}}
.card-gb::after{{content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse 70% 90% at 0% 0%,rgba(59,130,246,.09),transparent);pointer-events:none}}
.card-gg::after{{content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse 70% 90% at 0% 0%,rgba(16,185,129,.08),transparent);pointer-events:none}}
.card-gp::after{{content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse 70% 90% at 0% 0%,rgba(139,92,246,.08),transparent);pointer-events:none}}
.card-ga::after{{content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse 70% 90% at 0% 0%,rgba(245,158,11,.07),transparent);pointer-events:none}}
.ctbar{{position:absolute;top:0;left:0;right:0;height:2px;border-radius:16px 16px 0 0}}
.tb-blue  {{background:linear-gradient(90deg,var(--blue),var(--cyan),transparent)}}
.tb-green {{background:linear-gradient(90deg,var(--green),var(--cyan),transparent)}}
.tb-purple{{background:linear-gradient(90deg,var(--purple),var(--pink),transparent)}}
.tb-amber {{background:linear-gradient(90deg,var(--amber),var(--orange),transparent)}}
.tb-red   {{background:linear-gradient(90deg,var(--red),var(--pink),transparent)}}
.clabel{{
  font-family:'JetBrains Mono',monospace;font-size:.6rem;color:var(--dim);
  letter-spacing:.2em;text-transform:uppercase;margin-bottom:6px}}
.cvalue{{
  font-family:'JetBrains Mono',monospace;font-size:.95rem;color:var(--bright);
  font-weight:500;word-break:break-all;line-height:1.6}}
.cval-xl{{
  font-family:'JetBrains Mono',monospace;font-size:1.9rem;font-weight:700;
  background:linear-gradient(135deg,var(--blue2),var(--cyan));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.2;
  animation:countUp .7s cubic-bezier(.22,1,.36,1) both}}
.cval-green{{
  font-family:'JetBrains Mono',monospace;font-size:1.9rem;font-weight:700;
  background:linear-gradient(135deg,var(--green2),var(--cyan));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  animation:countUp .7s ease both}}
.cval-purple{{
  font-family:'JetBrains Mono',monospace;font-size:1.9rem;font-weight:700;
  background:linear-gradient(135deg,#a78bfa,var(--pink));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  animation:countUp .7s ease both}}

/* ── TILES ── */
.tile{{
  background:linear-gradient(145deg,var(--surf),var(--surf2));
  border:1px solid var(--border);border-radius:14px;
  padding:1.2rem 1rem;text-align:center;
  transition:all .25s;animation:fadeUp .6s cubic-bezier(.22,1,.36,1) both;
  position:relative;overflow:hidden}}
.tile::before{{
  content:'';position:absolute;bottom:0;left:0;right:0;height:70%;
  background:radial-gradient(ellipse 80% 100% at 50% 100%,rgba(59,130,246,.06),transparent);
  pointer-events:none}}
.tile:hover{{
  transform:translateY(-4px);
  box-shadow:0 16px 40px rgba(59,130,246,.18);
  border-color:rgba(59,130,246,.35)}}
.tile-val{{font-family:'JetBrains Mono',monospace;font-size:1.6rem;font-weight:700;animation:countUp .6s ease both}}
.tile-lbl{{font-size:.68rem;color:var(--dim);text-transform:uppercase;letter-spacing:.12em;margin-top:4px}}
.tile-sub{{font-family:'JetBrains Mono',monospace;font-size:.7rem;color:var(--text2);margin-top:3px}}

/* ── SECTION HEADS ── */
.sec{{
  display:flex;align-items:center;gap:.9rem;margin:2.2rem 0 1.1rem;
  animation:fadeIn .6s ease both}}
.sec-icon{{font-size:1rem}}
.sec-txt{{
  font-family:'JetBrains Mono',monospace;font-size:.63rem;color:var(--text2);
  letter-spacing:.22em;text-transform:uppercase;white-space:nowrap}}
.sec-line{{flex:1;height:1px;background:linear-gradient(90deg,rgba(59,130,246,.3),transparent)}}
.sec-count{{
  font-family:'JetBrains Mono',monospace;font-size:.6rem;
  background:rgba(59,130,246,.1);color:var(--blue2);
  border:1px solid rgba(59,130,246,.2);border-radius:100px;
  padding:2px 9px;animation:popIn .5s ease both}}

/* ── TABLES ── */
.wifi-wrap{{
  background:var(--surf);border:1px solid var(--border);border-radius:16px;
  overflow:hidden;animation:fadeUp .6s ease both;
  box-shadow:0 4px 24px rgba(0,0,0,.3)}}
.wtable{{width:100%;border-collapse:collapse;font-family:'JetBrains Mono',monospace;font-size:.78rem}}
.wtable th{{
  background:rgba(59,130,246,.06);color:var(--dim);font-size:.6rem;
  letter-spacing:.18em;text-transform:uppercase;padding:.8rem 1.1rem;
  text-align:left;border-bottom:1px solid var(--border)}}
.wtable td{{
  padding:.75rem 1.1rem;border-bottom:1px solid rgba(24,44,78,.6);
  color:var(--text);vertical-align:middle}}
.wtable tr:last-child td{{border-bottom:none}}
.wtable tr{{animation:slideIn .35s ease both}}
.wtable tr:hover td{{background:rgba(59,130,246,.05);transition:background .15s}}
.sbar-wrap{{display:flex;align-items:center;gap:9px}}
.sbar-track{{width:76px;height:5px;background:var(--bg3);border-radius:3px;overflow:hidden}}
.sbar-fill{{height:100%;border-radius:3px;animation:barGrow .8s cubic-bezier(.22,1,.36,1) both}}

/* ── BADGES ── */
.badge{{display:inline-block;padding:3px 10px;border-radius:100px;font-size:.6rem;font-weight:600;letter-spacing:.05em}}
.b-green {{background:rgba(16,185,129,.12);color:var(--green2);border:1px solid rgba(16,185,129,.25)}}
.b-red   {{background:rgba(239,68,68,.12); color:#f87171;      border:1px solid rgba(239,68,68,.25)}}
.b-blue  {{background:rgba(59,130,246,.12);color:var(--blue2); border:1px solid rgba(59,130,246,.25)}}
.b-amber {{background:rgba(245,158,11,.12);color:#fbbf24;      border:1px solid rgba(245,158,11,.25)}}
.b-purple{{background:rgba(139,92,246,.12);color:#a78bfa;      border:1px solid rgba(139,92,246,.25)}}
.b-gray  {{background:rgba(71,85,105,.12); color:var(--dim);   border:1px solid rgba(71,85,105,.25)}}
.b-cyan  {{background:rgba(6,182,212,.12); color:#67e8f9;      border:1px solid rgba(6,182,212,.25)}}
.b-orange{{background:rgba(249,115,22,.12);color:#fb923c;      border:1px solid rgba(249,115,22,.25)}}

/* ── TERMINAL ── */
.term-wrap{{
  background:#010507;border:1px solid var(--border);border-radius:14px;
  overflow:hidden;animation:fadeUp .6s ease both;
  box-shadow:0 8px 32px rgba(0,0,0,.5),0 0 0 1px rgba(59,130,246,.05) inset}}
.term-bar{{
  background:var(--bg3);border-bottom:1px solid var(--border);
  padding:.6rem 1.1rem;display:flex;align-items:center;gap:7px;
  position:relative;overflow:hidden}}
.term-bar::after{{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(59,130,246,.3),transparent)}}
.tdot{{width:11px;height:11px;border-radius:50%;flex-shrink:0}}
.term-title{{font-family:'JetBrains Mono',monospace;font-size:.68rem;color:var(--dim);margin-left:.6rem}}
.term-body{{
  padding:1.1rem 1.3rem;font-family:'JetBrains Mono',monospace;font-size:.77rem;
  color:#6ee7b7;white-space:pre-wrap;max-height:360px;overflow-y:auto;line-height:1.85;
  background:linear-gradient(180deg,#010507,#020a0e)}}
.term-cursor{{display:inline-block;width:8px;height:14px;background:var(--cyan);
  vertical-align:middle;animation:pulseDot .9s infinite;margin-left:2px}}

/* ── IP HERO ── */
.ip-hero{{
  background:linear-gradient(135deg,var(--surf),var(--surf2),rgba(11,23,48,1));
  border:1px solid var(--border);border-radius:20px;padding:2rem 2.2rem;
  margin-bottom:1.4rem;position:relative;overflow:hidden;
  animation:scaleIn .6s cubic-bezier(.22,1,.36,1) both;
  box-shadow:0 8px 40px rgba(0,0,0,.4)}}
.ip-hero::before{{
  content:'';position:absolute;top:-80px;right:-80px;width:280px;height:280px;
  border-radius:50%;background:radial-gradient(circle,rgba(59,130,246,.14),transparent);
  pointer-events:none}}
.ip-hero::after{{
  content:'';position:absolute;bottom:-50px;left:-50px;width:200px;height:200px;
  border-radius:50%;background:radial-gradient(circle,rgba(6,182,212,.09),transparent);
  pointer-events:none}}
.ip-scan-line{{
  position:absolute;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(59,130,246,.8),transparent);
  animation:scanLine 4s linear infinite}}
.ip-main{{
  font-family:'JetBrains Mono',monospace;font-size:2.6rem;font-weight:700;
  background:linear-gradient(135deg,var(--bright),var(--blue2),var(--cyan));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  letter-spacing:.02em;line-height:1.15;
  animation:countUp .8s cubic-bezier(.22,1,.36,1) both}}
.ip-country-flag{{
  display:flex;align-items:center;gap:10px;margin-top:8px;
  font-family:'JetBrains Mono',monospace;font-size:.85rem;color:var(--text2)}}
.ip-map-link{{
  font-family:'JetBrains Mono',monospace;font-size:.68rem;
  color:var(--blue2);text-decoration:none;
  border:1px solid rgba(59,130,246,.25);border-radius:6px;
  padding:3px 10px;background:rgba(59,130,246,.07);
  transition:all .2s;display:inline-block;margin-top:6px}}
.ip-map-link:hover{{background:rgba(59,130,246,.15);border-color:var(--blue)}}

/* ── INFO ROWS ── */
.info-grid{{
  background:var(--surf);border:1px solid var(--border);border-radius:14px;
  overflow:hidden;animation:fadeUp .5s ease both}}
.info-row{{
  display:flex;align-items:center;padding:.65rem 1.2rem;
  border-bottom:1px solid rgba(24,44,78,.5);
  font-family:'JetBrains Mono',monospace;font-size:.78rem;
  animation:slideIn .4s ease both;transition:background .15s}}
.info-row:last-child{{border-bottom:none}}
.info-row:hover{{background:rgba(59,130,246,.04)}}
.info-icon{{width:22px;flex-shrink:0;font-size:.85rem;margin-right:.5rem}}
.info-key{{color:var(--dim);width:140px;flex-shrink:0;font-size:.68rem;letter-spacing:.06em;text-transform:uppercase}}
.info-val{{color:var(--bright);flex:1}}
.info-copy{{
  font-size:.58rem;color:var(--dim);background:rgba(59,130,246,.08);
  border:1px solid rgba(59,130,246,.15);border-radius:4px;padding:1px 6px;
  cursor:pointer;transition:all .2s;margin-left:auto;flex-shrink:0}}
.info-copy:hover{{color:var(--blue2);border-color:var(--blue)}}

/* ── MAP ── */
.map-wrap{{
  border-radius:16px;overflow:hidden;border:1px solid var(--border);
  box-shadow:0 12px 40px rgba(59,130,246,.12);animation:fadeIn .8s ease both;
  position:relative}}
.map-wrap iframe{{display:block;filter:brightness(.5) saturate(.4) hue-rotate(180deg) contrast(1.15)}}
.map-overlay{{
  position:absolute;bottom:14px;left:14px;background:rgba(2,8,16,.9);
  backdrop-filter:blur(10px);border:1px solid var(--border);border-radius:9px;
  padding:7px 14px;font-family:'JetBrains Mono',monospace;font-size:.68rem;color:var(--text2)}}
.map-pin{{
  position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  width:16px;height:16px;border-radius:50%;
  background:var(--blue);box-shadow:0 0 0 4px rgba(59,130,246,.3),0 0 20px rgba(59,130,246,.6);
  animation:pulseDot 2s infinite}}

/* ── WHOIS ── */
.whois-wrap{{background:var(--surf);border:1px solid var(--border);border-radius:14px;overflow:hidden}}
.whois-row{{
  display:flex;padding:.55rem 1.1rem;border-bottom:1px solid rgba(24,44,78,.5);
  font-family:'JetBrains Mono',monospace;font-size:.75rem;
  animation:fadeIn .3s ease both;transition:background .15s}}
.whois-row:last-child{{border-bottom:none}}
.whois-row:hover{{background:rgba(59,130,246,.04)}}
.whois-key{{color:var(--blue2);width:220px;flex-shrink:0;font-size:.7rem}}
.whois-val{{color:var(--text)}}

/* ── THREAT PANEL ── */
.threat-panel{{
  background:linear-gradient(135deg,rgba(239,68,68,.06),rgba(249,115,22,.04));
  border:1px solid rgba(239,68,68,.2);border-radius:14px;padding:1.2rem 1.5rem;
  margin:1rem 0;animation:scaleIn .5s ease both}}
.threat-item{{
  display:flex;align-items:center;gap:.8rem;padding:.5rem 0;
  border-bottom:1px solid rgba(239,68,68,.1);font-family:'JetBrains Mono',monospace;font-size:.78rem}}
.threat-item:last-child{{border-bottom:none}}
.threat-icon{{font-size:1.1rem;flex-shrink:0}}
.threat-label{{color:var(--text2);flex:1}}
.threat-status-ok{{color:var(--green2)}}
.threat-status-bad{{color:#f87171}}

/* ── GAUGE ── */
.gauge-val{{
  font-family:'JetBrains Mono',monospace;font-size:3.2rem;font-weight:700;
  background:linear-gradient(135deg,var(--green2),var(--cyan));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  animation:countUp .9s cubic-bezier(.22,1,.36,1) both}}
.gauge-unit{{font-family:'JetBrains Mono',monospace;font-size:.88rem;color:var(--dim)}}

/* ── SPEED METER ── */
.speed-ring{{
  width:140px;height:140px;border-radius:50%;
  background:conic-gradient(var(--green) 0%,var(--cyan) 60%,var(--bg3) 60%);
  display:flex;align-items:center;justify-content:center;
  position:relative;margin:0 auto;
  box-shadow:0 0 30px rgba(16,185,129,.3)}}
.speed-ring-inner{{
  width:110px;height:110px;border-radius:50%;
  background:var(--surf);display:flex;flex-direction:column;
  align-items:center;justify-content:center}}

/* ── PROGRESS ── */
.stProgress > div > div{{background:linear-gradient(90deg,var(--blue),var(--cyan))}}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"]{{
  background:transparent!important;
  border-bottom:1px solid var(--border)!important;gap:0!important}}
.stTabs [data-baseweb="tab"]{{
  font-family:'Space Grotesk',sans-serif!important;font-size:.82rem!important;
  font-weight:600!important;color:var(--dim)!important;background:transparent!important;
  border:none!important;padding:.75rem 1.2rem!important;letter-spacing:.02em!important;
  transition:color .2s!important;position:relative!important}}
.stTabs [aria-selected="true"]{{color:var(--bright)!important;border-bottom:2px solid var(--blue)!important}}
.stTabs [aria-selected="true"]::after{{
  content:'';position:absolute;bottom:0;left:20%;right:20%;height:1px;
  background:var(--cyan);filter:blur(3px)}}
.stTabs [data-baseweb="tab"]:hover{{color:var(--text)!important}}

/* ── BUTTONS ── */
.stButton>button{{
  background:linear-gradient(135deg,rgba(59,130,246,.1),rgba(139,92,246,.08))!important;
  border:1px solid rgba(59,130,246,.28)!important;color:var(--blue2)!important;
  font-family:'JetBrains Mono',monospace!important;font-size:.77rem!important;
  letter-spacing:.05em!important;border-radius:10px!important;
  transition:all .2s!important;position:relative!important;overflow:hidden!important}}
.stButton>button::after{{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,rgba(59,130,246,.0),rgba(59,130,246,.12));
  opacity:0;transition:opacity .2s}}
.stButton>button:hover{{
  background:linear-gradient(135deg,rgba(59,130,246,.2),rgba(139,92,246,.15))!important;
  border-color:var(--blue)!important;
  box-shadow:0 0 24px rgba(59,130,246,.3),0 0 8px rgba(59,130,246,.1) inset!important;
  transform:translateY(-2px)!important}}
.stButton>button:active{{transform:translateY(0)!important}}

/* ── INPUTS ── */
.stTextInput input,.stSelectbox>div>div,.stTextArea textarea{{
  background:var(--surf)!important;border:1px solid var(--border)!important;
  border-radius:10px!important;color:var(--text)!important;
  font-family:'JetBrains Mono',monospace!important;font-size:.82rem!important;
  transition:border-color .2s,box-shadow .2s!important}}
.stTextInput input:focus,.stTextArea textarea:focus{{
  border-color:var(--blue)!important;
  box-shadow:0 0 0 3px rgba(59,130,246,.15)!important}}
label{{color:var(--text2)!important;font-size:.78rem!important}}

/* ── INFO BOX ── */
.info-box{{
  border-radius:10px;padding:.7rem 1rem;margin-bottom:1rem;
  font-family:'JetBrains Mono',monospace;font-size:.73rem;
  animation:fadeIn .5s ease both}}
.info-box-blue{{
  background:rgba(59,130,246,.07);border:1px solid rgba(59,130,246,.2);color:var(--blue2)}}
.info-box-red{{
  background:rgba(239,68,68,.07);border:1px solid rgba(239,68,68,.2);color:#f87171}}
.info-box-green{{
  background:rgba(16,185,129,.07);border:1px solid rgba(16,185,129,.2);color:var(--green2)}}
.info-box-amber{{
  background:rgba(245,158,11,.07);border:1px solid rgba(245,158,11,.2);color:#fbbf24}}

/* ── STAGGER ── */
.card:nth-child(1){{animation-delay:.04s}}.card:nth-child(2){{animation-delay:.09s}}
.card:nth-child(3){{animation-delay:.14s}}.card:nth-child(4){{animation-delay:.19s}}
.tile:nth-child(1){{animation-delay:.05s}}.tile:nth-child(2){{animation-delay:.1s}}
.tile:nth-child(3){{animation-delay:.15s}}.tile:nth-child(4){{animation-delay:.2s}}
.info-row:nth-child(odd) {{animation-delay:.04s}}
.info-row:nth-child(even){{animation-delay:.08s}}
.wtable tr:nth-child(1){{animation-delay:.03s}}.wtable tr:nth-child(2){{animation-delay:.06s}}
.wtable tr:nth-child(3){{animation-delay:.09s}}.wtable tr:nth-child(4){{animation-delay:.12s}}
.wtable tr:nth-child(5){{animation-delay:.15s}}.wtable tr:nth-child(6){{animation-delay:.18s}}
.stAlert{{background:var(--surf)!important;border:1px solid var(--border)!important;border-radius:11px!important}}

/* ── Ping Gauge ── */
.ping-gauge{{
  width:100%;height:8px;background:var(--bg3);border-radius:4px;
  overflow:hidden;margin-top:6px}}
.ping-fill{{height:100%;border-radius:4px;animation:barGrow 1s ease both}}

/* ── Network Sparkline ── */
.sparkline-wrap{{
  background:var(--surf);border:1px solid var(--border);border-radius:14px;
  padding:1.2rem 1.4rem;margin-bottom:1rem;animation:fadeUp .5s ease both}}
.sparkline-title{{
  font-family:'JetBrains Mono',monospace;font-size:.62rem;color:var(--dim);
  letter-spacing:.18em;text-transform:uppercase;margin-bottom:.7rem}}

/* ── Whois panel ── */
.whois-panel{{
  background:linear-gradient(135deg,var(--surf),var(--surf2));
  border:1px solid var(--border);border-radius:16px;overflow:hidden;
  animation:fadeUp .6s ease both}}
.whois-header{{
  background:rgba(59,130,246,.06);border-bottom:1px solid var(--border);
  padding:.8rem 1.2rem;font-family:'JetBrains Mono',monospace;
  font-size:.62rem;color:var(--dim);letter-spacing:.18em;text-transform:uppercase;
  display:flex;align-items:center;justify-content:space-between}}

/* ── NEW: Latency histogram bars ── */
.lat-bar-wrap{{display:flex;align-items:flex-end;gap:3px;height:60px;padding:4px 0}}
.lat-bar{{
  flex:1;border-radius:3px 3px 0 0;min-height:4px;
  background:linear-gradient(180deg,var(--blue),var(--cyan));
  transition:opacity .2s}}
.lat-bar:hover{{opacity:.7}}

/* ── NEW: Export button ── */
.export-btn{{
  font-family:'JetBrains Mono',monospace;font-size:.62rem;
  background:rgba(16,185,129,.08);color:var(--green2);
  border:1px solid rgba(16,185,129,.2);border-radius:7px;
  padding:4px 12px;cursor:pointer;transition:all .2s;display:inline-block;text-decoration:none}}
.export-btn:hover{{background:rgba(16,185,129,.15);border-color:var(--green)}}

/* ── NEW: Hostname result card ── */
.host-card{{
  background:linear-gradient(135deg,var(--surf),var(--surf2));
  border:1px solid var(--border);border-radius:14px;
  padding:1.1rem 1.4rem;margin-bottom:.6rem;
  animation:fadeUp .4s ease both;transition:border-color .2s}}
.host-card:hover{{border-color:rgba(59,130,246,.3)}}

/* ── NEW: Anomaly alert ── */
.anomaly-alert{{
  background:linear-gradient(135deg,rgba(239,68,68,.08),rgba(249,115,22,.06));
  border:1px solid rgba(239,68,68,.3);border-radius:12px;
  padding:1rem 1.3rem;margin-bottom:1rem;animation:scaleIn .4s ease both;
  display:flex;align-items:center;gap:1rem}}
.anomaly-icon{{font-size:1.4rem;flex-shrink:0}}
.anomaly-body{{flex:1;font-family:'JetBrains Mono',monospace;font-size:.75rem}}
.anomaly-title{{color:#f87171;font-weight:600;margin-bottom:3px}}
.anomaly-detail{{color:var(--text2)}}

/* ── NEW: CPU core bars ── */
.core-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(80px,1fr));gap:6px;margin-top:8px}}
.core-item{{text-align:center}}
.core-lbl{{font-family:'JetBrains Mono',monospace;font-size:.55rem;color:var(--dim);margin-bottom:3px}}
.core-track{{height:40px;width:100%;background:var(--bg3);border-radius:3px;
  position:relative;overflow:hidden;display:flex;align-items:flex-end}}
.core-fill{{width:100%;border-radius:3px;background:linear-gradient(180deg,var(--blue),var(--cyan));animation:barGrow .8s ease both}}
.core-pct{{font-family:'JetBrains Mono',monospace;font-size:.55rem;color:var(--blue2);margin-top:3px}}

/* ── NOTICE BOX for network-limited features ── */
.net-notice{{
  background:rgba(245,158,11,.07);border:1px solid rgba(245,158,11,.25);
  border-radius:10px;padding:.75rem 1rem;margin-bottom:.8rem;
  font-family:'JetBrains Mono',monospace;font-size:.72rem;color:#fbbf24;
  display:flex;align-items:center;gap:.6rem}}

/* ── LIVE MONITOR status bar ── */
.monitor-status-bar{{
  display:flex;align-items:center;gap:1rem;
  background:var(--surf);border:1px solid var(--border);border-radius:12px;
  padding:.8rem 1.2rem;margin-bottom:1.2rem;
  font-family:'JetBrains Mono',monospace;font-size:.72rem}}
.monitor-status-running{{border-color:rgba(16,185,129,.4);background:rgba(16,185,129,.05)}}
.monitor-status-stopped{{border-color:rgba(71,85,105,.3)}}
.live-indicator{{
  display:flex;align-items:center;gap:6px;
  color:var(--green2)}}
.live-indicator-stopped{{color:var(--dim)}}
.sparkline-mini-wrap{{
  display:flex;align-items:flex-end;gap:2px;height:32px}}
.sparkline-mini-bar{{
  width:6px;border-radius:2px 2px 0 0;min-height:2px;transition:height .3s ease}}
</style>
"""

dark = st.session_state.get("dark_mode", True)
st.markdown(get_css(dark), unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════════════════════════════════════
for k in ["loc_data","wifi_data","ping_res","trace_res","dns_res","ports_res",
          "net_stats","speed_res","arp_res","route_res","threat_res","headers_res",
          "whois_res","cert_res","hostname_res","ping_history","multi_ping_res",
          "export_data"]:
    if k not in st.session_state:
        st.session_state[k] = None

# ════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ════════════════════════════════════════════════════════════════════════════
def fmt_bytes(b):
    for u in ["B","KB","MB","GB","TB"]:
        if b < 1024: return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} PB"

def sig_color(s):
    if s >= 70: return "var(--green2)"
    if s >= 40: return "var(--amber)"
    return "#f87171"

def latency_class(ms):
    if ms is None: return "b-gray","N/A"
    if ms < 30:   return "b-green",f"{ms:.0f} ms"
    if ms < 100:  return "b-amber",f"{ms:.0f} ms"
    return "b-red",f"{ms:.0f} ms"

def ping_bar_color(ms):
    if ms is None: return "var(--dim)",0
    pct = max(0, min(100, 100 - (ms / 5)))
    if ms < 30:   return "linear-gradient(90deg,var(--green),var(--cyan))", pct
    if ms < 100:  return "linear-gradient(90deg,var(--amber),var(--orange))", pct
    return "linear-gradient(90deg,var(--red),var(--pink))", max(5, pct)

def parse_ping_avg(txt):
    for p in [r"Average\s*=\s*(\d+)ms", r"rtt .+?/([\d.]+)/", r"round-trip.+?/([\d.]+)/"]:
        m = re.search(p, txt)
        if m: return float(m.group(1))
    return None

def is_private(ip):
    try: return ipaddress.ip_address(ip).is_private
    except: return False

# ════════════════════════════════════════════════════════════════════════════
# FIXED: Pure-Python ping
# ════════════════════════════════════════════════════════════════════════════
def _find_ping_binary():
    candidates = ["/bin/ping", "/usr/bin/ping", "/sbin/ping", "/usr/sbin/ping", "ping"]
    import shutil
    for c in candidates:
        if c == "ping":
            if shutil.which("ping"): return "ping"
        else:
            import os
            if os.path.isfile(c): return c
    return None

_PING_BIN = _find_ping_binary()

def ping(host, count=4):
    if _PING_BIN:
        flag = "-n" if platform.system() == "Windows" else "-c"
        try:
            r = subprocess.run([_PING_BIN, flag, str(count), host],
                               capture_output=True, text=True, timeout=25)
            return r.stdout + r.stderr
        except Exception as e:
            return f"Ping binary error: {e}\n" + _tcp_ping_report(host, count)
    else:
        return _tcp_ping_report(host, count)

def _tcp_ping_report(host, count=4):
    ports_to_try = [80, 443, 53, 22, 8080]
    try:
        ip = socket.gethostbyname(host)
    except Exception as e:
        return f"ping: {host}: Name or service not known\n"
    lines = [f"TCP-PING {host} ({ip}): {count} probes"]
    times = []
    for i in range(count):
        rtt = None
        for port in ports_to_try:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                t0 = time.time()
                s.connect((ip, port))
                rtt = (time.time() - t0) * 1000
                s.close()
                break
            except: pass
        if rtt is not None:
            times.append(rtt)
            lines.append(f"seq={i+1} ttl=64 time={rtt:.2f} ms  (port {port})")
        else:
            lines.append(f"seq={i+1} Request timeout")
    if times:
        mn, mx, avg = min(times), max(times), sum(times)/len(times)
        lines.append(f"")
        lines.append(f"--- {host} tcp-ping statistics ---")
        lines.append(f"{count} packets transmitted, {len(times)} received, "
                     f"{((count-len(times))/count*100):.0f}% packet loss")
        lines.append(f"rtt min/avg/max = {mn:.3f}/{avg:.3f}/{mx:.3f} ms")
    else:
        lines.append(f"--- {host} tcp-ping statistics ---")
        lines.append(f"{count} packets transmitted, 0 received, 100% packet loss")
        lines.append("Host unreachable or all ports filtered.")
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════════════════════
# FIXED: Traceroute
# ════════════════════════════════════════════════════════════════════════════
def _find_traceroute_binary():
    import shutil, os
    if platform.system() == "Windows":
        candidates = ["tracert"]
    else:
        candidates = ["/bin/traceroute", "/usr/bin/traceroute", "/sbin/traceroute", "traceroute"]
    for c in candidates:
        if c in ("tracert", "traceroute"):
            if shutil.which(c): return c
        else:
            if os.path.isfile(c): return c
    return None

_TRACE_BIN = _find_traceroute_binary()

def traceroute(host):
    if _TRACE_BIN:
        if platform.system() == "Windows":
            cmd = [_TRACE_BIN, host]
        else:
            cmd = [_TRACE_BIN, "-n", "-m", "20", host]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            return r.stdout + r.stderr
        except Exception as e:
            return f"Traceroute binary error: {e}\n" + _tcp_traceroute(host)
    else:
        return _tcp_traceroute(host)

def _tcp_traceroute(host, max_hops=15):
    try:
        dest_ip = socket.gethostbyname(host)
    except Exception as e:
        return f"traceroute: {host}: Name or service not known\n"
    lines = [f"traceroute to {host} ({dest_ip}), {max_hops} hops max (TCP/socket probe)"]
    for ttl in range(1, max_hops + 1):
        rtt = None
        hop_ip = "*"
        try:
            recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            recv_sock.settimeout(2)
        except:
            recv_sock = None
        try:
            send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
            send_sock.settimeout(2)
            t0 = time.time()
            try:
                send_sock.connect((dest_ip, 80))
            except socket.timeout: pass
            except OSError: pass
            rtt = (time.time() - t0) * 1000
            send_sock.close()
        except Exception: pass
        if recv_sock:
            try:
                data, addr = recv_sock.recvfrom(512)
                hop_ip = addr[0]
            except: pass
            recv_sock.close()
        if hop_ip == "*" and rtt is not None:
            hop_ip = dest_ip if ttl == max_hops else "*"
        rtt_str = f"{rtt:.1f} ms" if rtt is not None else "* * *"
        lines.append(f" {ttl:2d}  {hop_ip:<18}  {rtt_str}")
        if hop_ip == dest_ip: break
    return "\n".join(lines)


# ════════════════════════════════════════════════════════════════════════════
# GEOLOCATION
# ════════════════════════════════════════════════════════════════════════════
_GEO_APIS = [
    ("https://ipapi.co/{ip}json/",      "ipapi_co"),
    ("http://ip-api.com/json/{ip}?fields=66846719", "ipapi_com"),
    ("https://ipwho.is/{ip}",           "ipwhois"),
    ("https://freeipapi.com/api/json/{ip}", "freeipapi"),
    ("https://ip.guide/{ip}",           "ipguide"),
]

def _parse_ipapi_co(j):
    if j.get("error") or not j.get("ip"): return None
    return {"ip": j.get("ip",""), "version": j.get("version","IPv4"),
            "city": j.get("city",""), "region": j.get("region",""),
            "region_code": j.get("region_code",""), "country": j.get("country_name",""),
            "country_code": j.get("country_code",""), "continent": j.get("continent_code",""),
            "postal": j.get("postal",""), "lat": j.get("latitude"),
            "lon": j.get("longitude"), "tz": j.get("timezone",""),
            "utc": j.get("utc_offset",""), "org": j.get("org",""),
            "asn": j.get("asn",""), "currency": j.get("currency",""),
            "currency_name": j.get("currency_name",""), "calling": j.get("country_calling_code",""),
            "languages": j.get("languages",""), "in_eu": j.get("in_eu",False),
            "source": "ipapi.co"}

def _parse_ipapi_com(j):
    if j.get("status") != "success": return None
    return {"ip": j.get("query",""), "version": "IPv4",
            "city": j.get("city",""), "region": j.get("regionName",""),
            "region_code": j.get("region",""), "country": j.get("country",""),
            "country_code": j.get("countryCode",""), "continent": j.get("continent",""),
            "postal": j.get("zip",""), "lat": j.get("lat"), "lon": j.get("lon"),
            "tz": j.get("timezone",""), "utc": "", "org": j.get("isp",""),
            "asn": j.get("as",""), "currency":"", "currency_name":"",
            "calling":"", "languages":"",
            "mobile": j.get("mobile",False), "proxy": j.get("proxy",False),
            "hosting": j.get("hosting",False), "in_eu": False,
            "source": "ip-api.com"}

def _parse_ipwhois(j):
    if not j.get("success") and j.get("ip") is None: return None
    return {"ip": j.get("ip",""), "version": "IPv4",
            "city": j.get("city",""), "region": j.get("region",""),
            "region_code": j.get("region_code",""), "country": j.get("country",""),
            "country_code": j.get("country_code",""), "continent": j.get("continent",""),
            "postal": j.get("postal",""), "lat": j.get("latitude"),
            "lon": j.get("longitude"),
            "tz": j.get("timezone",{}).get("id","") if isinstance(j.get("timezone"),dict) else j.get("timezone",""),
            "utc": "", "org": j.get("org",""), "asn": j.get("asn",""),
            "currency":"", "currency_name":"", "calling":"",
            "languages":"", "in_eu": False, "source": "ipwho.is"}

def _parse_freeipapi(j):
    if not j.get("ipAddress"): return None
    return {"ip": j.get("ipAddress",""), "version": "IPv4",
            "city": j.get("cityName",""), "region": j.get("regionName",""),
            "region_code": j.get("regionCode",""), "country": j.get("countryName",""),
            "country_code": j.get("countryCode",""), "continent": "",
            "postal": j.get("zipCode",""), "lat": j.get("latitude"),
            "lon": j.get("longitude"), "tz": j.get("timeZone",""),
            "utc":"", "org":"", "asn":"",
            "currency":"", "currency_name":"", "calling":"",
            "languages":"", "in_eu":False, "source": "freeipapi.com"}

def _parse_ipguide(j):
    loc = j.get("location", {})
    asn_info = j.get("autonomous_system", {})
    if not j.get("ip"): return None
    return {"ip": j.get("ip",""), "version": "IPv4",
            "city": loc.get("city",""), "region": loc.get("state",""),
            "region_code": "", "country": loc.get("country",""),
            "country_code": loc.get("country_code",""), "continent": "",
            "postal": loc.get("postal_code",""), "lat": loc.get("latitude"),
            "lon": loc.get("longitude"), "tz": loc.get("timezone",""),
            "utc":"", "org": asn_info.get("name",""), "asn": str(asn_info.get("asn","")),
            "currency":"", "currency_name":"", "calling":"",
            "languages":"", "in_eu":False, "source": "ip.guide"}

_PARSERS = {
    "ipapi_co": _parse_ipapi_co, "ipapi_com": _parse_ipapi_com,
    "ipwhois": _parse_ipwhois, "freeipapi": _parse_freeipapi, "ipguide": _parse_ipguide,
}

def get_location(ip=""):
    errors = []
    for url_tmpl, parser_key in _GEO_APIS:
        ip_seg = ip if ip else ""
        if "ipapi.co" in url_tmpl:
            url = f"https://ipapi.co/{ip_seg + '/' if ip_seg else ''}json/"
        elif "ip-api.com" in url_tmpl:
            url = f"http://ip-api.com/json/{ip_seg}?fields=66846719"
        elif "ipwho.is" in url_tmpl:
            url = f"https://ipwho.is/{ip_seg}"
        elif "freeipapi" in url_tmpl:
            url = f"https://freeipapi.com/api/json/{ip_seg}"
        elif "ip.guide" in url_tmpl:
            url = f"https://ip.guide/{ip_seg}" if ip_seg else "https://ip.guide/me"
        else:
            url = url_tmpl.format(ip=ip_seg)
        try:
            r = requests.get(url, timeout=8, headers={"User-Agent": "NetPulse/4.0", "Accept": "application/json"})
            if r.status_code != 200:
                errors.append(f"{url}: HTTP {r.status_code}"); continue
            j = r.json()
            d = _PARSERS[parser_key](j)
            if d and d.get("ip"):
                try: d["rdns"] = socket.gethostbyaddr(d["ip"])[0]
                except: d["rdns"] = "—"
                d["is_private"] = is_private(d["ip"])
                try:
                    addr = ipaddress.ip_address(d["ip"])
                    d["version"] = "IPv6" if isinstance(addr, ipaddress.IPv6Address) else "IPv4"
                except: pass
                return d
            else:
                errors.append(f"{url}: parser returned empty")
        except requests.exceptions.ConnectionError as e:
            errors.append(f"{url}: Connection refused/blocked")
        except Exception as e:
            errors.append(f"{url}: {e}")
    local_ip = _get_local_ip()
    return {"error": "All geolocation APIs unreachable from this environment.",
            "ip": local_ip, "is_private": True, "version": "IPv4", "_tried": errors}

def _get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.254.254.254", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except: return "127.0.0.1"

def check_threat(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=proxy,hosting,mobile,org,isp", timeout=8)
        j = r.json()
        return {"proxy": j.get("proxy", False), "hosting": j.get("hosting", False),
                "mobile": j.get("mobile", False), "isp": j.get("isp", "")}
    except: return {}

def get_cert_info(hostname):
    import ssl
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
            s.settimeout(5)
            s.connect((hostname, 443))
            cert = s.getpeercert()
            subject = dict(x[0] for x in cert.get("subject", []))
            issuer  = dict(x[0] for x in cert.get("issuer", []))
            return {"cn": subject.get("commonName", "—"), "org": subject.get("organizationName", "—"),
                    "issuer": issuer.get("organizationName", "—"),
                    "not_before": cert.get("notBefore", "—"), "not_after": cert.get("notAfter", "—"),
                    "san": [v for _, v in cert.get("subjectAltName", [])],
                    "version": s.version(), "cipher": s.cipher()[0] if s.cipher() else "—"}
    except Exception as e: return {"error": str(e)}

def fetch_headers(url):
    if not url.startswith("http"): url = "https://" + url
    try:
        r = requests.get(url, timeout=10, allow_redirects=True, headers={"User-Agent": "NetPulse/4.0"})
        return {"status": r.status_code, "url": r.url, "headers": dict(r.headers),
                "redirects": len(r.history), "elapsed_ms": round(r.elapsed.total_seconds() * 1000, 1),
                "size": len(r.content)}
    except Exception as e: return {"error": str(e)}

# ════════════════════════════════════════════════════════════════════════════
# FIXED WiFi Scanner — real scan + graceful fallback with actual error info
# ════════════════════════════════════════════════════════════════════════════
def scan_wifi():
    os_n = platform.system()
    nets = []
    error_msg = None

    if os_n == "Linux":
        # Try nmcli first
        try:
            # Check if nmcli exists
            import shutil
            if not shutil.which("nmcli"):
                error_msg = "nmcli not found. Install NetworkManager: sudo apt install network-manager"
            else:
                # Try rescan (may fail silently)
                try:
                    subprocess.run(["nmcli", "dev", "wifi", "rescan"], timeout=8, capture_output=True)
                    time.sleep(1)  # Give time for rescan
                except: pass
                out = subprocess.check_output(
                    ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY,BSSID,CHAN,FREQ", "dev", "wifi"],
                    stderr=subprocess.PIPE, timeout=12).decode(errors="ignore")
                if not out.strip():
                    error_msg = "No WiFi networks returned by nmcli. Is a wireless adapter connected?"
                else:
                    seen = set()
                    for line in out.strip().splitlines():
                        p = line.split(":")
                        if len(p) >= 4:
                            ssid = p[0].strip() or "<hidden>"
                            key  = f"{ssid}|{p[3]}"
                            if key in seen: continue
                            seen.add(key)
                            nets.append({"ssid": ssid,
                                         "signal": int(p[1]) if p[1].isdigit() else 0,
                                         "security": p[2] or "OPEN",
                                         "bssid": p[3],
                                         "channel": p[4] if len(p) > 4 else "?",
                                         "freq": p[5] if len(p) > 5 else "?"})
        except subprocess.CalledProcessError as e:
            stderr_out = e.stderr.decode(errors="ignore") if e.stderr else ""
            if "No Wi-Fi device found" in stderr_out or "Error" in stderr_out:
                error_msg = f"nmcli error: {stderr_out.strip() or 'No WiFi device found. Check wireless adapter.'}"
            else:
                error_msg = f"nmcli failed: {stderr_out.strip() or str(e)}"
        except Exception as e:
            error_msg = f"WiFi scan error: {str(e)}"

        # Fallback: try iwlist
        if not nets and error_msg:
            try:
                import shutil
                iwlist_bin = shutil.which("iwlist")
                if iwlist_bin:
                    # Get wireless interfaces
                    ifaces = []
                    try:
                        addrs = psutil.net_if_addrs()
                        stats = psutil.net_if_stats()
                        for name in addrs:
                            if any(x in name.lower() for x in ["wlan","wifi","wl","ath","wlp"]):
                                ifaces.append(name)
                    except: pass
                    if not ifaces: ifaces = ["wlan0", "wlp2s0"]
                    for iface in ifaces[:2]:
                        try:
                            out = subprocess.check_output(
                                [iwlist_bin, iface, "scan"],
                                stderr=subprocess.PIPE, timeout=15).decode(errors="ignore")
                            if "Scan completed" in out or "ESSID:" in out:
                                error_msg = None  # Clear error since iwlist worked
                                for block in re.split(r'Cell \d+ -', out):
                                    if not block.strip(): continue
                                    ms = re.search(r'ESSID:"([^"]*)"', block)
                                    mg = re.search(r'Signal level=(-?\d+)\s*dBm', block)
                                    mg2 = re.search(r'Signal level=(\d+)/(\d+)', block)
                                    ma = re.search(r'Encryption key:(on|off)', block)
                                    mb = re.search(r'Address:\s*([0-9A-Fa-f:]+)', block)
                                    mc = re.search(r'Channel:(\d+)', block)
                                    mf = re.search(r'Frequency:([\d.]+)', block)
                                    if ms:
                                        ssid = ms.group(1) or "<hidden>"
                                        if mg:
                                            sig = max(0, min(100, int(mg.group(1)) + 100))
                                        elif mg2:
                                            sig = int(int(mg2.group(1)) / int(mg2.group(2)) * 100)
                                        else:
                                            sig = 50
                                        security = "WPA2" if ma and ma.group(1) == "on" else "OPEN"
                                        nets.append({
                                            "ssid": ssid,
                                            "signal": sig,
                                            "security": security,
                                            "bssid": mb.group(1) if mb else "?",
                                            "channel": mc.group(1) if mc else "?",
                                            "freq": f"{mf.group(1)} GHz" if mf else "?"
                                        })
                                if nets: break
                        except: pass
            except: pass

    elif os_n == "Windows":
        try:
            out = subprocess.check_output(["netsh", "wlan", "show", "networks", "mode=bssid"],
                stderr=subprocess.DEVNULL, timeout=12).decode(errors="ignore")
            for block in re.split(r"\n(?=SSID \d)", out):
                ms = re.search(r"SSID\s+\d+\s*:\s*(.+)", block)
                mg = re.search(r"Signal\s*:\s*(\d+)%", block)
                ma = re.search(r"Authentication\s*:\s*(.+)", block)
                mb = re.search(r"BSSID \d+\s*:\s*([0-9a-fA-F:]+)", block)
                mc = re.search(r"Channel\s*:\s*(\d+)", block)
                if ms:
                    nets.append({"ssid": ms.group(1).strip(),
                                 "signal": int(mg.group(1)) if mg else 0,
                                 "security": ma.group(1).strip() if ma else "?",
                                 "bssid": mb.group(1).strip() if mb else "?",
                                 "channel": mc.group(1) if mc else "?", "freq": "?"})
        except Exception as e:
            error_msg = f"netsh error: {str(e)}"

    elif os_n == "Darwin":
        try:
            ap = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
            out = subprocess.check_output([ap, "-s"], stderr=subprocess.DEVNULL, timeout=10).decode(errors="ignore")
            for line in out.strip().splitlines()[1:]:
                p = line.split()
                if len(p) >= 3:
                    nets.append({"ssid": p[0],
                                 "signal": abs(int(p[2])) if p[2].lstrip('-').isdigit() else 0,
                                 "security": p[-1] if len(p) > 5 else "OPEN",
                                 "bssid": p[1],
                                 "channel": p[3] if len(p) > 3 else "?", "freq": "?"})
        except Exception as e:
            error_msg = f"airport error: {str(e)}"

    return sorted(nets, key=lambda x: x["signal"], reverse=True), error_msg


def dns_lookup(host):
    out = {}
    try: out["A"]    = list(set(r[4][0] for r in socket.getaddrinfo(host, None, socket.AF_INET)))
    except: out["A"] = []
    try: out["AAAA"] = list(set(r[4][0] for r in socket.getaddrinfo(host, None, socket.AF_INET6)))
    except: out["AAAA"] = []
    try: out["PTR"]  = socket.gethostbyaddr(out["A"][0])[0] if out["A"] else "—"
    except: out["PTR"] = "—"
    try: out["fqdn"] = socket.getfqdn(host)
    except: out["fqdn"] = "—"
    try: out["mx"]   = socket.getaddrinfo(f"mail.{host}", None)
    except: out["mx"] = []
    return out

SERVICES = {
    21:"FTP", 22:"SSH", 23:"Telnet", 25:"SMTP", 53:"DNS", 80:"HTTP",
    110:"POP3", 143:"IMAP", 443:"HTTPS", 445:"SMB", 993:"IMAPS", 995:"POP3S",
    1433:"MSSQL", 1521:"Oracle", 2181:"Zookeeper", 3000:"Dev/Node", 3306:"MySQL",
    3389:"RDP", 5000:"Flask/Dev", 5432:"PostgreSQL", 5900:"VNC", 5984:"CouchDB",
    6379:"Redis", 7474:"Neo4j", 8000:"Dev", 8080:"HTTP-Alt", 8443:"HTTPS-Alt",
    8888:"Jupyter", 9000:"SonarQube", 9200:"Elasticsearch", 27017:"MongoDB",
    11211:"Memcached", 2375:"Docker", 6443:"K8s API", 9090:"Prometheus",
    9093:"Alertmanager", 9100:"Node Exporter", 3100:"Loki", 4040:"Spark UI",
    15672:"RabbitMQ", 5601:"Kibana", 16686:"Jaeger", 2379:"etcd",
}

PORT_PROFILES = {
    "Common Top-25":   [21,22,23,25,53,80,110,135,139,143,443,445,993,995,1723,3306,3389,5900,8080,8443,8000,3000,5000,6379,27017],
    "Web Servers":     [80,443,8080,8443,8000,8888,3000,5000,4000,4200,4443,9000,7000],
    "Databases":       [3306,5432,1433,1521,27017,6379,5984,9200,7474,2181,11211,2379],
    "Remote Access":   [22,23,3389,5900,5901,5902,2222,8022],
    "Dev / DevOps":    [3000,4000,5000,8000,8080,8888,9000,3001,4001,5001,8001,2375,6443,9090,9093,9100,3100,15672,5601],
    "Observability":   [9090,9093,9100,3100,16686,5601,4040,9200,5601],
    "Custom Range":    [],
}

def port_scan(host, ports, timeout=0.9):
    results = []
    try: resolved = socket.gethostbyname(host)
    except: resolved = host
    for port in ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            res = s.connect_ex((resolved, port))
            s.close()
            svc = SERVICES.get(port, "")
            if not svc:
                try: svc = socket.getservbyport(port)
                except: svc = "unknown"
            results.append({"port": port, "state": "OPEN" if res == 0 else "CLOSED", "service": svc})
        except: results.append({"port": port, "state": "ERROR", "service": SERVICES.get(port, "?")})
    return results, resolved

def net_io_sample():
    """Take a 1-second I/O sample and return delta."""
    try:
        n1 = psutil.net_io_counters()
        time.sleep(1)
        n2 = psutil.net_io_counters()
        return {
            "sent_ps":    n2.bytes_sent - n1.bytes_sent,
            "recv_ps":    n2.bytes_recv - n1.bytes_recv,
            "bytes_sent": n2.bytes_sent, "bytes_recv": n2.bytes_recv,
            "pkts_sent":  n2.packets_sent, "pkts_recv": n2.packets_recv,
            "errin":      n2.errin, "errout": n2.errout,
            "dropin":     n2.dropin, "dropout": n2.dropout,
            "ts":         datetime.now().strftime("%H:%M:%S"),
        }
    except Exception as e: return {"error": str(e)}

def net_io():
    return net_io_sample()

def get_ifaces():
    ifaces = []
    try:
        addrs = psutil.net_if_addrs(); stats = psutil.net_if_stats()
        for name, al in addrs.items():
            st_ = stats.get(name)
            ifaces.append({
                "name":  name,
                "ipv4":  next((a.address for a in al if a.family == socket.AF_INET), "—"),
                "ipv6":  next((a.address.split("%")[0] for a in al if a.family == socket.AF_INET6), "—"),
                "mac":   next((a.address for a in al if a.family == psutil.AF_LINK), "—"),
                "mask":  next((a.netmask for a in al if a.family == socket.AF_INET), "—"),
                "up":    st_.isup if st_ else False,
                "speed": st_.speed if st_ else 0,
                "mtu":   st_.mtu if st_ else 0,
            })
    except: pass
    return ifaces

def speed_test():
    try:
        start = time.time()
        r = requests.get("https://speed.cloudflare.com/__down?bytes=10000000", stream=True, timeout=20)
        dl = 0
        for chunk in r.iter_content(65536):
            dl += len(chunk)
            if time.time() - start > 10: break
        e = time.time() - start
        return {"mbps": round(dl * 8 / (e * 1e6), 2), "bytes": dl, "elapsed": round(e, 2)}
    except Exception as e: return {"error": str(e)}

def get_arp():
    try:
        if platform.system() == "Windows":
            cmd = ["arp", "-a"]
        else:
            import shutil, os
            arp_bin = shutil.which("arp") or "/usr/sbin/arp" or "/sbin/arp"
            if not arp_bin or not os.path.isfile(arp_bin):
                try:
                    with open("/proc/net/arp") as f: return f.read()
                except: pass
                return "arp binary not found. On Linux, try: ip neigh show"
            cmd = [arp_bin, "-n"]
        return subprocess.check_output(cmd, timeout=8, stderr=subprocess.DEVNULL).decode(errors="ignore")
    except Exception as e:
        try:
            import shutil
            ip_bin = shutil.which("ip")
            if ip_bin:
                return subprocess.check_output([ip_bin, "neigh", "show"],
                    timeout=8, stderr=subprocess.DEVNULL).decode(errors="ignore")
        except: pass
        return f"Error: {e}"

def get_routes():
    try:
        if platform.system() == "Windows":
            cmd = ["route", "print"]
        elif platform.system() == "Darwin":
            cmd = ["netstat", "-rn"]
        else:
            import shutil
            ip_bin = shutil.which("ip")
            if ip_bin:
                cmd = [ip_bin, "route", "show"]
            else:
                try:
                    with open("/proc/net/route") as f: return f.read()
                except: pass
                return "ip binary not found"
        return subprocess.check_output(cmd, timeout=8, stderr=subprocess.DEVNULL).decode(errors="ignore")
    except Exception as e: return f"Error: {e}"

def subnet_calc(cidr):
    try:
        net   = ipaddress.ip_network(cidr, strict=False)
        hosts = list(net.hosts())
        return {
            "network":   str(net.network_address),
            "broadcast": str(net.broadcast_address),
            "netmask":   str(net.netmask),
            "wildcard":  str(net.hostmask),
            "prefix":    net.prefixlen,
            "total":     net.num_addresses,
            "usable":    max(0, net.num_addresses - 2),
            "first":     str(hosts[0])  if hosts else str(net.network_address),
            "last":      str(hosts[-1]) if hosts else str(net.broadcast_address),
            "cls":       "A" if net.prefixlen <= 8 else "B" if net.prefixlen <= 16 else "C",
            "private":   net.is_private,
            "loopback":  net.is_loopback,
            "multicast": net.is_multicast,
        }
    except Exception as e: return {"error": str(e)}

def ip_range_expand(start_ip, end_ip):
    try:
        start = int(ipaddress.IPv4Address(start_ip))
        end   = int(ipaddress.IPv4Address(end_ip))
        if end < start: return [], "End IP must be >= Start IP"
        count = end - start + 1
        if count > 256: return [], f"Range too large ({count} IPs). Max 256."
        return [str(ipaddress.IPv4Address(i)) for i in range(start, end + 1)], None
    except Exception as e:
        return [], str(e)

def detect_network_anomalies(stats):
    anomalies = []
    if stats.get("errin", 0) + stats.get("errout", 0) > 100:
        anomalies.append(("High Error Rate", f"{stats['errin']+stats['errout']} total errors detected on interfaces"))
    if stats.get("dropin", 0) + stats.get("dropout", 0) > 500:
        anomalies.append(("Packet Loss Detected", f"{stats['dropin']+stats['dropout']} dropped packets"))
    if stats.get("recv_ps", 0) > 100 * 1024 * 1024:
        anomalies.append(("High Inbound Traffic", f"Receiving {fmt_bytes(stats['recv_ps'])}/s — possible flood or large transfer"))
    if stats.get("sent_ps", 0) > 100 * 1024 * 1024:
        anomalies.append(("High Outbound Traffic", f"Sending {fmt_bytes(stats['sent_ps'])}/s — check for data exfiltration"))
    return anomalies

def resolve_hostname(hostname):
    result = {"hostname": hostname, "ipv4": [], "ipv6": [], "fqdn": "", "aliases": [], "error": None}
    try:
        try: result["ipv4"] = list(set(r[4][0] for r in socket.getaddrinfo(hostname, None, socket.AF_INET)))
        except: pass
        try: result["ipv6"] = list(set(r[4][0] for r in socket.getaddrinfo(hostname, None, socket.AF_INET6)))
        except: pass
        try: result["fqdn"] = socket.getfqdn(hostname)
        except: pass
        ptrs = []
        for ip in result["ipv4"][:3]:
            try: ptrs.append((ip, socket.gethostbyaddr(ip)[0]))
            except: ptrs.append((ip, "—"))
        result["ptr_map"] = ptrs
        if result["ipv4"]:
            try:
                r = requests.get(f"https://ipapi.co/{result['ipv4'][0]}/json/", timeout=6,
                                  headers={"User-Agent": "NetPulse/4.0"})
                j = r.json()
                result["geo"] = {"org": j.get("org","—"), "country": j.get("country_name","—"),
                                 "city": j.get("city","—"), "asn": j.get("asn","—")}
            except: result["geo"] = {}
    except Exception as e:
        result["error"] = str(e)
    return result

def export_to_json(data, label="data"):
    try: return json.dumps(data, indent=2, default=str)
    except: return "{}"

def get_live_connections():
    """Get active TCP connections with real data."""
    try:
        conns = [c for c in psutil.net_connections(kind="inet") if c.status == "ESTABLISHED"]
        result = []
        for c in conns[:50]:
            raddr_ip   = c.raddr.ip   if c.raddr else "—"
            raddr_port = c.raddr.port if c.raddr else ""
            pid_str    = str(c.pid) if c.pid else "—"
            # Try to get process name
            proc_name = "—"
            if c.pid:
                try: proc_name = psutil.Process(c.pid).name()
                except: pass
            is_ext = not is_private(raddr_ip) if raddr_ip != "—" else False
            result.append({
                "local": f"{c.laddr.ip}:{c.laddr.port}",
                "remote": f"{raddr_ip}:{raddr_port}",
                "is_ext": is_ext,
                "pid": pid_str,
                "proc": proc_name,
            })
        return result, None
    except Exception as e:
        return [], str(e)

# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:.6rem 0 1.4rem">
      <div style="position:relative;display:inline-block;animation:float 4s ease-in-out infinite">
        <div style="font-size:2.6rem;filter:drop-shadow(0 0 16px rgba(59,130,246,.8))">⚡</div>
      </div>
      <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:1.2rem;
           background:linear-gradient(135deg,#fff,#60a5fa,#06b6d4);-webkit-background-clip:text;
           -webkit-text-fill-color:transparent;margin-top:4px;">NetPulse</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:.58rem;color:#475569;
           letter-spacing:.22em;text-transform:uppercase;margin-top:4px;">v4.0 · Intelligence</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sb-sec">🎨 Appearance</div>', unsafe_allow_html=True)
    current_dark = st.session_state.get("dark_mode", True)
    toggle_label = "☀️ Switch to Light Mode" if current_dark else "🌙 Switch to Dark Mode"
    if st.button(toggle_label, use_container_width=True, key="theme_btn"):
        st.session_state["dark_mode"] = not current_dark
        st.rerun()
    mode_label = "🌑 Dark Mode Active" if current_dark else "☀️ Light Mode Active"
    st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:.62rem;color:var(--dim);text-align:center;margin-top:4px">{mode_label}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="sb-sec">⬡ System Status</div>', unsafe_allow_html=True)
    try:
        cpu_p  = psutil.cpu_percent(interval=0.3)
        cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
        ram    = psutil.virtual_memory()
        disk   = psutil.disk_usage("/")
        net_io_sb = psutil.net_io_counters()
        st.markdown(f"""
        <div class="sb-host">
          🖥 <span>{socket.gethostname()[:18]}</span><br>
          💻 <span>{platform.system()} {platform.release()[:12]}</span><br>
          🐍 <span>Python {platform.python_version()[:6]}</span><br>
          🕐 <span>{datetime.now().strftime('%H:%M:%S')}</span>
        </div><br>
        <div class="rbar-wrap">
          <div class="rbar-lbl"><span>CPU</span><span style="color:#60a5fa">{cpu_p}%</span></div>
          <div class="rbar-track"><div class="rbar-fill rbar-cpu" style="width:{cpu_p}%"></div></div>
        </div>
        <div class="rbar-wrap">
          <div class="rbar-lbl"><span>RAM</span><span style="color:#34d399">{ram.percent}%</span></div>
          <div class="rbar-track"><div class="rbar-fill rbar-ram" style="width:{ram.percent}%"></div></div>
        </div>
        <div class="rbar-wrap">
          <div class="rbar-lbl"><span>DISK</span><span style="color:#a78bfa">{disk.percent}%</span></div>
          <div class="rbar-track"><div class="rbar-fill rbar-disk" style="width:{disk.percent}%"></div></div>
        </div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:.63rem;color:#475569;margin-top:8px;line-height:1.9">
          RAM {fmt_bytes(ram.used)}/{fmt_bytes(ram.total)}<br>
          DISK {fmt_bytes(disk.used)}/{fmt_bytes(disk.total)}<br>
          ↑ {fmt_bytes(net_io_sb.bytes_sent)} ↓ {fmt_bytes(net_io_sb.bytes_recv)}
        </div>""", unsafe_allow_html=True)

        if cpu_per_core and len(cpu_per_core) > 1:
            st.markdown('<div class="sb-sec" style="margin-top:1rem">⬡ CPU Cores</div>', unsafe_allow_html=True)
            core_items = ""
            for i, pct in enumerate(cpu_per_core[:8]):
                col = "var(--green2)" if pct < 50 else "var(--amber)" if pct < 80 else "#f87171"
                core_items += f"""
                <div class="core-item">
                  <div class="core-lbl">C{i}</div>
                  <div class="core-track">
                    <div class="core-fill" style="height:{max(4,int(pct*0.4))}px;background:linear-gradient(180deg,{col},{col}88)"></div>
                  </div>
                  <div class="core-pct">{int(pct)}%</div>
                </div>"""
            st.markdown(f'<div class="core-grid">{core_items}</div>', unsafe_allow_html=True)
    except: pass

    st.markdown("---")
    st.markdown('<div class="sb-sec">⬡ Quick Links</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;font-size:.7rem;line-height:2.4;color:#475569">
      🌐 <a href="https://ipapi.co" target="_blank" style="color:#60a5fa;text-decoration:none">ipapi.co</a><br>
      🔍 <a href="https://shodan.io" target="_blank" style="color:#60a5fa;text-decoration:none">Shodan</a><br>
      🛡 <a href="https://virustotal.com" target="_blank" style="color:#60a5fa;text-decoration:none">VirusTotal</a><br>
      📡 <a href="https://bgp.he.net" target="_blank" style="color:#60a5fa;text-decoration:none">BGP Toolkit</a><br>
      🗺 <a href="https://mxtoolbox.com" target="_blank" style="color:#60a5fa;text-decoration:none">MX Toolbox</a><br>
      🔎 <a href="https://dnschecker.org" target="_blank" style="color:#60a5fa;text-decoration:none">DNS Checker</a><br>
      🔒 <a href="https://crt.sh" target="_blank" style="color:#60a5fa;text-decoration:none">SSL Cert Search</a><br>
      📊 <a href="https://iplocation.net" target="_blank" style="color:#60a5fa;text-decoration:none">IP Location</a>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:.58rem;
         color:#1e3a5f;text-align:center;line-height:2;">
         ⚠ ETHICAL USE ONLY<br>Authorised networks only.</div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════════════════════════
dark_now = st.session_state.get("dark_mode", True)
theme_icon = "☀️" if dark_now else "🌙"
theme_label_short = "Light" if dark_now else "Dark"

st.markdown(f"""
<div class="hero-wrap">
  <div class="hero-logo">
    <div class="hero-icon-outer">
      <div class="hero-ring1"></div>
      <div class="hero-ring2"></div>
      <div class="hero-orbit-dot"></div>
      <div class="hero-core">⚡</div>
    </div>
    <div>
      <div class="hero-name">NetPulse</div>
      <div class="hero-tagline">Advanced Network Intelligence Dashboard · v4.0</div>
      <div class="hero-badges">
        <span class="hbadge hb-blue">Geo · Multi-API</span>
        <span class="hbadge hb-green">SSL Inspector</span>
        <span class="hbadge hb-purple">IP Range Scan</span>
        <span class="hbadge hb-orange">Hostname Intel</span>
        <span class="hbadge hb-green">{theme_icon} {theme_label_short} Mode</span>
      </div>
    </div>
  </div>
  <div class="hero-right">
    <div class="time-badge">{datetime.now().strftime('%d %b %Y · %H:%M')}</div>
    <div class="live-badge"><span class="pulse-dot"></span>Live</div>
  </div>
</div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🌐  IP & Location",
    "📶  WiFi Scanner",
    "🔧  Diagnostics",
    "🔍  Port Scanner",
    "📊  Live Monitor",
    "🛠  Tools",
    "🔒  SSL & Security",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — IP & LOCATION
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="info-box info-box-blue">ℹ IP geolocation uses 5 APIs in sequence (ipapi.co → ip-api.com → ipwho.is → freeipapi.com → ip.guide). VPN/proxy exit nodes show their own location.</div>', unsafe_allow_html=True)

    ci, cb1, cb2, cb3 = st.columns([4, 1, 1, 1])
    with ci:
        custom_ip = st.text_input("IP", placeholder="Leave blank for your own public IP · or type any IPv4/IPv6",
                                   label_visibility="collapsed")
    with cb1: run_loc    = st.button("🔍 Geolocate", use_container_width=True)
    with cb2: run_threat = st.button("🛡 Threat Check", use_container_width=True)
    with cb3: run_clear  = st.button("✕ Clear", use_container_width=True)

    if run_clear:
        st.session_state["loc_data"]   = None
        st.session_state["threat_res"] = None
        st.rerun()

    if run_loc:
        with st.spinner("Fetching geolocation data (trying multiple APIs)..."):
            d = get_location(custom_ip.strip())
        st.session_state["loc_data"] = d

    if run_threat:
        ip_chk = custom_ip.strip() or (st.session_state.get("loc_data") or {}).get("ip", "")
        if ip_chk:
            with st.spinner("Checking proxy/VPN/hosting flags..."):
                st.session_state["threat_res"] = check_threat(ip_chk)

    d      = st.session_state.get("loc_data")
    threat = st.session_state.get("threat_res")

    if d:
        if "error" in d:
            st.markdown(f"""
            <div class="anomaly-alert">
              <span class="anomaly-icon">🌐</span>
              <div class="anomaly-body">
                <div class="anomaly-title">Geolocation Unavailable</div>
                <div class="anomaly-detail">{d['error']}</div>
              </div>
            </div>""", unsafe_allow_html=True)
            if d.get("ip"):
                st.markdown(f"""
                <div class="card card-gb">
                  <div class="ctbar tb-blue"></div>
                  <div class="clabel">Local / Detected IP</div>
                  <div class="cvalue" style="color:var(--blue2);font-size:1.4rem">{d['ip']}</div>
                  <div style="margin-top:8px">
                    <span class="badge b-amber">PRIVATE / LOCAL</span>
                    <span class="badge b-gray" style="margin-left:6px">{d.get('version','IPv4')}</span>
                  </div>
                </div>""", unsafe_allow_html=True)
            if d.get("_tried"):
                with st.expander("🔧 API Attempts Debug"):
                    for t in d["_tried"]:
                        st.code(t)
        else:
            lat = d.get("lat"); lon = d.get("lon")
            cc  = d.get("country_code", "").lower()
            is_priv = d.get("is_private", False)
            priv_b  = '<span class="badge b-amber">PRIVATE</span>' if is_priv else '<span class="badge b-blue">PUBLIC</span>'
            ver_b   = f'<span class="badge b-cyan">{d.get("version","IPv4")}</span>'
            src_b   = f'<span class="badge b-gray">via {d.get("source","")}</span>'
            threat_html = ""
            if threat:
                flags = []
                if threat.get("proxy"):   flags.append('<span class="badge b-red">⚠ PROXY/VPN</span>')
                if threat.get("hosting"): flags.append('<span class="badge b-amber">🖥 HOSTING</span>')
                if threat.get("mobile"):  flags.append('<span class="badge b-purple">📱 MOBILE</span>')
                if not flags:             flags.append('<span class="badge b-green">✓ CLEAN</span>')
                threat_html = " ".join(flags)
            flag_img = f'<img src="https://flagcdn.com/24x18/{cc}.png" style="border-radius:3px;vertical-align:middle" />' if cc else ""
            location_str = ", ".join(filter(None, [d.get("city",""), d.get("region",""), d.get("country","")]))
            gmap_url = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else "#"
            osm_url  = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=10" if lat and lon else "#"

            if threat and (threat.get("proxy") or threat.get("hosting")):
                proxy_type = "Proxy/VPN" if threat.get("proxy") else "Hosting/Datacenter"
                st.markdown(f"""
                <div class="anomaly-alert">
                  <span class="anomaly-icon">⚠️</span>
                  <div class="anomaly-body">
                    <div class="anomaly-title">{proxy_type} Detected</div>
                    <div class="anomaly-detail">This IP is flagged as a {proxy_type.lower()} endpoint. ISP: {threat.get("isp","—")}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

            st.markdown(f"""
            <div class="ip-hero">
              <div class="ip-scan-line"></div>
              <div class="ctbar tb-blue"></div>
              <div class="clabel">DETECTED / QUERIED IP ADDRESS</div>
              <div class="ip-main">{d.get("ip","—")}</div>
              <div class="ip-country-flag">{flag_img} {location_str or "—"}</div>
              <div style="margin-top:10px;display:flex;gap:8px;align-items:center;flex-wrap:wrap">
                {priv_b} {ver_b} {src_b} {threat_html}
              </div>
              <div style="margin-top:10px;display:flex;gap:8px">
                <a href="{gmap_url}" target="_blank" class="ip-map-link">🗺 Google Maps</a>
                <a href="{osm_url}"  target="_blank" class="ip-map-link">🌍 OpenStreetMap</a>
              </div>
            </div>""", unsafe_allow_html=True)

            cl, cr = st.columns([5, 6])
            with cl:
                st.markdown('<div class="sec"><span class="sec-icon">📍</span><span class="sec-txt">Location Details</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
                rows_data = [
                    ("🏙", "City",      d.get("city", "—")),
                    ("🗺", "Region",    f"{d.get('region','—')} ({d.get('region_code','')})"),
                    ("🌍", "Country",   f"{flag_img} {d.get('country','—')} ({d.get('country_code','')})"),
                    ("🌐", "Continent", d.get("continent", "—")),
                    ("📮", "Postal",    d.get("postal", "—") or "—"),
                    ("🕐", "Timezone",  d.get("tz", "—")),
                    ("⏰", "UTC Offset",d.get("utc", "—") or "—"),
                    ("📞", "Call Code", d.get("calling", "—") or "—"),
                    ("💰", "Currency",  f"{d.get('currency_name','—')} ({d.get('currency','')})" if d.get("currency") else "—"),
                    ("🗣", "Languages", (d.get("languages","") or "—").replace(",", " · ")),
                    ("🇪🇺", "In EU",   "✓ Yes" if d.get("in_eu") else "✗ No"),
                ]
                rows_html = "".join(
                    f'<div class="info-row"><span class="info-icon">{icon}</span><span class="info-key">{k}</span><span class="info-val">{v}</span></div>'
                    for icon, k, v in rows_data
                )
                st.markdown(f'<div class="info-grid">{rows_html}</div>', unsafe_allow_html=True)
                if d:
                    export_json = export_to_json(d, "ip_location")
                    st.download_button(label="⬇ Export Location Data (JSON)", data=export_json,
                        file_name=f"netpulse_ip_{d.get('ip','unknown')}.json", mime="application/json", use_container_width=True)

            with cr:
                st.markdown('<div class="sec"><span class="sec-icon">🔌</span><span class="sec-txt">Network Identity</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
                net_rows = [
                    ("🌐", "ISP / Org", d.get("org", "—")),
                    ("📡", "ASN",       d.get("asn", "—") or "—"),
                    ("🔄", "Reverse DNS", d.get("rdns", "—")),
                    ("🔑", "IP Version", d.get("version", "IPv4")),
                    ("🏠", "Private IP", "✓ Yes" if d.get("is_private") else "✗ No — Public"),
                ]
                net_html = "".join(
                    f'<div class="info-row"><span class="info-icon">{icon}</span><span class="info-key">{k}</span><span class="info-val">{v}</span></div>'
                    for icon, k, v in net_rows
                )
                st.markdown(f'<div class="info-grid">{net_html}</div>', unsafe_allow_html=True)
                if threat:
                    st.markdown('<div class="sec"><span class="sec-icon">🛡</span><span class="sec-txt">Threat Intelligence</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
                    items = [("🔒", "Proxy / VPN", threat.get("proxy", False)),
                             ("🖥", "Hosting / DC", threat.get("hosting", False)),
                             ("📱", "Mobile Network", threat.get("mobile", False))]
                    threat_rows = ""
                    for icon, label, is_bad in items:
                        status = f'<span class="threat-status-bad">⚠ DETECTED</span>' if is_bad else f'<span class="threat-status-ok">✓ Clean</span>'
                        threat_rows += f'<div class="threat-item"><span class="threat-icon">{icon}</span><span class="threat-label">{label}</span>{status}</div>'
                    st.markdown(f'<div class="threat-panel">{threat_rows}</div>', unsafe_allow_html=True)
                if lat and lon:
                    st.markdown('<div class="sec"><span class="sec-icon">🗺</span><span class="sec-txt">Approximate Location</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="map-wrap">
                      <iframe width="100%" height="260" frameborder="0" scrolling="no"
                        src="https://www.openstreetmap.org/export/embed.html?bbox={lon-2},{lat-1.5},{lon+2},{lat+1.5}&layer=mapnik&marker={lat},{lon}"
                        style="border:none"></iframe>
                      <div class="map-overlay">📍 {lat:.4f}, {lon:.4f}</div>
                    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — WIFI SCANNER (FIXED)
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    sys_n = platform.system()
    req_map = {"Linux": "nmcli / iwlist", "Windows": "netsh (built-in)", "Darwin": "airport (built-in)"}
    st.markdown(f'<div class="info-box info-box-blue">📡 Platform: <strong>{sys_n}</strong> · Tool: {req_map.get(sys_n,"unknown")} · Performs a live rescan before listing. On Linux, requires a wireless adapter and nmcli or iwlist.</div>', unsafe_allow_html=True)

    wc1, wc2 = st.columns([3, 1])
    with wc2:
        sec_filter = st.selectbox("Filter", ["All", "Secure only", "Open only"], label_visibility="collapsed")
    if st.button("📡 Scan WiFi Networks", use_container_width=False):
        with st.spinner("Scanning wireless networks... (this may take a few seconds)"):
            nets, wifi_error = scan_wifi()
        st.session_state["wifi_data"] = (nets, wifi_error)

    wifi_state = st.session_state.get("wifi_data")
    if wifi_state is not None:
        nets, wifi_error = wifi_state

        # Show error prominently if scan failed
        if wifi_error and not nets:
            st.markdown(f"""
            <div class="anomaly-alert">
              <span class="anomaly-icon">📡</span>
              <div class="anomaly-body">
                <div class="anomaly-title">WiFi Scan Failed</div>
                <div class="anomaly-detail">{wifi_error}</div>
              </div>
            </div>""", unsafe_allow_html=True)
            st.markdown("""
            <div class="info-box info-box-amber">
            💡 <strong>Troubleshooting:</strong><br>
            • Linux: Make sure NetworkManager is running: <code>sudo systemctl start NetworkManager</code><br>
            • Linux: Or install iwlist: <code>sudo apt install wireless-tools</code><br>
            • Make sure a WiFi adapter is connected and enabled<br>
            • Try running with elevated privileges if on a restricted system
            </div>""", unsafe_allow_html=True)
        else:
            # Show partial warning if we had an error but still got results
            if wifi_error and nets:
                st.markdown(f'<div class="info-box info-box-amber">⚠ Primary scanner issue: {wifi_error} · Showing results from fallback scanner.</div>', unsafe_allow_html=True)

            if not nets:
                st.markdown('<div class="info-box info-box-amber">📡 No WiFi networks found. Make sure your wireless adapter is enabled and try again.</div>', unsafe_allow_html=True)
            else:
                filtered = nets
                if sec_filter == "Secure only":   filtered = [n for n in nets if n.get("security", "OPEN") != "OPEN"]
                elif sec_filter == "Open only":    filtered = [n for n in nets if n.get("security", "OPEN") == "OPEN"]

                open_c = sum(1 for n in nets if n.get("security") == "OPEN")
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.markdown(f'<div class="tile"><div class="tile-val" style="color:var(--blue2)">{len(nets)}</div><div class="tile-lbl">Networks Found</div></div>', unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="tile"><div class="tile-val" style="color:var(--green2)">{len(nets)-open_c}</div><div class="tile-lbl">Secured</div></div>', unsafe_allow_html=True)
                with c3: st.markdown(f'<div class="tile"><div class="tile-val" style="color:#f87171">{open_c}</div><div class="tile-lbl">Open / Unsecured</div></div>', unsafe_allow_html=True)
                with c4:
                    best_sig = max((n["signal"] for n in nets), default=0)
                    st.markdown(f'<div class="tile"><div class="tile-val" style="color:var(--amber)">{best_sig}%</div><div class="tile-lbl">Best Signal</div></div>', unsafe_allow_html=True)

                if open_c > 0:
                    st.markdown(f"""
                    <div class="anomaly-alert">
                      <span class="anomaly-icon">📡</span>
                      <div class="anomaly-body">
                        <div class="anomaly-title">{open_c} Unsecured Network{"s" if open_c > 1 else ""} Detected</div>
                        <div class="anomaly-detail">Open networks transmit data without encryption. Avoid connecting to unknown open networks.</div>
                      </div>
                    </div>""", unsafe_allow_html=True)

                st.markdown(f'<div class="sec"><span class="sec-icon">📶</span><span class="sec-txt">Detected Networks</span><div class="sec-line"></div><span class="sec-count">{len(filtered)}</span></div>', unsafe_allow_html=True)

                rows = ""
                for net in filtered:
                    sig    = net["signal"]
                    s_col  = sig_color(sig)
                    bars   = math.ceil(sig / 25)
                    bar_html = "".join(f'<div style="width:5px;height:{8+i*5}px;border-radius:2px;background:{"var(--green2)" if i < bars else "var(--bg3)"}"></div>' for i in range(4))
                    sec    = net.get("security", "OPEN")
                    sec_b  = '<span class="badge b-red">OPEN</span>' if sec == "OPEN" else f'<span class="badge b-green">{sec[:12]}</span>'
                    freq   = net.get("freq", "?")
                    try:
                        chan_num = int(net.get("channel","0") or 0)
                    except: chan_num = 0
                    band   = "5 GHz" if "5" in str(freq) and "2.4" not in str(freq) else "2.4 GHz" if "2.4" in str(freq) or (chan_num > 0 and chan_num <= 14) else "?"
                    rows += f'<tr><td style="color:var(--bright);font-weight:600">{net["ssid"]}</td><td><div style="display:flex;align-items:flex-end;gap:2px">{bar_html}</div></td><td style="color:{s_col}">{sig}%</td><td>{sec_b}</td><td style="color:var(--dim)">{net.get("bssid","?")}</td><td style="color:var(--text2)">{net.get("channel","?")}</td><td><span class="badge b-cyan">{band}</span></td></tr>'

                st.markdown(f'<div class="wifi-wrap"><table class="wtable"><thead><tr><th>SSID</th><th>Signal</th><th>%</th><th>Security</th><th>BSSID / MAC</th><th>Ch</th><th>Band</th></tr></thead><tbody>{rows}</tbody></table></div>', unsafe_allow_html=True)

                wifi_json = export_to_json({"scan_time": datetime.now().isoformat(), "networks": nets})
                st.download_button(label="⬇ Export WiFi Scan (JSON)", data=wifi_json,
                    file_name=f"netpulse_wifi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", mime="application/json")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — DIAGNOSTICS
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    dt1, dt2, dt3, dt4, dt5 = st.tabs(["📡 Ping", "🛣 Traceroute", "🔎 DNS Lookup", "📋 ARP & Routes", "⚡ Speed Test"])

    with dt1:
        if _PING_BIN:
            st.markdown(f'<div class="info-box info-box-green">✓ Using system ping binary: <strong>{_PING_BIN}</strong></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="net-notice">⚡ System ping binary not found — using TCP-based latency measurement (pure Python fallback). Results show TCP RTT instead of ICMP.</div>', unsafe_allow_html=True)

        pc1, pc2, pc3 = st.columns([3, 1, 1])
        with pc1: p_h = st.text_input("Host", value="8.8.8.8", label_visibility="collapsed", key="ping_host")
        with pc2: p_c = st.selectbox("Count", [2, 4, 8, 16], index=1, label_visibility="collapsed")
        with pc3: rp = st.button("▶ Ping", use_container_width=True)
        if rp and p_h:
            with st.spinner(f"Pinging {p_h}..."):
                out = ping(p_h.strip(), p_c)
            st.session_state["ping_res"] = (p_h.strip(), out)
            avg_new = parse_ping_avg(out)
            hist = st.session_state.get("ping_history") or []
            hist.append({"host": p_h.strip(), "avg": avg_new, "ts": datetime.now().strftime("%H:%M:%S")})
            st.session_state["ping_history"] = hist[-20:]

        if st.session_state.get("ping_res"):
            h_, o_ = st.session_state["ping_res"]
            avg = parse_ping_avg(o_)
            bc, bl = latency_class(avg)
            bar_col, bar_pct = ping_bar_color(avg)
            st.markdown(f"""
            <div style="display:flex;gap:1rem;margin-bottom:1rem;flex-wrap:wrap">
              <div class="card card-gb" style="flex:1;min-width:180px">
                <div class="ctbar tb-blue"></div>
                <div class="clabel">Target</div>
                <div class="cvalue" style="color:var(--blue2)">{h_}</div>
              </div>
              <div class="card" style="flex:1;min-width:180px;text-align:center">
                <div class="ctbar tb-green"></div>
                <div class="clabel">Avg Latency</div>
                <div class="cval-xl">{f"{avg:.0f}" if avg else "N/A"}</div>
                <div class="gauge-unit">ms</div>
                <div class="ping-gauge"><div class="ping-fill" style="width:{bar_pct}%;background:{bar_col}"></div></div>
              </div>
              <div class="card" style="flex:1;min-width:140px;text-align:center">
                <div class="clabel">Quality</div>
                <div style="margin-top:8px"><span class="badge {bc}" style="font-size:.85rem;padding:6px 16px">{bl}</span></div>
              </div>
            </div>""", unsafe_allow_html=True)

            hist = st.session_state.get("ping_history") or []
            if len(hist) > 1:
                vals = [h["avg"] for h in hist if h["avg"] is not None]
                if vals:
                    max_v = max(vals) or 1
                    bars_html = ""
                    for v in vals:
                        pct = int((v / max_v) * 100)
                        col = "#34d399" if v < 30 else "#fbbf24" if v < 100 else "#f87171"
                        bars_html += f'<div class="lat-bar" style="height:{max(4,pct)}%;background:{col}" title="{v:.0f}ms"></div>'
                    st.markdown(f"""
                    <div class="sparkline-wrap">
                      <div class="sparkline-title">📈 Ping History · last {len(vals)} samples</div>
                      <div class="lat-bar-wrap">{bars_html}</div>
                      <div style="font-family:JetBrains Mono,monospace;font-size:.6rem;color:var(--dim);margin-top:6px">
                        Min: {min(vals):.0f}ms · Max: {max(vals):.0f}ms · Avg: {sum(vals)/len(vals):.0f}ms
                      </div>
                    </div>""", unsafe_allow_html=True)

            st.markdown(f"""<div class="term-wrap"><div class="term-bar">
              <div class="tdot" style="background:#ef4444"></div>
              <div class="tdot" style="background:#f59e0b"></div>
              <div class="tdot" style="background:#10b981"></div>
              <span class="term-title">ping {h_}</span></div>
              <div class="term-body">{o_}<span class="term-cursor"></span></div></div>""", unsafe_allow_html=True)

    with dt2:
        if _TRACE_BIN:
            st.markdown(f'<div class="info-box info-box-green">✓ Using system traceroute: <strong>{_TRACE_BIN}</strong></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="net-notice">⚡ traceroute binary not found — using TCP/socket based traceroute fallback.</div>', unsafe_allow_html=True)

        tc1, tc2 = st.columns([4, 1])
        with tc1: tr_h = st.text_input("Target", value="8.8.8.8", label_visibility="collapsed", key="trace_host")
        with tc2: rt = st.button("▶ Trace", use_container_width=True)
        if rt and tr_h:
            with st.spinner(f"Tracing route to {tr_h}..."):
                st.session_state["trace_res"] = (tr_h, traceroute(tr_h))
        if st.session_state.get("trace_res"):
            h_, o_ = st.session_state["trace_res"]
            hop_count = len([l for l in o_.splitlines() if re.match(r"\s*\d+", l)])
            st.markdown(f'<div class="card card-gb" style="margin-bottom:.8rem"><div class="ctbar tb-blue"></div><div class="clabel">Route to</div><div class="cvalue" style="color:var(--blue2)">{h_} <span style="color:var(--dim);font-size:.8rem">· {hop_count} hops detected</span></div></div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="term-wrap"><div class="term-bar">
              <div class="tdot" style="background:#ef4444"></div>
              <div class="tdot" style="background:#f59e0b"></div>
              <div class="tdot" style="background:#10b981"></div>
              <span class="term-title">traceroute {h_}</span></div>
              <div class="term-body">{o_}<span class="term-cursor"></span></div></div>""", unsafe_allow_html=True)

    with dt3:
        dc1, dc2 = st.columns([4, 1])
        with dc1: di = st.text_input("Domain", value="google.com", label_visibility="collapsed", key="dns_host")
        with dc2: rd = st.button("▶ Resolve", use_container_width=True)
        if rd and di:
            with st.spinner(f"Resolving {di}..."):
                st.session_state["dns_res"] = (di.strip(), dns_lookup(di.strip()))
        if st.session_state.get("dns_res"):
            dn_, dr_ = st.session_state["dns_res"]
            c1, c2, c3, c4 = st.columns(4)
            for col, (title, val, col_var) in zip([c1, c2, c3, c4], [
                ("A Records (IPv4)", "<br>".join(dr_.get("A",  [])) or "—", "var(--blue2)"),
                ("AAAA (IPv6)",      "<br>".join(dr_.get("AAAA",[])) or "—", "var(--cyan)"),
                ("PTR Reverse",       dr_.get("PTR", "—"),                    "var(--green2)"),
                ("FQDN",              dr_.get("fqdn", "—"),                   "var(--text2)"),
            ]):
                with col:
                    st.markdown(f'<div class="card card-gb"><div class="ctbar tb-blue"></div><div class="clabel">{title}</div><div class="cvalue" style="color:{col_var}">{val}</div></div>', unsafe_allow_html=True)

    with dt4:
        a1, a2 = st.columns(2)
        with a1:
            if st.button("📋 ARP Table", use_container_width=True):
                with st.spinner(): st.session_state["arp_res"] = get_arp()
        with a2:
            if st.button("🗺 Routing Table", use_container_width=True):
                with st.spinner(): st.session_state["route_res"] = get_routes()
        for key, lbl in [("arp_res", "arp / ip neigh"), ("route_res", "ip route show")]:
            v = st.session_state.get(key)
            if v:
                st.markdown(f"""<div class="term-wrap" style="margin-bottom:1rem"><div class="term-bar">
                  <div class="tdot" style="background:#ef4444"></div>
                  <div class="tdot" style="background:#f59e0b"></div>
                  <div class="tdot" style="background:#10b981"></div>
                  <span class="term-title">{lbl}</span></div>
                  <div class="term-body">{v}</div></div>""", unsafe_allow_html=True)

    with dt5:
        st.markdown('<div class="info-box info-box-blue">ℹ Downloads 10 MB from Cloudflare edge (max 10s). Single-connection estimate only.</div>', unsafe_allow_html=True)
        if st.button("⚡ Run Speed Test"):
            with st.spinner("Downloading from Cloudflare edge..."):
                sr = speed_test()
            st.session_state["speed_res"] = sr
        sr = st.session_state.get("speed_res")
        if sr:
            if "error" in sr:
                st.error(f"Speed test failed: {sr['error']}")
            else:
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f'<div class="card card-gg" style="text-align:center;padding:2rem"><div class="ctbar tb-green"></div><div class="clabel">Download Speed</div><div class="gauge-val">{sr["mbps"]}</div><div class="gauge-unit">Mbps</div></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="card" style="text-align:center"><div class="clabel">Downloaded</div><div class="cval-green">{fmt_bytes(sr["bytes"])}</div></div>', unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<div class="card" style="text-align:center"><div class="clabel">Duration</div><div class="cval-purple">{sr["elapsed"]}s</div></div>', unsafe_allow_html=True)
                mbps = sr["mbps"]
                if mbps >= 100:    q, qc = "Excellent — 4K Streaming / Large transfers", "var(--green2)"
                elif mbps >= 25:   q, qc = "Good — HD Streaming / Video calls", "var(--green2)"
                elif mbps >= 5:    q, qc = "Fair — SD Streaming / Basic browsing", "var(--amber)"
                else:              q, qc = "Poor — Basic browsing only", "#f87171"
                st.markdown(f'<div class="info-box info-box-green" style="margin-top:.5rem">📊 Assessment: <strong style="color:{qc}">{q}</strong></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — PORT SCANNER
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="info-box info-box-red">⛔ LEGAL WARNING — Only scan localhost, your own servers, or hosts with explicit written permission. Unauthorized scanning may violate CFAA, Computer Misuse Act, IT Act, and equivalent laws.</div>', unsafe_allow_html=True)

    pt1, pt2 = st.tabs(["🔍 Single Host Scan", "📋 IP Range Scan"])

    with pt1:
        sc1, sc2, sc3 = st.columns([3, 2, 1])
        with sc1: s_t = st.text_input("Target", value="localhost", label_visibility="collapsed", key="port_target")
        with sc2: s_p = st.selectbox("Profile", list(PORT_PROFILES.keys()), label_visibility="collapsed")
        with sc3: rs = st.button("🔍 Scan", use_container_width=True)

        if s_p == "Custom Range":
            cps = st.text_input("Custom ports (comma-separated)", placeholder="22,80,443,8080", label_visibility="collapsed")
            try:    plist = [int(p.strip()) for p in cps.split(",") if p.strip().isdigit()]
            except: plist = []
        else:
            plist = PORT_PROFILES.get(s_p, [])

        if rs and s_t and plist:
            with st.spinner(f"Scanning {len(plist)} ports on {s_t}..."):
                results, rip = port_scan(s_t, plist)
            st.session_state["ports_res"] = (s_t, rip, results)

        pres = st.session_state.get("ports_res")
        if pres:
            ph_, rip_, pr_ = pres
            open_p  = [p for p in pr_ if p["state"] == "OPEN"]
            close_p = [p for p in pr_ if p["state"] != "OPEN"]

            st.markdown(f'<div class="card card-gb" style="margin-bottom:.8rem"><div class="ctbar tb-blue"></div><div class="clabel">Resolved Target</div><div class="cvalue" style="font-size:1.1rem">{ph_} <span style="color:var(--dim)">→</span> {rip_}</div></div>', unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="tile"><div class="tile-val">{len(pr_)}</div><div class="tile-lbl">Scanned</div></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="tile"><div class="tile-val" style="color:var(--green2)">{len(open_p)}</div><div class="tile-lbl">✓ Open</div></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="tile"><div class="tile-val" style="color:var(--dim)">{len(close_p)}</div><div class="tile-lbl">✗ Closed</div></div>', unsafe_allow_html=True)

            dangerous_open = [p for p in open_p if p["port"] in [23, 21, 445, 2375, 3389, 5900, 11211, 6379, 27017]]
            if dangerous_open:
                dports_str = ", ".join(f'{p["port"]} ({p["service"]})' for p in dangerous_open)
                st.markdown(f"""
                <div class="anomaly-alert">
                  <span class="anomaly-icon">🚨</span>
                  <div class="anomaly-body">
                    <div class="anomaly-title">High-Risk Ports Open</div>
                    <div class="anomaly-detail">Potentially dangerous services detected: {dports_str}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

            if open_p:
                st.markdown(f'<div class="sec"><span class="sec-icon">✅</span><span class="sec-txt">Open Ports</span><div class="sec-line"></div><span class="sec-count">{len(open_p)}</span></div>', unsafe_allow_html=True)
                open_rows = "".join(
                    f'<tr><td><span class="badge b-green">OPEN</span></td>'
                    f'<td style="color:var(--blue2);font-weight:600">{p["port"]}</td>'
                    f'<td style="color:var(--bright)">{p["service"]}</td></tr>'
                    for p in open_p
                )
                st.markdown(f'<div class="wifi-wrap"><table class="wtable"><thead><tr><th>State</th><th>Port</th><th>Service</th></tr></thead><tbody>{open_rows}</tbody></table></div>', unsafe_allow_html=True)

            st.markdown('<div class="sec"><span class="sec-icon">📋</span><span class="sec-txt">All Results</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
            all_rows = ""
            for p in pr_:
                if p["state"] == "OPEN":
                    state_badge = '<span class="badge b-green">OPEN</span>'
                else:
                    state_badge = '<span class="badge b-gray">CLOSED</span>'
                all_rows += (f'<tr><td>{state_badge}</td>'
                             f'<td style="color:var(--blue2)">{p["port"]}</td>'
                             f'<td style="color:var(--text2)">{p["service"]}</td></tr>')
            st.markdown(f'<div class="wifi-wrap"><table class="wtable"><thead><tr><th>State</th><th>Port</th><th>Service</th></tr></thead><tbody>{all_rows}</tbody></table></div>', unsafe_allow_html=True)

            scan_export = export_to_json({"target": ph_, "resolved": rip_,
                "scan_time": datetime.now().isoformat(), "results": pr_})
            st.download_button(label="⬇ Export Scan Results (JSON)", data=scan_export,
                file_name=f"netpulse_portscan_{ph_}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", mime="application/json")

    with pt2:
        st.markdown('<div class="info-box info-box-amber">⚠ Scans all IPs in the given range against selected ports. Max 256 IPs per scan. Only use on your own network.</div>', unsafe_allow_html=True)
        rc1, rc2, rc3, rc4 = st.columns([2, 2, 2, 1])
        with rc1: r_start = st.text_input("Start IP", value="192.168.1.1", label_visibility="collapsed")
        with rc2: r_end   = st.text_input("End IP",   value="192.168.1.10", label_visibility="collapsed")
        with rc3: r_ports_str = st.text_input("Ports (comma-sep)", value="22,80,443,8080", label_visibility="collapsed")
        with rc4: r_scan = st.button("🔍 Scan Range", use_container_width=True)

        if r_scan:
            try:
                r_ports = [int(x.strip()) for x in r_ports_str.split(",") if x.strip().isdigit()]
            except: r_ports = []
            ip_list, err = ip_range_expand(r_start.strip(), r_end.strip())
            if err:
                st.error(f"Range error: {err}")
            elif not r_ports:
                st.error("Enter at least one valid port.")
            else:
                prog = st.progress(0, text="Scanning...")
                range_results = []
                for i, ip in enumerate(ip_list):
                    res, _ = port_scan(ip, r_ports, timeout=0.5)
                    open_ports = [r for r in res if r["state"] == "OPEN"]
                    range_results.append({"ip": ip, "open": open_ports, "total": len(res)})
                    prog.progress((i + 1) / len(ip_list), text=f"Scanning {ip}...")
                prog.empty()
                alive = [r for r in range_results if r["open"]]
                c1, c2, c3 = st.columns(3)
                with c1: st.markdown(f'<div class="tile"><div class="tile-val">{len(ip_list)}</div><div class="tile-lbl">IPs Scanned</div></div>', unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="tile"><div class="tile-val" style="color:var(--green2)">{len(alive)}</div><div class="tile-lbl">Hosts Alive</div></div>', unsafe_allow_html=True)
                with c3:
                    total_open = sum(len(r["open"]) for r in range_results)
                    st.markdown(f'<div class="tile"><div class="tile-val" style="color:var(--amber)">{total_open}</div><div class="tile-lbl">Open Ports</div></div>', unsafe_allow_html=True)

                st.markdown(f'<div class="sec"><span class="sec-icon">📋</span><span class="sec-txt">Range Scan Results</span><div class="sec-line"></div><span class="sec-count">{len(alive)} hosts with open ports</span></div>', unsafe_allow_html=True)
                range_rows = ""
                for r in range_results:
                    if r["open"]:
                        ports_str = ", ".join(str(p["port"]) for p in r["open"])
                        range_rows += (f'<tr><td style="color:var(--blue2);font-weight:600">{r["ip"]}</td>'
                                       f'<td><span class="badge b-green">{len(r["open"])} Open</span></td>'
                                       f'<td style="color:var(--bright)">{ports_str}</td></tr>')
                if range_rows:
                    st.markdown(f'<div class="wifi-wrap"><table class="wtable"><thead><tr><th>IP Address</th><th>Status</th><th>Open Ports</th></tr></thead><tbody>{range_rows}</tbody></table></div>', unsafe_allow_html=True)
                else:
                    st.info("No open ports found on any host in the range.")

                if range_results:
                    range_export = export_to_json({"range": f"{r_start} - {r_end}",
                        "ports_scanned": r_ports, "scan_time": datetime.now().isoformat(), "results": range_results})
                    st.download_button(label="⬇ Export Range Scan (JSON)", data=range_export,
                        file_name=f"netpulse_rangescan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", mime="application/json")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 — LIVE MONITOR (FULLY REBUILT with Start/Stop/Reset)
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    # ── Monitor Control Bar ──
    mon_running = st.session_state.get("monitor_running", False)
    mon_history = st.session_state.get("monitor_history", [])

    # Control buttons
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 1, 1, 5])
    with btn_col1:
        if st.button("▶ Start" if not mon_running else "⏸ Pause", use_container_width=True, key="mon_start_stop"):
            st.session_state["monitor_running"] = not mon_running
            st.rerun()
    with btn_col2:
        if st.button("⏹ Stop", use_container_width=True, key="mon_stop"):
            st.session_state["monitor_running"] = False
            st.rerun()
    with btn_col3:
        if st.button("↺ Reset", use_container_width=True, key="mon_reset"):
            st.session_state["monitor_running"] = False
            st.session_state["monitor_history"] = []
            st.session_state["monitor_tick"] = 0
            st.session_state["net_stats"] = None
            st.rerun()

    # Status bar
    tick = st.session_state.get("monitor_tick", 0)
    if mon_running:
        status_class = "monitor-status-running"
        dot_html = '<span class="pulse-dot"></span>'
        status_text = f'<span style="color:var(--green2)">LIVE — Sampling every 2s · Tick #{tick}</span>'
    else:
        status_class = "monitor-status-stopped"
        dot_html = '<span style="width:8px;height:8px;border-radius:50%;background:var(--dim);display:inline-block"></span>'
        status_text = f'<span style="color:var(--dim)">STOPPED — {len(mon_history)} samples collected</span>'

    # Mini sparkline for bandwidth history
    sparkline_html = ""
    if mon_history:
        recv_vals = [h.get("recv_ps", 0) for h in mon_history[-20:]]
        sent_vals = [h.get("sent_ps", 0) for h in mon_history[-20:]]
        max_val = max(max(recv_vals or [1]), max(sent_vals or [1])) or 1
        for rv, sv in zip(recv_vals, sent_vals):
            rh = max(2, int((rv / max_val) * 28))
            sh = max(2, int((sv / max_val) * 28))
            sparkline_html += f'<div style="display:flex;flex-direction:column;gap:1px;align-items:center"><div class="sparkline-mini-bar" style="height:{rh}px;background:var(--green2);width:5px;border-radius:2px 2px 0 0"></div><div class="sparkline-mini-bar" style="height:{sh}px;background:var(--blue2);width:5px;border-radius:2px 2px 0 0"></div></div>'

    st.markdown(f"""
    <div class="monitor-status-bar {status_class}">
      {dot_html}
      {status_text}
      <div style="flex:1"></div>
      <div style="display:flex;align-items:flex-end;gap:2px;height:32px">{sparkline_html}</div>
      <div style="font-size:.6rem;color:var(--dim);margin-left:8px">
        <span style="color:var(--green2)">▮</span> ↓Recv &nbsp;
        <span style="color:var(--blue2)">▮</span> ↑Sent
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Network Interfaces (always shown, refreshed when monitoring) ──
    st.markdown('<div class="sec"><span class="sec-icon">🔌</span><span class="sec-txt">Network Interfaces</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
    ifaces = get_ifaces()
    if ifaces:
        iface_rows = ""
        for i in ifaces:
            up_badge   = '<span class="badge b-green">UP</span>' if i["up"] else '<span class="badge b-red">DOWN</span>'
            ipv6_short = i["ipv6"][:22] + ("…" if len(i["ipv6"]) > 22 else "")
            iface_rows += (f'<tr><td style="color:var(--bright);font-weight:600">{i["name"]}</td>'
                           f'<td>{up_badge}</td>'
                           f'<td style="color:var(--blue2)">{i["ipv4"]}</td>'
                           f'<td style="color:var(--dim)">{ipv6_short}</td>'
                           f'<td style="color:var(--dim)">{i["mac"]}</td>'
                           f'<td style="color:var(--text2)">{i["mask"]}</td>'
                           f'<td><span class="badge b-cyan">{i["speed"]} Mbps</span></td>'
                           f'<td style="color:var(--dim)">{i["mtu"]}</td></tr>')
        st.markdown(f'<div class="wifi-wrap"><table class="wtable"><thead><tr><th>Interface</th><th>Status</th><th>IPv4</th><th>IPv6</th><th>MAC</th><th>Netmask</th><th>Speed</th><th>MTU</th></tr></thead><tbody>{iface_rows}</tbody></table></div>', unsafe_allow_html=True)

    # ── Live I/O Section ──
    st.markdown('<div class="sec"><span class="sec-icon">📊</span><span class="sec-txt">I/O Throughput</span><div class="sec-line"></div></div>', unsafe_allow_html=True)

    # If monitoring is running, take a live sample automatically
    if mon_running:
        with st.spinner("Sampling network I/O (1 second)..."):
            live_stats = net_io_sample()
        if "error" not in live_stats:
            # Append to history
            hist_entry = {
                "ts":       live_stats["ts"],
                "recv_ps":  live_stats["recv_ps"],
                "sent_ps":  live_stats["sent_ps"],
                "errin":    live_stats["errin"],
                "errout":   live_stats["errout"],
                "dropin":   live_stats["dropin"],
                "dropout":  live_stats["dropout"],
            }
            mon_history = st.session_state.get("monitor_history", [])
            mon_history.append(hist_entry)
            st.session_state["monitor_history"] = mon_history[-60:]  # Keep last 60 samples
            st.session_state["monitor_tick"] = tick + 1
            st.session_state["net_stats"] = live_stats
    else:
        # Manual sample button when stopped
        if st.button("⚡ Sample I/O Once", key="manual_io"):
            with st.spinner("Sampling 1 second..."):
                st.session_state["net_stats"] = net_io_sample()

    stats = st.session_state.get("net_stats")
    if stats and "error" not in stats:
        ts_str = stats.get("ts", datetime.now().strftime("%H:%M:%S"))
        c1, c2, c3, c4 = st.columns(4)
        for col, (v, l, c) in zip([c1, c2, c3, c4], [
            (fmt_bytes(stats["sent_ps"]) + "/s", "↑ Upload",     "var(--blue2)"),
            (fmt_bytes(stats["recv_ps"]) + "/s", "↓ Download",   "var(--green2)"),
            (fmt_bytes(stats["bytes_sent"]),      "Total Sent",   "var(--text2)"),
            (fmt_bytes(stats["bytes_recv"]),      "Total Recv",   "var(--text2)"),
        ]):
            with col:
                st.markdown(f'<div class="tile"><div class="tile-val" style="color:{c};font-size:1.2rem">{v}</div><div class="tile-lbl">{l}</div><div class="tile-sub">{ts_str}</div></div>', unsafe_allow_html=True)

        c5, c6, c7, c8 = st.columns(4)
        for col, (v, l, c) in zip([c5, c6, c7, c8], [
            (f"{stats['pkts_sent']:,}", "Pkts Sent", "var(--text2)"),
            (f"{stats['pkts_recv']:,}", "Pkts Recv", "var(--text2)"),
            (str(stats["errin"] + stats["errout"]),   "Errors",  "#f87171" if stats["errin"] + stats["errout"] > 0 else "var(--green2)"),
            (str(stats["dropin"] + stats["dropout"]), "Dropped", "#f87171" if stats["dropin"] + stats["dropout"] > 0 else "var(--green2)"),
        ]):
            with col:
                st.markdown(f'<div class="tile"><div class="tile-val" style="color:{c}">{v}</div><div class="tile-lbl">{l}</div></div>', unsafe_allow_html=True)

        anomalies = detect_network_anomalies(stats)
        if anomalies:
            for title, detail in anomalies:
                st.markdown(f"""
                <div class="anomaly-alert">
                  <span class="anomaly-icon">⚠️</span>
                  <div class="anomaly-body">
                    <div class="anomaly-title">{title}</div>
                    <div class="anomaly-detail">{detail}</div>
                  </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-box info-box-green">✓ No network anomalies detected in this sample.</div>', unsafe_allow_html=True)

    elif stats and "error" in stats:
        st.error(f"I/O sampling error: {stats['error']}")

    # ── Bandwidth History Chart ──
    if mon_history and len(mon_history) > 1:
        st.markdown('<div class="sec"><span class="sec-icon">📈</span><span class="sec-txt">Bandwidth History</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
        recv_vals = [h.get("recv_ps", 0) for h in mon_history]
        sent_vals = [h.get("sent_ps", 0) for h in mon_history]
        ts_vals   = [h.get("ts", "") for h in mon_history]
        max_val   = max(max(recv_vals or [1]), max(sent_vals or [1])) or 1

        recv_bars = ""
        sent_bars = ""
        for rv, sv in zip(recv_vals, sent_vals):
            rh = max(2, int((rv / max_val) * 80))
            sh = max(2, int((sv / max_val) * 80))
            recv_bars += f'<div style="flex:1;height:{rh}px;background:var(--green2);border-radius:2px 2px 0 0;opacity:.8;min-width:3px" title="{fmt_bytes(rv)}/s"></div>'
            sent_bars += f'<div style="flex:1;height:{sh}px;background:var(--blue2);border-radius:2px 2px 0 0;opacity:.8;min-width:3px" title="{fmt_bytes(sv)}/s"></div>'

        # Stats summary
        avg_recv = sum(recv_vals) / len(recv_vals)
        avg_sent = sum(sent_vals) / len(sent_vals)
        max_recv = max(recv_vals)
        max_sent = max(sent_vals)

        st.markdown(f"""
        <div class="sparkline-wrap">
          <div class="sparkline-title">↓ Download Rate · {len(recv_vals)} samples · avg {fmt_bytes(avg_recv)}/s · peak {fmt_bytes(max_recv)}/s</div>
          <div style="display:flex;align-items:flex-end;gap:2px;height:80px;padding:4px 0">{recv_bars}</div>
        </div>
        <div class="sparkline-wrap">
          <div class="sparkline-title">↑ Upload Rate · avg {fmt_bytes(avg_sent)}/s · peak {fmt_bytes(max_sent)}/s</div>
          <div style="display:flex;align-items:flex-end;gap:2px;height:80px;padding:4px 0">{sent_bars}</div>
        </div>""", unsafe_allow_html=True)

        # Timestamp labels
        if len(ts_vals) >= 2:
            st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:.58rem;color:var(--dim);display:flex;justify-content:space-between;margin-top:-8px"><span>{ts_vals[0]}</span><span>{ts_vals[len(ts_vals)//2]}</span><span>{ts_vals[-1]}</span></div>', unsafe_allow_html=True)

    # ── Active TCP Connections (Live when monitoring) ──
    st.markdown('<div class="sec"><span class="sec-icon">🔗</span><span class="sec-txt">Active TCP Connections</span><div class="sec-line"></div></div>', unsafe_allow_html=True)

    show_conns = mon_running
    if not mon_running:
        if st.button("🔗 List Active Connections", key="list_conns_btn"):
            show_conns = True

    if show_conns:
        conns, conn_err = get_live_connections()
        if conn_err:
            st.warning(f"Could not list connections: {conn_err}")
        elif not conns:
            st.info("No established connections found (may need elevated privileges).")
        else:
            ext_count = sum(1 for c in conns if c["is_ext"])
            conn_meta_c1, conn_meta_c2, conn_meta_c3 = st.columns(3)
            with conn_meta_c1: st.markdown(f'<div class="tile"><div class="tile-val">{len(conns)}</div><div class="tile-lbl">Total Connections</div></div>', unsafe_allow_html=True)
            with conn_meta_c2: st.markdown(f'<div class="tile"><div class="tile-val" style="color:var(--amber)">{ext_count}</div><div class="tile-lbl">External</div></div>', unsafe_allow_html=True)
            with conn_meta_c3: st.markdown(f'<div class="tile"><div class="tile-val" style="color:var(--green2)">{len(conns)-ext_count}</div><div class="tile-lbl">Local/LAN</div></div>', unsafe_allow_html=True)

            conn_rows = ""
            for c in conns[:30]:
                ext_badge = '<span class="badge b-orange">EXT</span>' if c["is_ext"] else '<span class="badge b-gray">LAN</span>'
                conn_rows += (f'<tr>'
                              f'<td style="color:var(--blue2)">{c["local"]}</td>'
                              f'<td style="color:var(--text2)">{c["remote"]}</td>'
                              f'<td>{ext_badge}</td>'
                              f'<td><span class="badge b-green">ESTABLISHED</span></td>'
                              f'<td style="color:var(--dim)">{c["pid"]}</td>'
                              f'<td style="color:var(--text2)">{c["proc"]}</td>'
                              f'</tr>')
            st.markdown(f'<div class="wifi-wrap"><table class="wtable"><thead><tr><th>Local</th><th>Remote</th><th>Type</th><th>Status</th><th>PID</th><th>Process</th></tr></thead><tbody>{conn_rows}</tbody></table></div>', unsafe_allow_html=True)

            if mon_running:
                st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:.6rem;color:var(--dim);margin-top:6px">🔄 Auto-refreshed at {datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)

    # ── Auto-rerun loop when monitoring is active ──
    if mon_running:
        time.sleep(1)  # Brief pause between the sample and rerun
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6 — TOOLS
# ─────────────────────────────────────────────────────────────────────────────
with tab6:
    tt1, tt2, tt3, tt4 = st.tabs(["🧮 Subnet Calc", "🌐 HTTP Inspector", "📡 Multi-Ping", "🖥 Hostname Intel"])

    with tt1:
        sc1, sc2 = st.columns([4, 1])
        with sc1: ci_n = st.text_input("CIDR", value="192.168.1.0/24", label_visibility="collapsed", placeholder="192.168.1.0/24")
        with sc2: run_s = st.button("🧮 Calculate", use_container_width=True)
        if run_s and ci_n:
            sub = subnet_calc(ci_n.strip())
            if "error" in sub:
                st.error(f"Invalid CIDR: {sub['error']}")
            else:
                c1, c2, c3, c4 = st.columns(4)
                for col, (v, l, c) in zip([c1, c2, c3, c4], [
                    (sub["network"],   "Network Address", "var(--blue2)"),
                    (sub["broadcast"], "Broadcast",       "#f87171"),
                    (sub["netmask"],   "Subnet Mask",     "var(--green2)"),
                    (sub["wildcard"],  "Wildcard Mask",   "var(--amber)"),
                ]):
                    with col:
                        st.markdown(f'<div class="card card-gb"><div class="ctbar tb-blue"></div><div class="clabel">{l}</div><div class="cvalue" style="color:{c};font-size:1.05rem">{v}</div></div>', unsafe_allow_html=True)

                c5, c6, c7, c8 = st.columns(4)
                for col, (v, l, c) in zip([c5, c6, c7, c8], [
                    (f"/{sub['prefix']}",  "Prefix",       "var(--blue2)"),
                    (f"{sub['total']:,}",  "Total Hosts",  "var(--text2)"),
                    (f"{sub['usable']:,}", "Usable Hosts", "var(--green2)"),
                    (f"Class {sub['cls']}","IP Class",     "var(--purple)"),
                ]):
                    with col:
                        st.markdown(f'<div class="tile"><div class="tile-val" style="color:{c}">{v}</div><div class="tile-lbl">{l}</div></div>', unsafe_allow_html=True)

                c9, c10, c11, c12 = st.columns(4)
                with c9:  st.markdown(f'<div class="card"><div class="clabel">First Usable</div><div class="cvalue" style="color:var(--green2)">{sub["first"]}</div></div>', unsafe_allow_html=True)
                with c10: st.markdown(f'<div class="card"><div class="clabel">Last Usable</div><div class="cvalue" style="color:var(--green2)">{sub["last"]}</div></div>', unsafe_allow_html=True)
                with c11: st.markdown(f'<div class="card"><div class="clabel">Private / RFC1918</div><div class="cvalue">{"✓ Yes" if sub["private"] else "✗ Public"}</div></div>', unsafe_allow_html=True)
                with c12: st.markdown(f'<div class="card"><div class="clabel">Multicast</div><div class="cvalue">{"✓ Yes" if sub["multicast"] else "✗ No"}</div></div>', unsafe_allow_html=True)

                sub_export = export_to_json({"cidr": ci_n, **sub})
                st.download_button(label="⬇ Export Subnet Info (JSON)", data=sub_export,
                    file_name=f"netpulse_subnet_{ci_n.replace('/','-')}.json", mime="application/json")

    with tt2:
        hc1, hc2 = st.columns([4, 1])
        with hc1: h_u = st.text_input("URL", value="https://example.com", label_visibility="collapsed")
        with hc2: rh = st.button("🔍 Inspect", use_container_width=True)
        if rh and h_u:
            with st.spinner(f"Fetching {h_u}..."):
                st.session_state["headers_res"] = fetch_headers(h_u.strip())
        hr = st.session_state.get("headers_res")
        if hr:
            if "error" in hr:
                st.error(f"Request failed: {hr['error']}")
            else:
                sc = hr["status"]
                sc_c = "var(--green2)" if 200 <= sc < 300 else "var(--amber)" if 300 <= sc < 400 else "#f87171"
                c1, c2, c3, c4, c5 = st.columns(5)
                with c1: st.markdown(f'<div class="tile"><div class="tile-val" style="color:{sc_c}">{sc}</div><div class="tile-lbl">HTTP Status</div></div>', unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="tile"><div class="tile-val" style="font-size:1.2rem;color:var(--blue2)">{hr["elapsed_ms"]}ms</div><div class="tile-lbl">Response Time</div></div>', unsafe_allow_html=True)
                with c3: st.markdown(f'<div class="tile"><div class="tile-val">{hr["redirects"]}</div><div class="tile-lbl">Redirects</div></div>', unsafe_allow_html=True)
                with c4: st.markdown(f'<div class="tile"><div class="tile-val">{len(hr["headers"])}</div><div class="tile-lbl">Headers</div></div>', unsafe_allow_html=True)
                with c5: st.markdown(f'<div class="tile"><div class="tile-val" style="font-size:1.1rem;color:var(--purple)">{fmt_bytes(hr.get("size",0))}</div><div class="tile-lbl">Body Size</div></div>', unsafe_allow_html=True)

                st.markdown(f'<div class="card" style="margin-top:.8rem"><div class="clabel">Final URL</div><div class="cvalue" style="color:var(--blue2)">{hr["url"]}</div></div>', unsafe_allow_html=True)

                st.markdown('<div class="sec"><span class="sec-icon">📋</span><span class="sec-txt">Response Headers</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
                hrows = "".join(f'<div class="whois-row"><div class="whois-key">{k}</div><div class="whois-val">{v}</div></div>' for k, v in hr["headers"].items())
                st.markdown(f'<div class="whois-wrap">{hrows}</div>', unsafe_allow_html=True)

                sec_hdrs = ["Strict-Transport-Security", "Content-Security-Policy", "X-Frame-Options",
                            "X-Content-Type-Options", "Referrer-Policy", "Permissions-Policy",
                            "X-XSS-Protection", "Cross-Origin-Opener-Policy"]
                st.markdown('<div class="sec"><span class="sec-icon">🛡</span><span class="sec-txt">Security Header Audit</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
                cols = st.columns(4)
                for i, sh in enumerate(sec_hdrs):
                    present = sh in hr["headers"]
                    with cols[i % 4]:
                        badge = '<span class="badge b-green">✓ Present</span>' if present else '<span class="badge b-red">✗ Missing</span>'
                        st.markdown(f'<div class="card" style="padding:.8rem 1rem"><div class="clabel">{sh}</div><div style="margin-top:5px">{badge}</div></div>', unsafe_allow_html=True)

    with tt3:
        mp_h = st.text_area("Hosts (one per line)", value="8.8.8.8\n1.1.1.1\ngoogle.com\ngithub.com\ncloudflare.com", height=120, label_visibility="collapsed")
        mc1, mc2 = st.columns([3, 1])
        with mc2: mp_c = st.selectbox("Packets each", [2, 4, 8], index=1, label_visibility="collapsed")

        if not _PING_BIN:
            st.markdown('<div class="net-notice">⚡ Using TCP-based latency (no ping binary). Results measure TCP RTT.</div>', unsafe_allow_html=True)

        if st.button("📡 Ping All Hosts"):
            hosts   = [h.strip() for h in mp_h.strip().splitlines() if h.strip()]
            results = []; prog = st.progress(0)
            for i, h in enumerate(hosts):
                out = ping(h, mp_c); avg = parse_ping_avg(out); results.append((h, avg))
                prog.progress((i + 1) / len(hosts))
            prog.empty()
            st.session_state["multi_ping_res"] = results

        mp_results = st.session_state.get("multi_ping_res")
        if mp_results:
            valid_results = [(h, avg) for h, avg in mp_results if avg is not None]
            if valid_results:
                max_lat = max(avg for _, avg in valid_results) or 1
                hist_bars = ""
                for h, avg in valid_results:
                    pct = int((avg / max_lat) * 100)
                    col = "#34d399" if avg < 30 else "#fbbf24" if avg < 100 else "#f87171"
                    short_h = h[:15] + "…" if len(h) > 15 else h
                    hist_bars += f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;font-family:JetBrains Mono,monospace;font-size:.7rem"><span style="color:var(--text2);width:120px;flex-shrink:0">{short_h}</span><div style="flex:1;height:10px;background:var(--bg3);border-radius:5px;overflow:hidden"><div style="width:{pct}%;height:100%;background:{col};border-radius:5px"></div></div><span style="color:{col};width:50px;text-align:right">{avg:.0f}ms</span></div>'
                st.markdown(f'<div class="sparkline-wrap"><div class="sparkline-title">📊 Latency Comparison</div>{hist_bars}</div>', unsafe_allow_html=True)

            mp_rows = ""
            for h, avg in mp_results:
                bc, bl = latency_class(avg)
                lat_str = f"{avg:.0f}" if avg else "—"
                mp_rows += (f'<tr><td style="color:var(--bright)">{h}</td>'
                            f'<td><span class="badge {bc}">{bl}</span></td>'
                            f'<td style="color:var(--dim)">{lat_str} ms</td></tr>')
            st.markdown(f'<div class="wifi-wrap"><table class="wtable"><thead><tr><th>Host</th><th>Status</th><th>Avg Latency</th></tr></thead><tbody>{mp_rows}</tbody></table></div>', unsafe_allow_html=True)

            ping_export = export_to_json({"scan_time": datetime.now().isoformat(),
                "results": [{"host": h, "avg_ms": avg} for h, avg in mp_results]})
            st.download_button(label="⬇ Export Multi-Ping Results (JSON)", data=ping_export,
                file_name=f"netpulse_multiping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", mime="application/json")

    with tt4:
        st.markdown('<div class="info-box info-box-blue">🖥 Resolve a hostname to its IPs, perform reverse lookups, and fetch basic geolocation for the resolved address.</div>', unsafe_allow_html=True)
        h4c1, h4c2 = st.columns([4, 1])
        with h4c1:
            hostname_input = st.text_input("Hostname or Domain", value="github.com",
                                           label_visibility="collapsed", placeholder="e.g. github.com, api.example.com")
        with h4c2:
            h4_btn = st.button("🖥 Resolve", use_container_width=True, key="hostname_btn")

        if h4_btn and hostname_input:
            with st.spinner(f"Resolving {hostname_input}..."):
                st.session_state["hostname_res"] = resolve_hostname(hostname_input.strip())

        hr4 = st.session_state.get("hostname_res")
        if hr4:
            if hr4.get("error"):
                st.error(f"Resolution failed: {hr4['error']}")
            else:
                h4_name = hr4.get("hostname", "—")
                h4_ipv4 = hr4.get("ipv4", [])
                h4_ipv6 = hr4.get("ipv6", [])
                h4_fqdn = hr4.get("fqdn", "—")
                h4_geo  = hr4.get("geo", {})
                h4_ptrs = hr4.get("ptr_map", [])

                c1, c2, c3 = st.columns(3)
                with c1: st.markdown(f'<div class="tile"><div class="tile-val" style="color:var(--blue2)">{len(h4_ipv4)}</div><div class="tile-lbl">IPv4 Addresses</div></div>', unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="tile"><div class="tile-val" style="color:var(--cyan)">{len(h4_ipv6)}</div><div class="tile-lbl">IPv6 Addresses</div></div>', unsafe_allow_html=True)
                with c3: st.markdown(f'<div class="tile"><div class="tile-val" style="color:var(--purple)">{len(h4_ptrs)}</div><div class="tile-lbl">PTR Records</div></div>', unsafe_allow_html=True)

                st.markdown('<div class="sec"><span class="sec-icon">🖥</span><span class="sec-txt">Resolution Results</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
                res_rows = [
                    ("🏷", "Hostname",   h4_name),
                    ("🌐", "FQDN",      h4_fqdn),
                    ("🔵", "IPv4 (A)",  " · ".join(h4_ipv4) if h4_ipv4 else "—"),
                    ("🟣", "IPv6 (AAAA)"," · ".join(h4_ipv6[:3]) if h4_ipv6 else "—"),
                ]
                res_html = "".join(
                    f'<div class="info-row"><span class="info-icon">{icon}</span><span class="info-key">{k}</span><span class="info-val">{v}</span></div>'
                    for icon, k, v in res_rows
                )
                st.markdown(f'<div class="info-grid">{res_html}</div>', unsafe_allow_html=True)

                if h4_ptrs:
                    st.markdown('<div class="sec"><span class="sec-icon">🔄</span><span class="sec-txt">Reverse DNS (PTR)</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
                    ptr_rows = "".join(
                        f'<div class="info-row"><span class="info-icon">🔁</span><span class="info-key">{ip}</span><span class="info-val" style="color:var(--text2)">{ptr}</span></div>'
                        for ip, ptr in h4_ptrs
                    )
                    st.markdown(f'<div class="info-grid">{ptr_rows}</div>', unsafe_allow_html=True)

                if h4_geo:
                    st.markdown('<div class="sec"><span class="sec-icon">🌍</span><span class="sec-txt">Geo Intelligence (First IP)</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
                    geo_rows = [
                        ("🏢", "ASN / Org", h4_geo.get("org","—")),
                        ("🌍", "Country",   h4_geo.get("country","—")),
                        ("🏙", "City",      h4_geo.get("city","—")),
                        ("📡", "ASN",       h4_geo.get("asn","—")),
                    ]
                    geo_html = "".join(
                        f'<div class="info-row"><span class="info-icon">{icon}</span><span class="info-key">{k}</span><span class="info-val">{v}</span></div>'
                        for icon, k, v in geo_rows
                    )
                    st.markdown(f'<div class="info-grid">{geo_html}</div>', unsafe_allow_html=True)

                host_export = export_to_json(hr4)
                st.download_button(label="⬇ Export Hostname Intel (JSON)", data=host_export,
                    file_name=f"netpulse_hostname_{h4_name}.json", mime="application/json")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 7 — SSL & SECURITY
# ─────────────────────────────────────────────────────────────────────────────
with tab7:
    st.markdown('<div class="info-box info-box-blue">🔒 Inspect SSL/TLS certificates and security headers. Enter a hostname (no https://) to fetch certificate details.</div>', unsafe_allow_html=True)

    ssl1, ssl2, ssl3 = st.tabs(["🔒 SSL Certificate", "🛡 Headers Audit", "🌐 WHOIS / ASN"])

    with ssl1:
        c1, c2 = st.columns([4, 1])
        with c1: cert_host = st.text_input("Hostname", value="google.com", label_visibility="collapsed", placeholder="example.com (no https://)")
        with c2: cert_btn = st.button("🔒 Fetch Cert", use_container_width=True)
        if cert_btn and cert_host:
            with st.spinner(f"Fetching SSL cert for {cert_host}..."):
                st.session_state["cert_res"] = (cert_host.strip(), get_cert_info(cert_host.strip()))
        cert_data = st.session_state.get("cert_res")
        if cert_data:
            ch_, ci_ = cert_data
            if "error" in ci_:
                st.error(f"SSL error: {ci_['error']}")
            else:
                try:
                    from datetime import datetime as dt
                    exp_dt  = dt.strptime(ci_["not_after"], "%b %d %H:%M:%S %Y %Z")
                    days_left = (exp_dt - dt.utcnow()).days
                    exp_color = "var(--green2)" if days_left > 30 else "var(--amber)" if days_left > 0 else "#f87171"
                    exp_badge = f'<span class="badge {"b-green" if days_left>30 else "b-amber" if days_left>0 else "b-red"}">{days_left}d left</span>'
                except: days_left = None; exp_color = "var(--text2)"; exp_badge = ""

                if days_left is not None and days_left <= 30:
                    urgency = "CRITICAL — Certificate has expired!" if days_left <= 0 else f"WARNING — Only {days_left} days until expiry"
                    st.markdown(f"""
                    <div class="anomaly-alert">
                      <span class="anomaly-icon">{"🚨" if days_left <= 0 else "⚠️"}</span>
                      <div class="anomaly-body">
                        <div class="anomaly-title">Certificate Expiry {urgency}</div>
                        <div class="anomaly-detail">Cert for {ch_} expires: {ci_["not_after"]}. Renew immediately.</div>
                      </div>
                    </div>""", unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                with c1: st.markdown(f'<div class="tile"><div class="tile-val" style="color:var(--green2);font-size:1.1rem">{ci_["version"]}</div><div class="tile-lbl">TLS Version</div></div>', unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="tile"><div class="tile-val" style="color:{exp_color};font-size:1.3rem">{days_left if days_left is not None else "?"}</div><div class="tile-lbl">Days Until Expiry</div></div>', unsafe_allow_html=True)
                with c3: st.markdown(f'<div class="tile"><div class="tile-val" style="font-size:.85rem;color:var(--cyan)">{ci_["cipher"][:18]}</div><div class="tile-lbl">Cipher Suite</div></div>', unsafe_allow_html=True)

                rows_data = [
                    ("🏷", "Common Name",  ci_["cn"]),
                    ("🏢", "Organization", ci_["org"]),
                    ("🔐", "Issuer",       ci_["issuer"]),
                    ("📅", "Not Before",   ci_["not_before"]),
                    ("📅", "Not After",    f'{ci_["not_after"]} {exp_badge}'),
                    ("🔒", "TLS Version",  ci_["version"]),
                    ("🔑", "Cipher",       ci_["cipher"]),
                    ("📋", "SANs",         " · ".join(ci_["san"][:8]) + ("…" if len(ci_["san"]) > 8 else "") or "—"),
                ]
                rows_html = "".join(
                    f'<div class="info-row"><span class="info-icon">{icon}</span><span class="info-key">{k}</span><span class="info-val">{v}</span></div>'
                    for icon, k, v in rows_data
                )
                st.markdown(f'<div class="sec"><span class="sec-icon">🔒</span><span class="sec-txt">Certificate Details · {ch_}</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-grid">{rows_html}</div>', unsafe_allow_html=True)

                cert_export = export_to_json({"hostname": ch_, "days_left": days_left, **ci_})
                st.download_button(label="⬇ Export Certificate Data (JSON)", data=cert_export,
                    file_name=f"netpulse_cert_{ch_}.json", mime="application/json")

    with ssl2:
        h2c1, h2c2 = st.columns([4, 1])
        with h2c1: h2_url = st.text_input("URL", value="https://google.com", label_visibility="collapsed", key="sec_url")
        with h2c2: h2_btn = st.button("🛡 Audit", use_container_width=True, key="sec_audit")
        if h2_btn and h2_url:
            with st.spinner("Fetching headers..."):
                st.session_state["headers_res"] = fetch_headers(h2_url.strip())

        hr2 = st.session_state.get("headers_res")
        if hr2 and "error" not in hr2:
            CRITICAL_HEADERS = {
                "Strict-Transport-Security": ("Enforces HTTPS", "b-red"),
                "Content-Security-Policy":   ("Prevents XSS/injection", "b-red"),
                "X-Frame-Options":           ("Prevents clickjacking", "b-amber"),
                "X-Content-Type-Options":    ("Prevents MIME sniffing", "b-amber"),
                "Referrer-Policy":           ("Controls referrer leakage", "b-amber"),
                "Permissions-Policy":        ("Controls browser features", "b-amber"),
                "X-XSS-Protection":          ("Legacy XSS filter", "b-gray"),
                "Cross-Origin-Opener-Policy":("Cross-origin isolation", "b-amber"),
                "Cross-Origin-Resource-Policy":("Resource isolation", "b-gray"),
                "Access-Control-Allow-Origin":("CORS policy", "b-gray"),
            }
            present_count = sum(1 for h in CRITICAL_HEADERS if h in hr2["headers"])
            score = int((present_count / len(CRITICAL_HEADERS)) * 100)
            score_col = "var(--green2)" if score >= 70 else "var(--amber)" if score >= 40 else "#f87171"

            sc1, sc2, sc3 = st.columns(3)
            with sc1: st.markdown(f'<div class="tile"><div class="tile-val" style="color:{score_col}">{score}</div><div class="tile-lbl">Security Score</div></div>', unsafe_allow_html=True)
            with sc2: st.markdown(f'<div class="tile"><div class="tile-val" style="color:var(--green2)">{present_count}</div><div class="tile-lbl">Present</div></div>', unsafe_allow_html=True)
            with sc3: st.markdown(f'<div class="tile"><div class="tile-val" style="color:#f87171">{len(CRITICAL_HEADERS)-present_count}</div><div class="tile-lbl">Missing</div></div>', unsafe_allow_html=True)

            if score < 40:
                st.markdown(f"""
                <div class="anomaly-alert">
                  <span class="anomaly-icon">🚨</span>
                  <div class="anomaly-body">
                    <div class="anomaly-title">Poor Security Posture · Score {score}/100</div>
                    <div class="anomaly-detail">Critical security headers are missing. This site may be vulnerable to XSS, clickjacking, and data leakage attacks.</div>
                  </div>
                </div>""", unsafe_allow_html=True)

            st.markdown('<div class="sec"><span class="sec-icon">🛡</span><span class="sec-txt">Security Header Checklist</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
            cols = st.columns(2)
            for i, (hdr, (desc, miss_cls)) in enumerate(CRITICAL_HEADERS.items()):
                present = hdr in hr2["headers"]
                with cols[i % 2]:
                    badge = '<span class="badge b-green">✓ Present</span>' if present else f'<span class="badge {miss_cls}">✗ Missing</span>'
                    val   = hr2["headers"].get(hdr, "")
                    short_val = (val[:60] + "…") if len(val) > 60 else val
                    val_div = f'<div style="margin-top:5px;font-family:JetBrains Mono,monospace;font-size:.65rem;color:var(--text2)">{short_val}</div>' if short_val else ""
                    st.markdown(f'<div class="card" style="padding:.9rem 1.1rem;margin-bottom:.5rem"><div class="clabel">{hdr}</div><div style="display:flex;align-items:center;justify-content:space-between;margin-top:4px">{badge}<span style="font-family:JetBrains Mono,monospace;font-size:.6rem;color:var(--dim)">{desc}</span></div>{val_div}</div>', unsafe_allow_html=True)

    with ssl3:
        st.markdown('<div class="info-box info-box-blue">🌐 Fetch ASN, organization, and threat intelligence for any IP address using ip-api.com.</div>', unsafe_allow_html=True)
        w1, w2 = st.columns([4, 1])
        with w1: whois_ip = st.text_input("IP Address", value="8.8.8.8", label_visibility="collapsed", placeholder="IPv4 or IPv6 address")
        with w2: whois_btn = st.button("🔍 Lookup", use_container_width=True)
        if whois_btn and whois_ip:
            with st.spinner(f"Looking up {whois_ip}..."):
                try:
                    r = requests.get(f"http://ip-api.com/json/{whois_ip.strip()}?fields=66846719", timeout=8)
                    j = r.json()
                    st.session_state["whois_res"] = j
                except Exception as e:
                    st.session_state["whois_res"] = {"error": str(e)}

        wr = st.session_state.get("whois_res")
        if wr:
            if "error" in wr:
                st.error(f"Lookup failed: {wr['error']}")
            elif wr.get("status") == "success":
                cc2 = wr.get("countryCode", "").lower()
                flag2 = f'<img src="https://flagcdn.com/20x15/{cc2}.png" style="border-radius:2px;vertical-align:middle;margin-right:6px" />' if cc2 else ""

                c1, c2, c3 = st.columns(3)
                with c1:
                    proxy_col = "#f87171" if wr.get("proxy") else "var(--green2)"
                    proxy_val = "⚠ YES" if wr.get("proxy") else "✓ No"
                    st.markdown(f'<div class="tile"><div class="tile-val" style="color:{proxy_col};font-size:1.1rem">{proxy_val}</div><div class="tile-lbl">Proxy / VPN</div></div>', unsafe_allow_html=True)
                with c2:
                    host_col = "#fbbf24" if wr.get("hosting") else "var(--green2)"
                    host_val = "⚠ YES" if wr.get("hosting") else "✓ No"
                    st.markdown(f'<div class="tile"><div class="tile-val" style="color:{host_col};font-size:1.1rem">{host_val}</div><div class="tile-lbl">Hosting / DC</div></div>', unsafe_allow_html=True)
                with c3:
                    mob_col = "var(--purple)" if wr.get("mobile") else "var(--dim)"
                    mob_val = "📱 YES" if wr.get("mobile") else "✗ No"
                    st.markdown(f'<div class="tile"><div class="tile-val" style="color:{mob_col};font-size:1.1rem">{mob_val}</div><div class="tile-lbl">Mobile Network</div></div>', unsafe_allow_html=True)

                fields = [
                    ("🌐", "IP Address",    wr.get("query", "—")),
                    ("🌍", "Country",       f'{flag2}{wr.get("country","—")} ({wr.get("countryCode","")})'),
                    ("🗺",  "Region",        f'{wr.get("regionName","—")} ({wr.get("region","")})'),
                    ("🏙",  "City",          wr.get("city", "—")),
                    ("📮",  "Zip",           wr.get("zip", "—")),
                    ("📡",  "ISP",           wr.get("isp", "—")),
                    ("🏢",  "Organization",  wr.get("org", "—")),
                    ("📊",  "AS",            wr.get("as", "—")),
                    ("🕐",  "Timezone",      wr.get("timezone", "—")),
                    ("📍",  "Coordinates",   f'{wr.get("lat","—")}, {wr.get("lon","—")}'),
                    ("📱",  "Mobile",        "✓ Yes" if wr.get("mobile") else "✗ No"),
                    ("🔒",  "Proxy / VPN",   "⚠ Detected" if wr.get("proxy") else "✓ Clean"),
                    ("🖥",  "Hosting / DC",  "⚠ Detected" if wr.get("hosting") else "✓ Clean"),
                ]
                rows_html = "".join(
                    f'<div class="info-row"><span class="info-icon">{icon}</span><span class="info-key">{k}</span><span class="info-val">{v}</span></div>'
                    for icon, k, v in fields
                )
                st.markdown(f'<div class="info-grid">{rows_html}</div>', unsafe_allow_html=True)

                whois_export = export_to_json(wr)
                st.download_button(label="⬇ Export WHOIS / ASN Data (JSON)", data=whois_export,
                    file_name=f"netpulse_whois_{wr.get('query','unknown')}.json", mime="application/json")

# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center;margin-top:3.5rem;padding-top:1.5rem;border-top:1px solid var(--border);
     font-family:'JetBrains Mono',monospace;font-size:.6rem;color:#162e52;letter-spacing:.14em;">
  ⚡ NETPULSE v4.0 · ADVANCED NETWORK INTELLIGENCE · ETHICAL USE ONLY · MIT LICENSE
</div>""", unsafe_allow_html=True)
