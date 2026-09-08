import http.server
import socketserver
import json
import os
import urllib.parse
import sys
from dataclasses import asdict
from pathlib import Path
import numpy as np

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai.audio_classifier.classifier import BioacousticClassifier
from ai.vision_classifier.classifier import VisionClassifier
from app.ui.office_kit_bridge import VivoOfficeKitBridge
from data.lessons import NatureLanguageBook

SAMPLES_DIR = PROJECT_ROOT / "demo" / "sample_recordings"
SAMPLE_FILES = {
    "bee": "sample_bee.wav",
    "cricket": "sample_cricket.wav",
    "rain": "sample_rain_wind.wav",
    "bat": "sample_bat_ultrasonic.wav",
}

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>NATURA — Multimodal Nature Explorer</title>
    <meta name="description" content="NATURA: on-device nature exploration. Hear the unheard, interpret nature, compose music, and learn nature's language.">
    <link rel="manifest" href="/manifest.json">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="NATURA">
    <meta name="theme-color" content="#2a4a2c">
    <link rel="icon" type="image/svg+xml" href="/icon.svg">
    <link rel="apple-touch-icon" href="/icon.svg">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #f6f2ea;
            --bg-alt: #efe8d9;
            --panel: #fffdf8;
            --ink: #26301f;
            --ink-soft: #5b6350;
            --line: #dfd6bf;
            --moss: #3f6b42;
            --moss-deep: #2a4a2c;
            --moss-soft: #cfe0c6;
            --sand: #cbb992;
            --sand-deep: #a68a56;
            --amber: #c98a3f;
            --red: #a63d3d;
            --radius: 18px;
            --radius-sm: 12px;
            --gap: 14px;
            --phone-w: 390px;
            --phone-h: 844px;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
        html, body { background: #d8d0bd; color: var(--ink); font-family: 'Inter', -apple-system, sans-serif; height: 100%; overflow: hidden; }
        h1, h2, h3, .display { font-family: 'Fraunces', Georgia, serif; }
        button { font-family: inherit; }
        a { color: inherit; }

        /* PHONE SHELL — fixed on wide desktop screens; full-bleed native app on mobile & PWA */
        #phone-wrap { height: 100vh; height: 100dvh; width: 100vw; display: flex; align-items: center; justify-content: center; }
        #app { width: var(--phone-w); height: var(--phone-h); max-height: 94vh; background: var(--bg); position: relative; display: flex; flex-direction: column; border-radius: 34px; overflow: hidden; box-shadow: 0 20px 60px rgba(30,25,10,0.35); border: 8px solid #171a12; flex-shrink: 0; }

        .statusbar { display: flex; justify-content: space-between; align-items: center; padding: 10px 22px 2px; font-size: 12px; font-weight: 700; color: var(--ink); flex-shrink: 0; }
        .topbar { display: flex; align-items: center; gap: 9px; padding: 6px 18px 12px; flex-shrink: 0; }
        .topbar .mark { width: 24px; height: 24px; color: var(--moss); flex-shrink: 0; }
        .topbar span { font-family: 'Fraunces', serif; font-weight: 600; font-size: 17px; letter-spacing: 0.4px; color: var(--moss-deep); }

        /* NATIVE MOBILE APP ADAPTATION (Any Phone & Standalone PWA) */
        @media (max-width: 600px), (display-mode: standalone), (max-device-width: 600px) {
            html, body {
                background: var(--bg) !important;
                height: 100% !important;
                height: 100dvh !important;
                overflow: hidden !important;
            }
            #phone-wrap {
                height: 100% !important;
                height: 100dvh !important;
                width: 100% !important;
                display: block !important;
            }
            #app {
                width: 100% !important;
                width: 100vw !important;
                max-width: 100% !important;
                height: 100% !important;
                height: 100dvh !important;
                max-height: 100dvh !important;
                border-radius: 0 !important;
                border: none !important;
                box-shadow: none !important;
            }
            .statusbar {
                display: none !important; /* Mobile devices already show native system bar */
            }
            .topbar {
                padding-top: max(10px, env(safe-area-inset-top)) !important;
                padding-left: max(16px, env(safe-area-inset-left));
                padding-right: max(16px, env(safe-area-inset-right));
            }
            .bottomnav {
                padding-bottom: max(16px, env(safe-area-inset-bottom)) !important;
                padding-left: max(16px, env(safe-area-inset-left));
                padding-right: max(16px, env(safe-area-inset-right));
            }
            .page {
                padding-bottom: calc(100px + env(safe-area-inset-bottom, 0px)) !important;
            }
        }

        .pwa-install-banner { display: flex; align-items: center; justify-content: space-between; background: linear-gradient(135deg, #f2faed, #e6f2de); border: 1.5px solid var(--moss-soft); border-radius: var(--radius-sm); padding: 10px 12px; margin-bottom: 14px; box-shadow: 0 2px 8px rgba(42,74,44,0.08); }

        main { flex: 1; min-height: 0; overflow-y: auto; -webkit-overflow-scrolling: touch; }
        .page { display: none; padding: 6px 18px 100px; min-height: 100%; }
        .page.active { display: block; animation: fadeIn 0.22s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(6px);} to { opacity: 1; transform: translateY(0);} }

        .eyebrow { font-size: 10.5px; text-transform: uppercase; letter-spacing: 1.5px; color: var(--sand-deep); font-weight: 700; margin-bottom: 6px; }
        .page h1.display { font-size: 24px; font-weight: 600; color: var(--moss-deep); margin-bottom: 5px; line-height: 1.2; }
        .page-lede { color: var(--ink-soft); font-size: 12.5px; margin-bottom: 18px; line-height: 1.5; }

        .section-heading { display: flex; align-items: center; gap: 9px; margin: 22px 0 12px; }
        .section-heading .glyph { width: 24px; height: 24px; border-radius: 7px; background: var(--moss-soft); color: var(--moss-deep); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        .section-heading .glyph svg { width: 14px; height: 14px; }
        .section-heading h2 { font-size: 15px; font-weight: 600; color: var(--ink); }

        .card { background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius); padding: 16px; box-shadow: 0 3px 14px rgba(60,50,20,0.05); margin-bottom: var(--gap); }
        .card p.desc { font-size: 12.5px; color: var(--ink-soft); line-height: 1.55; margin-bottom: 12px; }
        .card:last-child { margin-bottom: 0; }

        .hero { position: relative; border-radius: 20px; overflow: hidden; padding: 24px 20px; color: #f4f1e6; min-height: 170px; display: flex; flex-direction: column; justify-content: flex-end; background:
            radial-gradient(120% 100% at 15% 0%, rgba(255,255,255,0.10), transparent 55%),
            linear-gradient(200deg, #1f3d24 0%, #2c4f2c 38%, #3c5c37 62%, #6c7a48 100%); margin-bottom: var(--gap); }
        .hero::before { content: ''; position: absolute; inset: 0; background-image:
            radial-gradient(2px 2px at 20% 30%, rgba(255,255,255,0.25) 0, transparent 60%),
            radial-gradient(2px 2px at 70% 20%, rgba(255,255,255,0.18) 0, transparent 60%),
            radial-gradient(3px 3px at 85% 55%, rgba(255,255,255,0.12) 0, transparent 60%);
            opacity: 0.6; }
        .hero svg.leafart { position: absolute; right: -10px; top: -10px; width: 110px; height: 110px; opacity: 0.16; }
        .hero .hero-tag { display: inline-flex; align-items: center; gap: 6px; font-size: 10px; text-transform: uppercase; letter-spacing: 1.4px; font-weight: 700; color: #d7e6c8; margin-bottom: 9px; position: relative; }
        .hero h1 { font-size: 22px; line-height: 1.18; font-weight: 500; margin-bottom: 8px; position: relative; }
        .hero p { font-size: 11.5px; color: #dfe8d3; line-height: 1.5; position: relative; }

        .btn { background: var(--moss); color: #fff; border: none; padding: 10px 15px; border-radius: 999px; font-weight: 700; cursor: pointer; font-size: 12px; display: inline-flex; align-items: center; gap: 6px; transition: 0.15s; white-space: nowrap; }
        .btn:active { transform: scale(0.97); }
        .btn:hover { background: var(--moss-deep); }
        .btn.light { background: rgba(255,255,255,0.14); color: #f4f1e6; border: 1px solid rgba(255,255,255,0.35); }
        .btn.outline { background: transparent; color: var(--moss-deep); border: 1.5px solid var(--moss); }
        .btn.outline:hover { background: var(--moss-soft); }
        .btn.gold { background: var(--amber); }
        .btn.ghost { background: var(--bg-alt); color: var(--ink); }
        .btn.danger { background: var(--red); color: #fff; }
        .btn:disabled { opacity: 0.45; cursor: not-allowed; }
        .btn svg { width: 14px; height: 14px; flex-shrink:0; }
        .btn.block { width: 100%; justify-content: center; }
        .btn.sm { padding: 7px 11px; font-size: 11px; }
        .btn.xs { padding: 6px 10px; font-size: 10.5px; border-radius: 10px; }
        .btn.rec.recording { background: #a63d3d; }

        .capture-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
        .capture-panel { background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius); padding: 12px; text-align: center; }
        .capture-panel .stage { height: 90px; border-radius: var(--radius-sm); background: var(--moss-soft); display: flex; align-items: center; justify-content: center; margin-bottom: 9px; overflow: hidden; position: relative; }
        .capture-panel video, .capture-panel img, .capture-panel canvas { width: 100%; height: 100%; object-fit: cover; }
        .capture-panel audio { width: 100%; }
        .capture-panel .stage.empty { color: var(--moss-deep); font-size: 10px; flex-direction: column; gap: 4px; }
        .capture-panel .stage.empty svg { width: 20px; height: 20px; opacity: 0.55; }
        .capture-panel .status { font-size: 9.5px; color: var(--ink-soft); margin-top: 6px; min-height: 12px; line-height: 1.35; }
        .capture-panel .label { font-size: 11px; font-weight: 700; margin-bottom: 8px; color: var(--ink); }
        .bars { display: flex; align-items: flex-end; gap: 3px; height: 100%; padding: 8px; }
        .bars i { flex: 1; background: var(--moss); border-radius: 3px; animation: bar 0.9s ease-in-out infinite; }
        @keyframes bar { 0%,100% { height: 20%; } 50% { height: 85%; } }

        .meter-row { margin-bottom: 12px; }
        .meter-label { display: flex; justify-content: space-between; font-size: 11.5px; color: var(--ink-soft); margin-bottom: 5px; }
        .meter-bar { height: 7px; background: var(--bg-alt); border-radius: 4px; overflow: hidden; }
        .meter-fill { height: 100%; border-radius: 4px; background: linear-gradient(90deg, var(--moss), var(--sand)); }

        .toggle-row { display: flex; gap: 7px; margin-bottom: 12px; }
        .toggle-btn { flex: 1; text-align: center; padding: 8px 4px; border-radius: 10px; font-size: 11px; font-weight: 700; background: var(--bg-alt); color: var(--ink-soft); cursor: pointer; border: 1px solid var(--line); }
        .toggle-btn.active { background: var(--moss); color: #fff; border-color: var(--moss); }
        .mode-explain { font-size: 11.5px; color: var(--ink-soft); background: var(--bg-alt); border-radius: 10px; padding: 10px 12px; margin-bottom: 12px; line-height: 1.5; }
        .mode-explain b { color: var(--moss-deep); }

        .layer-box { background: var(--bg-alt); border-left: 3px solid var(--moss); padding: 11px 14px; border-radius: 0 12px 12px 0; margin-bottom: 9px; font-size: 12.5px; color: var(--ink); line-height: 1.5; }
        .layer-title { font-weight: 700; color: var(--moss-deep); font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.4px; margin-bottom: 4px; }
        .layer-box.grey { border-color: #a09a86; }

        .stem-tag { display: inline-block; background: var(--moss-soft); color: var(--moss-deep); border: 1px solid #b9d1ac; border-radius: 8px; padding: 5px 9px; font-size: 11px; margin: 3px 4px 3px 0; font-weight: 600; }

        .stat-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: var(--gap); }
        .stat-grid.cols-3 { grid-template-columns: repeat(3, 1fr); }
        .stat-box { background: var(--bg-alt); border-radius: var(--radius-sm); padding: 12px 8px; text-align: center; }
        .stat-num { font-family: 'Fraunces', serif; font-size: 19px; font-weight: 600; color: var(--moss-deep); }
        .stat-label { font-size: 9.5px; color: var(--ink-soft); text-transform: uppercase; letter-spacing: 0.4px; margin-top: 3px; }

        .field-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
        .field-card { border-radius: var(--radius-sm); overflow: hidden; border: 1px solid var(--line); background: var(--panel); cursor: pointer; transition: transform 0.15s; position: relative; }
        .field-card:active { transform: scale(0.97); }
        .field-art { height: 96px; position: relative; overflow: hidden; }
        .field-art img, .field-art video { width: 100%; height: 100%; object-fit: cover; display: block; }
        .field-art .scene { width:100%; height:100%; }
        .field-card figcaption { padding: 8px 9px 2px; font-size: 11.5px; font-weight: 700; color: var(--ink); }
        .field-card .sub { padding: 0 9px 9px; font-size: 9.5px; color: var(--ink-soft); }
        .field-card .badge { position:absolute; top:6px; left:6px; background:rgba(20,20,10,0.6); color:#fff; font-size:8.5px; font-weight:700; padding:3px 7px; border-radius:999px; letter-spacing:0.3px; }
        .field-card .del-btn { position:absolute; top:6px; right:6px; width:22px; height:22px; border-radius:50%; background:rgba(20,20,10,0.55); color:#fff; border:none; display:flex; align-items:center; justify-content:center; cursor:pointer; z-index:2; }
        .field-card .del-btn svg { width:11px; height:11px; }

        .timeline { display: flex; gap: 3px; align-items: flex-end; height: 56px; padding: 8px 0; overflow-x: auto; }
        .timeline .tick { min-width: 10px; border-radius: 3px 3px 0 0; background: var(--sand); cursor: pointer; opacity: 0.75; }
        .timeline .tick:hover, .timeline .tick.hot { opacity: 1; background: var(--moss); }
        .timeline-labels { display: flex; justify-content: space-between; font-size: 9.5px; color: var(--ink-soft); margin-top: 4px; }

        .quest-card { padding: 14px; margin-bottom: 12px; }
        .quest-card .qhead { display:flex; align-items:flex-start; gap: 10px; margin-bottom: 10px; }
        .quest-card .qnum { min-width: 24px; height: 24px; border-radius: 50%; background: var(--line); color: var(--ink-soft); display:flex; align-items:center; justify-content:center; font-weight:800; font-size:11px; flex-shrink:0; }
        .quest-card .qnum.done { background: var(--moss); color: #fff; }
        .quest-card .qtitle { font-size: 13px; font-weight: 700; color: var(--ink); margin-bottom: 3px; }
        .quest-card .qdetail { font-size: 11.5px; color: var(--ink-soft); line-height: 1.5; }
        .quest-card .qactions { display:flex; gap: 8px; margin-top: 10px; }
        .quest-card.complete { border-color: var(--moss); background: linear-gradient(180deg, var(--panel), #f2f7ee); }
        .quest-mini-stage { min-height: 60px; border-radius: 10px; background: var(--bg-alt); display:flex; align-items:center; justify-content:center; overflow:hidden; margin-top:10px; flex-direction: column; padding: 8px; gap: 8px; }
        .quest-mini-stage img, .quest-mini-stage video { width:100%; border-radius: 8px; }
        .quest-mini-stage audio { width:100%; }
        .quest-mini-stage.empty { color: var(--ink-soft); font-size: 10.5px; }
        .quest-fail { color: var(--red); font-size: 11px; font-weight: 700; }
        .chip-select { display:flex; flex-wrap: wrap; gap: 6px; justify-content: center; }
        .chip-select button { padding: 6px 11px; border-radius: 999px; border: 1px solid var(--line); background: var(--panel); font-size: 10.5px; font-weight: 600; color: var(--ink); cursor: pointer; }
        .chip-select button:hover { background: var(--moss-soft); }
        .quest-timer { display: flex; align-items: center; justify-content: space-between; background: var(--bg-alt); border-radius: var(--radius-sm); padding: 14px 16px; margin-bottom: 14px; }
        .quest-timer .time { font-family: 'Fraunces', serif; font-size: 24px; font-weight: 600; color: var(--moss-deep); }
        .progressbar { height: 6px; background: var(--bg-alt); border-radius: 4px; overflow: hidden; margin-bottom: 16px; }
        .progressbar > div { height: 100%; background: var(--moss); border-radius: 4px; width: 0%; transition: width 0.4s; }

        .cat-chip-row { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 4px; margin-bottom: 4px; }
        .cat-chip { flex-shrink:0; padding: 8px 14px; border-radius: 999px; background: var(--bg-alt); border: 1px solid var(--line); font-size: 11.5px; font-weight: 700; color: var(--ink-soft); cursor: pointer; }
        .cat-chip.active { background: var(--moss); color: #fff; border-color: var(--moss); }
        .learn-fact { font-size: 12px; padding: 7px 0 7px 14px; border-left: 2px solid var(--line); position: relative; color: var(--ink-soft); line-height: 1.5; margin-bottom: 2px; }
        .learn-fact b { color: var(--ink); }
        .learn-fact::before { content: ''; position: absolute; left: -5px; top: 11px; width: 7px; height: 7px; border-radius: 50%; background: var(--moss); }

        .mix-row { display: flex; align-items: center; gap: 10px; padding: 10px 0; border-bottom: 1px solid var(--line); }
        .mix-row:last-child { border-bottom: none; }
        .mix-art { width: 40px; height: 40px; border-radius: 10px; flex-shrink: 0; overflow:hidden; }
        .mix-art img { width:100%; height:100%; object-fit:cover; }
        .mix-info { flex: 1; min-width: 0; }
        .mix-info b { font-size: 12.5px; display:block; }
        .mix-info span { font-size: 10.5px; color: var(--ink-soft); }
        .mix-vol { width: 52px; accent-color: var(--moss); }
        .mix-toggle { width: 32px; height: 32px; border-radius: 50%; border: 1.5px solid var(--moss); background: transparent; color: var(--moss); font-weight: 800; cursor: pointer; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
        .mix-toggle.on { background: var(--moss); color: #fff; }
        .mix-track-bar { height: 5px; border-radius: 3px; background: var(--bg-alt); overflow: hidden; margin-top: 5px; }
        .mix-track-bar > div { height: 100%; width: 0%; background: var(--sand-deep); }
        .comp-name-input, .modal input[type=text] { width: 100%; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--line); background: var(--bg-alt); font-size: 13px; color: var(--ink); margin-bottom: 10px; font-family: inherit; }
        .saved-comp { display:flex; align-items:center; gap:10px; padding: 9px 0; border-bottom: 1px solid var(--line); font-size: 12px; }
        .saved-comp:last-child { border-bottom: none; }
        .saved-comp .sc-del { margin-left: auto; background: none; border: none; color: var(--ink-soft); cursor: pointer; padding: 4px; }

        .cinema-pick-list { max-height: 190px; overflow-y: auto; border: 1px solid var(--line); border-radius: 12px; margin-bottom: 10px; }
        .cinema-pick-item { display:flex; align-items:center; gap:9px; padding: 8px 10px; border-bottom: 1px solid var(--line); font-size: 11.5px; cursor: pointer; }
        .cinema-pick-item:last-child { border-bottom: none; }
        .cinema-pick-item .cp-art { width: 34px; height: 34px; border-radius: 8px; overflow:hidden; flex-shrink:0; }
        .cinema-pick-item .cp-art img, .cinema-pick-item .cp-art .scene { width:100%; height:100%; object-fit:cover; }
        .cinema-pick-item input { accent-color: var(--moss); }
        .cinema-chips { display:flex; flex-wrap:wrap; gap:6px; margin-bottom: 12px; }
        .cinema-chip { display:flex; align-items:center; gap:5px; background: var(--moss-soft); color: var(--moss-deep); border-radius: 999px; padding: 5px 8px 5px 10px; font-size: 10.5px; font-weight: 700; }
        .cinema-chip button { background:none; border:none; color: var(--moss-deep); cursor:pointer; font-weight:800; padding:0; }
        .cinema-stage { height: 200px; border-radius: var(--radius-sm); background: #101710; display:flex; align-items:center; justify-content:center; overflow:hidden; margin-bottom: 10px; position: relative; }
        .cinema-stage img, .cinema-stage video { width:100%; height:100%; object-fit: cover; }
        .cinema-stage .cs-empty { color: #cfd9c8; font-size: 11.5px; }
        .cinema-stage .cs-caption { position:absolute; bottom:0; left:0; right:0; background: linear-gradient(0deg, rgba(0,0,0,0.65), transparent); color:#fff; font-size: 11px; padding: 16px 10px 8px; }

        nav.bottomnav { position: absolute; bottom: 0; left: 0; right: 0; background: rgba(255,253,248,0.94); backdrop-filter: blur(6px); border-top: 1px solid var(--line); display: flex; padding: 7px 4px calc(env(safe-area-inset-bottom, 8px)); flex-shrink: 0; z-index: 5; }
        nav.bottomnav button { flex: 1; background: none; border: none; color: var(--ink-soft); font-size: 9.5px; padding: 6px 2px; border-radius: 10px; cursor: pointer; display: flex; flex-direction: column; align-items: center; gap: 3px; font-weight: 600; }
        nav.bottomnav button svg { width: 19px; height: 19px; }
        nav.bottomnav button.active { color: var(--moss-deep); }
        nav.bottomnav button.active svg { color: var(--moss-deep); }

        .backbar { display:flex; align-items:center; gap: 10px; padding: 4px 0 14px; }
        .backbar button { background: var(--bg-alt); border: none; width: 32px; height: 32px; border-radius: 50%; display:flex; align-items:center; justify-content:center; cursor:pointer; color: var(--ink); flex-shrink:0; }
        .backbar button svg { width: 16px; height: 16px; }
        .detail-hero { height: 180px; border-radius: var(--radius); overflow: hidden; margin-bottom: var(--gap); position: relative; }
        .detail-hero img, .detail-hero video { width: 100%; height: 100%; object-fit: cover; }
        .detail-hero .scene { width:100%; height:100%; }
        .detail-title { font-size: 19px; font-weight: 600; color: var(--moss-deep); margin-bottom: 3px; }
        .detail-meta { font-size: 11.5px; color: var(--ink-soft); margin-bottom: 12px; }
        .sample-strip { display:flex; gap: 8px; overflow-x: auto; padding-bottom: 4px; margin-bottom: var(--gap); }
        .sample-chip { flex-shrink:0; width: 64px; text-align:center; cursor: pointer; position: relative; }
        .sample-chip .sc-art { width: 64px; height: 56px; border-radius: 10px; overflow:hidden; border: 2px solid transparent; }
        .sample-chip.active .sc-art { border-color: var(--moss); }
        .sample-chip .sc-art img, .sample-chip .sc-art .scene { width:100%; height:100%; object-fit:cover; }
        .sample-chip .sc-label { font-size: 8.5px; color: var(--ink-soft); margin-top: 3px; }
        .sample-chip .sc-x { position:absolute; top:-4px; right:-4px; width:17px; height:17px; border-radius:50%; background: var(--red); color:#fff; border:none; font-size:10px; cursor:pointer; display:flex; align-items:center; justify-content:center; }

        .live-toast { position: absolute; top: 12px; left: 14px; right: 14px; background: var(--moss-deep); color: #fff; padding: 10px 14px; border-radius: 12px; font-size: 11px; font-weight: 600; box-shadow: 0 4px 18px rgba(0,0,0,0.25); z-index: 50; display: flex; align-items: center; justify-content: space-between; gap: 8px; animation: slideDown 0.25s ease; }
        @keyframes slideDown { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: translateY(0); } }
        .video-mix-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; max-height: 210px; overflow-y: auto; margin-bottom: 10px; }
        .video-mix-item { border: 1.5px solid var(--line); border-radius: 10px; overflow: hidden; background: var(--bg-alt); cursor: pointer; position: relative; transition: all 0.2s; }
        .video-mix-item.selected { border-color: var(--moss); box-shadow: 0 0 0 2px var(--moss-soft); background: #f2f8ee; }
        .video-mix-item .vm-thumb { width: 100%; height: 72px; background: #111; position: relative; display: flex; align-items: center; justify-content: center; overflow:hidden; }
        .video-mix-item .vm-thumb video, .video-mix-item .vm-thumb img { width: 100%; height: 100%; object-fit: cover; }
        .video-mix-item .vm-badge { position: absolute; top: 4px; right: 4px; background: rgba(0,0,0,0.65); color: #fff; font-size: 8.5px; padding: 2px 5px; border-radius: 4px; font-weight: 700; }
        .video-mix-item .vm-title { font-size: 10.5px; font-weight: 700; padding: 5px 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: var(--ink); }
        .video-mix-chips { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 8px; }
        .video-mix-chip { display: inline-flex; align-items: center; gap: 4px; background: var(--moss-soft); color: var(--moss-deep); border-radius: 999px; padding: 4px 8px; font-size: 10px; font-weight: 700; }
        .video-mix-chip button { background: none; border: none; color: var(--moss-deep); font-weight: 800; cursor: pointer; padding: 0; }
        .quest-celebration { background: linear-gradient(145deg, #f2faed, #e2f0d9); border: 2px solid var(--moss); border-radius: var(--radius); padding: 16px; text-align: center; margin-bottom: 14px; }

        .modal-backdrop { position: absolute; inset: 0; background: rgba(20,20,10,0.5); display: none; align-items: flex-end; z-index: 20; }
        .modal-backdrop.open { display: flex; }
        .modal { background: var(--panel); width: 100%; border-radius: 22px 22px 0 0; padding: 20px 20px calc(20px + env(safe-area-inset-bottom, 10px)); max-height: 85%; overflow-y: auto; }
        .modal h3 { font-size: 16px; font-weight: 600; color: var(--moss-deep); margin-bottom: 4px; }
        .modal .modal-sub { font-size: 11.5px; color: var(--ink-soft); margin-bottom: 14px; line-height: 1.5; }
        .modal .modal-thumb { height: 110px; border-radius: 12px; overflow: hidden; margin-bottom: 12px; background: var(--bg-alt); display:flex; align-items:center; justify-content:center; }
        .modal .modal-thumb img, .modal .modal-thumb video { width:100%; height:100%; object-fit:cover; }
        .modal-actions { display:flex; gap: 8px; margin-top: 4px; }
        .field-label { font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.4px; color: var(--ink-soft); margin-bottom: 5px; display:block; }
        .detect-pill { display:inline-flex; align-items:center; gap:6px; background: var(--moss-soft); color: var(--moss-deep); font-size: 11px; font-weight: 700; padding: 6px 11px; border-radius: 999px; margin-bottom: 12px; }

        ::-webkit-scrollbar { width: 0; height: 0; }

        /* ===== Splash screen ===== */
        #splash { position: fixed; inset: 0; z-index: 9999; display: flex; flex-direction: column; align-items: center; justify-content: center; background: radial-gradient(120% 90% at 50% 8%, #1f3d24 0%, #142719 55%, #0b1710 100%); transition: opacity 0.55s ease, visibility 0.55s; }
        #splash.hide { opacity: 0; visibility: hidden; pointer-events: none; }
        #splash .splash-logo { width: 128px; height: 128px; filter: drop-shadow(0 10px 28px rgba(0,0,0,0.45)); }
        #splash .lg-bar { transform-origin: bottom center; opacity: 0; animation: barRise 0.45s ease forwards; }
        #splash .lg-bar.b1 { animation-delay: 1.55s; } #splash .lg-bar.b2 { animation-delay: 1.62s; } #splash .lg-bar.b3 { animation-delay: 1.69s; }
        #splash .lg-bar.b4 { animation-delay: 1.69s; } #splash .lg-bar.b5 { animation-delay: 1.62s; } #splash .lg-bar.b6 { animation-delay: 1.55s; }
        #splash .lg-lens { opacity: 0; transform: scale(0.6); transform-origin: 50px 58px; animation: popIn 0.5s cubic-bezier(.34,1.56,.64,1) forwards 0.15s; }
        #splash .lg-ring { opacity: 0; animation: fadeUp 0.5s ease forwards 0.35s; }
        #splash .lg-inner-leaf { opacity: 0; transform: scale(0.5); transform-origin: 50px 55px; animation: popIn 0.4s cubic-bezier(.34,1.56,.64,1) forwards 0.65s; }
        #splash .lg-mountains { opacity: 0; transform: translateY(6px); animation: fadeUp 0.5s ease forwards 0.85s; }
        #splash .lg-leaf-top { opacity: 0; transform: translateY(8px) scale(0.85); transform-origin: 55px 30px; animation: fadeUp 0.6s ease forwards 1.05s; }
        #splash .lg-birds path { opacity: 0; animation: fadeUp 0.4s ease forwards; }
        #splash .lg-birds path:nth-child(1) { animation-delay: 1.35s; }
        #splash .lg-birds path:nth-child(2) { animation-delay: 1.44s; }
        #splash .lg-birds path:nth-child(3) { animation-delay: 1.53s; }
        #splash .splash-word { opacity: 0; margin-top: 20px; font-family: 'Fraunces', serif; font-size: 30px; font-weight: 600; letter-spacing: 3px; color: #eef6ea; animation: fadeUp 0.6s ease forwards 1.9s; }
        #splash .splash-tag { opacity: 0; margin-top: 7px; font-size: 10.5px; letter-spacing: 3.5px; text-transform: uppercase; color: #a9d1a0; animation: fadeUp 0.55s ease forwards 2.35s; }
        @keyframes popIn { from { opacity: 0; transform: scale(0.55); } to { opacity: 1; transform: scale(1); } }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes barRise { from { opacity: 0; transform: scaleY(0); } to { opacity: 1; transform: scaleY(1); } }
    </style>
</head>
<body>
<div id="splash">
    <svg class="splash-logo" viewBox="0 0 100 100" fill="none">
        <rect class="lg-bar b1" x="2" y="48" width="3.4" height="18" rx="1.7" fill="#5fae5f"/>
        <rect class="lg-bar b2" x="9" y="42" width="3.4" height="30" rx="1.7" fill="#5fae5f"/>
        <rect class="lg-bar b3" x="16" y="35" width="3.4" height="44" rx="1.7" fill="#5fae5f"/>
        <rect class="lg-bar b4" x="80.6" y="35" width="3.4" height="44" rx="1.7" fill="#5fae5f"/>
        <rect class="lg-bar b5" x="87.6" y="42" width="3.4" height="30" rx="1.7" fill="#5fae5f"/>
        <rect class="lg-bar b6" x="94.6" y="48" width="3.4" height="18" rx="1.7" fill="#5fae5f"/>
        <circle class="lg-lens" cx="50" cy="58" r="29" fill="#0f2016"/>
        <circle class="lg-ring" cx="50" cy="58" r="29" fill="none" stroke="#7fc47f" stroke-width="1.4" opacity="0.55"/>
        <path class="lg-mountains" d="M25 76c6-11 15-15 25-8 8-10 17-12 25-4v12H25Z" fill="#25452a"/>
        <path class="lg-inner-leaf" d="M50 43c7 3 10 10 6 18-7-2-12-9-12-15 0-1.5 2.5-3.5 6-3Z" fill="#4fa653"/>
        <path class="lg-leaf-top" d="M50 6c15 6 21 19 14 33-4-2-8-5-10-9 6-2 8-8 5-15-5 4-9 11-7 19-7-6-9-17-5-27 1-0.5 2-1 3-1Z" fill="#3f9142"/>
        <g class="lg-birds" stroke="#12241a" stroke-width="1.7" stroke-linecap="round" fill="none">
            <path d="M69 18l4-3 4 2"/>
            <path d="M77 24l4-3 4 2"/>
            <path d="M73 13l3-2.4 3 1.6"/>
        </g>
    </svg>
    <div class="splash-word">NATURA</div>
    <div class="splash-tag">Hear Beyond Human Hearing</div>
</div>
<div id="phone-wrap">
<div id="app">
    <div class="statusbar"><span>9:41</span><span>NATURA</span></div>
    <div class="topbar">
        <svg class="mark" viewBox="0 0 100 100" fill="none">
            <rect x="2" y="48" width="3.4" height="18" rx="1.7" fill="currentColor" opacity="0.85"/>
            <rect x="9" y="42" width="3.4" height="30" rx="1.7" fill="currentColor" opacity="0.85"/>
            <rect x="16" y="35" width="3.4" height="44" rx="1.7" fill="currentColor" opacity="0.85"/>
            <rect x="80.6" y="35" width="3.4" height="44" rx="1.7" fill="currentColor" opacity="0.85"/>
            <rect x="87.6" y="42" width="3.4" height="30" rx="1.7" fill="currentColor" opacity="0.85"/>
            <rect x="94.6" y="48" width="3.4" height="18" rx="1.7" fill="currentColor" opacity="0.85"/>
            <circle cx="50" cy="58" r="29" fill="none" stroke="currentColor" stroke-width="2.2"/>
            <path d="M50 43c7 3 10 10 6 18-7-2-12-9-12-15 0-1.5 2.5-3.5 6-3Z" fill="currentColor"/>
            <path d="M50 6c15 6 21 19 14 33-4-2-8-5-10-9 6-2 8-8 5-15-5 4-9 11-7 19-7-6-9-17-5-27 1-0.5 2-1 3-1Z" fill="currentColor"/>
        </svg>
        <span>NATURA</span>
        <button id="installAppBtn" class="btn xs gold" style="display:none; margin-left:auto; font-size:10.5px; padding:3px 9px; font-weight:700; border-radius:999px; gap:4px; align-items:center;" onclick="triggerAppInstall()">
            <span>📲</span><span>Install App</span>
        </button>
    </div>

    <main>
        <!-- PAGE 1: LISTEN -->
        <section id="page-listen" class="page active">
            <div id="pwaBanner" class="pwa-install-banner">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:20px;">📲</span>
                    <div>
                        <div style="font-weight:700; font-size:11.5px; color:var(--moss-deep);">Install NATURA on Your Phone</div>
                        <div style="font-size:10px; color:var(--ink-soft);">Run full-screen like a mobile app with offline biophony</div>
                    </div>
                </div>
                <div style="display:flex; gap:6px; align-items:center;">
                    <button class="btn xs gold" style="font-size:10.5px; padding:3px 9px;" onclick="triggerAppInstall()">Install</button>
                    <button style="background:none; border:none; color:var(--ink-soft); font-size:14px; cursor:pointer; padding:2px;" onclick="document.getElementById('pwaBanner').style.display='none'">✕</button>
                </div>
            </div>

            <div class="hero">
                <svg class="leafart" viewBox="0 0 32 32" fill="none"><path d="M16 3c6 4 11 9 11 15.5A11 11 0 1 1 5 18.5C5 12 10 7 16 3Z" stroke="#fff" stroke-width="1"/></svg>
                <div class="hero-tag"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M4.9 4.9l2.8 2.8M16.3 16.3l2.8 2.8M2 12h4M18 12h4M4.9 19.1l2.8-2.8M16.3 7.7l2.8-2.8"/></svg>Field Bioacoustics</div>
                <h1>Past the edge of hearing.</h1>
                <p>Record, capture or film what's around you — NATURA analyzes it on-device and keeps it in your Album.</p>
            </div>

            <div class="section-heading">
                <div class="glyph"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="10" width="3" height="4"/><rect x="8" y="6" width="3" height="12"/><rect x="13" y="3" width="3" height="18"/><rect x="18" y="8" width="3" height="8"/></svg></div>
                <h2>Capture this session</h2>
            </div>
            <div class="capture-row">
                <div class="capture-panel">
                    <div class="label">Audio</div>
                    <div class="stage empty" id="audioStage">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3Z"/><path d="M19 11a7 7 0 0 1-14 0"/></svg>
                        <span>None</span>
                    </div>
                    <button class="btn outline block xs" onclick="toggleRecord()" id="recBtn2">Record</button>
                    <div class="status" id="audioStatus">On-device only.</div>
                </div>
                <div class="capture-panel">
                    <div class="label">Photo</div>
                    <div class="stage empty" id="camStage">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 8a2 2 0 0 1 2-2h1l1.2-1.6A1 1 0 0 1 9 4h6a1 1 0 0 1 .8.4L17 6h1a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8Z"/><circle cx="12" cy="13" r="3.4"/></svg>
                        <span>None</span>
                    </div>
                    <button class="btn outline block xs" onclick="openCamera()" id="camBtn">Camera</button>
                    <div class="status" id="camStatus">Visual context.</div>
                </div>
                <div class="capture-panel">
                    <div class="label">Video</div>
                    <div class="stage empty" id="vidStage">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="6" width="13" height="12" rx="2"/><path d="m16 10 5-3v10l-5-3Z"/></svg>
                        <span>None</span>
                    </div>
                    <button class="btn outline block xs" onclick="toggleVideo()" id="vidBtn">Record</button>
                    <div class="status" id="vidStatus">Sight + sound.</div>
                </div>
            </div>
            <div id="liveToast" class="live-toast" style="display:none;"></div>

            <div class="section-heading">
                <div class="glyph"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3Z"/><path d="M19 11a7 7 0 0 1-14 0"/></svg></div>
                <h2>Hear the unheard</h2>
            </div>
            <div class="card">
                <p class="desc">The human ear covers a limited range. NATURA reprocesses captured audio so quiet or buried detail becomes clearly audible — a real-time translation, not a claim that ultrasound is literally perceived.</p>
                <div class="toggle-row" id="listenModeRow">
                    <div class="toggle-btn active" data-mode="original" onclick="selectListenMode(this)">Original</div>
                    <div class="toggle-btn" data-mode="enhanced" onclick="selectListenMode(this)">Enhanced</div>
                    <div class="toggle-btn" data-mode="sonified" onclick="selectListenMode(this)">Sonified</div>
                </div>
                <div class="mode-explain" id="listenModeExplain"><b>Original —</b> the raw recording, unprocessed.</div>
                <select id="listenClipPicker" class="comp-name-input" onchange="playRepresentation()">
                    <option value="bee">Honeybee on hibiscus</option>
                    <option value="cricket">Night field cricket</option>
                    <option value="rain">Monsoon on teak leaves</option>
                    <option value="bat">Bat echolocation</option>
                </select>
                <audio id="reprPlayer" style="width:100%; margin-bottom:10px;" controls></audio>
                <button class="btn block" onclick="playRepresentation()">▶ Play selected representation</button>
            </div>

            <div class="section-heading">
                <div class="glyph"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg></div>
                <h2>Acoustic timeline</h2>
            </div>
            <div class="card">
                <p class="desc">Every recording gets a timeline of detected events. Tap any mark to jump there.</p>
                <div class="timeline" id="timeline"></div>
                <div class="timeline-labels"><span>0:00</span><span>0:15</span><span>0:30</span></div>
            </div>
        </section>

        <!-- PAGE 2: ALBUM -->
        <section id="page-album" class="page">
            <div class="eyebrow">Nature Album</div>
            <h1 class="display">My Nature</h1>
            <p class="page-lede">Similar recordings are grouped automatically. Tap a group to open it, or the ✕ to delete.</p>

            <div class="stat-grid">
                <div class="stat-box"><div class="stat-num" id="albumDiscoveries">4</div><div class="stat-label">Recordings</div></div>
                <div class="stat-box"><div class="stat-num" id="albumGroupsCount">4</div><div class="stat-label">Recognized groups</div></div>
            </div>

            <div class="section-heading">
                <div class="glyph"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8.5" cy="9" r="1.6"/><path d="m21 15-5-5-11 11"/></svg></div>
                <h2>Nature moments</h2>
            </div>
            <div class="field-grid" id="albumGrid"></div>
        </section>

        <!-- PAGE 2b: MOMENT DETAIL (not in bottom nav) -->
        <section id="page-detail" class="page">
            <div class="backbar"><button onclick="closeDetail()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="m15 5-7 7 7 7"/></svg></button><div class="eyebrow" style="margin:0;">Nature Moment</div></div>
            <div class="detail-hero" id="detailHero"></div>
            <div class="detail-title" id="detailTitle">—</div>
            <div class="detail-meta" id="detailMeta">—</div>

            <div class="sample-strip" id="sampleStrip"></div>

            <div class="card">
                <div class="toggle-row" id="detailModeRow">
                    <div class="toggle-btn active" data-mode="original" onclick="selectDetailMode(this)">Original</div>
                    <div class="toggle-btn" data-mode="enhanced" onclick="selectDetailMode(this)">Enhanced</div>
                    <div class="toggle-btn" data-mode="sonified" onclick="selectDetailMode(this)">Sonified</div>
                </div>
                <div class="mode-explain" id="detailModeExplain"></div>
                <audio id="detailPlayer" style="width:100%;" controls></audio>
            </div>

            <div class="card">
                <div class="layer-title">Scientific interpretation</div>
                <p class="desc" id="detailInterpretation" style="margin-bottom:0;">—</p>
            </div>

            <div style="display:flex; gap:8px;">
                <button class="btn block" id="detailLearnBtn" onclick="goLearnFromDetail()">Learn about this →</button>
                <button class="btn danger sm" onclick="deleteGroupFromDetail()">Delete group</button>
            </div>
        </section>

        <!-- PAGE 3: LEARN -->
        <section id="page-learn" class="page">
            <div class="eyebrow">Nature Interpreter &amp; Nature's Language</div>
            <h1 class="display">Understand what you heard</h1>
            <p class="page-lede">Browse by category, or record something new right now to learn what it might be.</p>

            <div class="section-heading">
                <div class="glyph"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3Z"/><path d="M19 11a7 7 0 0 1-14 0M12 18v3"/></svg></div>
                <h2>Learn a new sound</h2>
            </div>
            <div class="card">
                <p class="desc">Record something you're hearing right now — NATURA runs its on-device signature match and files it under "My Recordings" below.</p>
                <div class="stage empty" id="learnAudioStage" style="height:80px; border-radius:12px; background:var(--bg-alt); margin-bottom:10px; display:flex; align-items:center; justify-content:center;">
                    <span style="font-size:11px; color:var(--ink-soft);">No recording yet</span>
                </div>
                <button class="btn block" id="learnRecBtn" onclick="toggleLearnRecord()">● Record to learn</button>
            </div>

            <div class="cat-chip-row" id="learnChips"></div>
            <div id="learnGrid" class="field-grid" style="margin-top: 10px;"></div>
            <div id="learnDetailWrap"></div>

            <div class="section-heading">
                <div class="glyph"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 12h6M9 16h6M9 8h6M5 4h14v16H5z"/></svg></div>
                <h2>How NATURA reads it</h2>
            </div>
            <div class="card">
                <p class="desc">Method: on-device frequency + pulse-pattern signature → known bioacoustic association → interpretation. When the signature is ambiguous, NATURA reports "unclassified" instead of guessing.</p>
                <div class="layer-box grey">
                    <div class="layer-title">Honesty check</div>
                    <p>Weak or mixed signature → logged as "Unclassified sound, source unconfirmed."</p>
                </div>
            </div>
        </section>

        <!-- PAGE 4: QUEST -->
        <section id="page-quest" class="page">
            <div class="eyebrow">Nature Quest</div>
            <h1 class="display">Ten minutes in the field</h1>
            <div id="questTheme" style="font-size:12px; font-weight:700; color:var(--moss-deep); margin-bottom:4px;">Mission 1: The Pollinator's Trail</div>
            <p class="page-lede">Step outside. Each mission is checked by NATURA AI against what you actually submit — record the wrong sound or capture non-nature images and NATURA will guide you to retry.</p>

            <div class="quest-timer">
                <div>
                    <div class="time" id="questTime">10:00</div>
                    <div style="font-size:10.5px; color:var(--ink-soft);" id="questState">Not started</div>
                </div>
                <button class="btn gold sm" id="questBtn" onclick="toggleQuest()">Begin quest</button>
            </div>
            <div class="progressbar"><div id="questProgress"></div></div>

            <div id="questCelebration" style="display:none;" class="quest-celebration">
                <div style="font-size:24px; margin-bottom:4px;">🏆</div>
                <h3 style="color:var(--moss-deep); font-size:16px; margin-bottom:4px;">Quest Round Completed!</h3>
                <p style="font-size:11.5px; color:var(--ink-soft); margin-bottom:12px;">All missions verified by NATURA AI. Your Nature Moment has been saved to your Album.</p>
                <button class="btn gold block" style="font-weight:700;" onclick="startNewQuestRound()">⚡ Generate New Quest</button>
            </div>

            <div style="display:flex; justify-content:space-between; align-items:center; margin: 12px 0 10px; padding:0 2px;">
                <span style="font-size:11px; color:var(--ink-soft);">Can't find a sound or subject nearby?</span>
                <button class="btn xs outline" style="font-size:10.5px; padding:3px 9px;" onclick="skipNextQuestStep()">Skip Next Step ⏭</button>
            </div>

            <div id="questCardsWrap"></div>
            <button class="btn block" id="questSaveBtn" onclick="saveQuestMoment()" disabled>Save Nature Moment to Album</button>
            <button class="btn outline block" style="margin-top:8px;" onclick="startNewQuestRound()">⚡ Generate New Quest</button>
        </section>

        <!-- PAGE 5: COMPOSE -->
        <section id="page-compose" class="page">
            <div class="eyebrow">Nature Composer</div>
            <h1 class="display">Mix &amp; edit your soundscape</h1>
            <p class="page-lede">Blend reference field clips, or mix videos taken on the Live page into a Nature Cinema reel.</p>

            <div class="section-heading">
                <div class="glyph"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="6" width="13" height="12" rx="2"/><path d="m16 10 5-3v10l-5-3Z"/></svg></div>
                <h2>Field Video Mixer</h2>
            </div>
            <div class="card" id="videoMixerCard">
                <p class="desc">Videos recorded on the Live page appear here automatically. Select videos to mix into a seamless sequence with ambient nature soundscapes.</p>
                <div class="video-mix-grid" id="videoMixGrid"></div>
                <div class="video-mix-chips" id="videoMixChips"></div>
                <div style="margin: 10px 0 6px;">
                    <span class="field-label" style="font-size:11px; font-weight:700; color:var(--ink-soft); display:block; margin-bottom:4px;">Overlay Ambient Nature Soundscape</span>
                    <select id="videoMixTrackSelect" class="comp-name-input" style="margin-bottom:8px;">
                        <option value="none">Original Video Audio Only</option>
                        <option value="cricket">Twilight Field Crickets (48kHz Bioacoustics)</option>
                        <option value="rain">Monsoon Rain on Teak Leaves</option>
                        <option value="bee">Humming Pollinator Meadow</option>
                    </select>
                </div>
                <div style="display:flex; gap:8px; margin-bottom:8px;">
                    <button class="btn block" onclick="playVideoMix()">▶ Play Video Mix</button>
                    <button class="btn ghost sm" onclick="stopCinema()">■ Stop</button>
                </div>
                <input class="comp-name-input" id="videoMixName" type="text" placeholder="Name this video mix…" value="Field Video Mix 1">
                <button class="btn outline block" onclick="saveVideoMix()">Save Video Mix to Cinema</button>
            </div>

            <div class="section-heading">
                <div class="glyph"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V6l11-2v12"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/></svg></div>
                <h2>Field clip mixer</h2>
            </div>
            <div class="card" id="mixerCard"></div>
            <div class="card">
                <span class="field-label">Composition name</span>
                <input class="comp-name-input" id="compName" type="text" placeholder="Name this composition…" value="Morning in Chennai">
                <div style="display:flex; gap:8px;">
                    <button class="btn block" id="mixPlayBtn" onclick="toggleMixPlay()">▶ Play mix</button>
                    <button class="btn outline block" onclick="saveComposition()">Save</button>
                </div>
            </div>

            <div class="section-heading">
                <div class="glyph"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 8a2 2 0 0 1 2-2h1l1.2-1.6A1 1 0 0 1 9 4h6a1 1 0 0 1 .8.4L17 6h1a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8Z"/><circle cx="12" cy="13" r="3.4"/></svg></div>
                <h2>Nature Cinema Player</h2>
            </div>
            <div class="card">
                <p class="desc">Sequence album clips and videos into a Nature Cinema montage.</p>
                <div class="cinema-pick-list" id="cinemaPickList"></div>
                <div class="cinema-chips" id="cinemaChips"></div>
                <div class="cinema-stage" id="cinemaStage"><span class="cs-empty">Select clips or a video mix above, then Preview</span></div>
                <div style="display:flex; gap:8px; margin-bottom:10px;">
                    <button class="btn outline block sm" onclick="previewCinema()">▶ Preview</button>
                    <button class="btn ghost block sm" onclick="stopCinema()">■ Stop</button>
                </div>
                <input class="comp-name-input" id="cinemaName" type="text" placeholder="Name this cinema…" value="Field Highlights">
                <button class="btn block" onclick="saveCinema()">Save Cinema</button>
            </div>

            <div class="section-heading">
                <div class="glyph"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 20c3-1 4-4 4-7s-1-4-1-6a3 3 0 0 1 6 0c0 3-2 4-2 8s2 5 5 5"/></svg></div>
                <h2>Your journey &amp; saved reels</h2>
            </div>
            <div class="stat-grid cols-3">
                <div class="stat-box"><div class="stat-num" id="journeySessions">21</div><div class="stat-label">Sessions</div></div>
                <div class="stat-box"><div class="stat-num" id="journeyComps">0</div><div class="stat-label">Mixes</div></div>
                <div class="stat-box"><div class="stat-num" id="journeyCinemas">0</div><div class="stat-label">Cinemas</div></div>
            </div>
            <div class="card" id="savedComps"></div>
            <div class="card" id="savedCinemas" style="display:none;"></div>
        </section>
    </main>

    <nav class="bottomnav">
        <button class="active" data-page="page-listen" onclick="showPage('page-listen', this)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><path d="M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3Z"/><path d="M19 11a7 7 0 0 1-14 0M12 18v3"/></svg>
            Listen
        </button>
        <button data-page="page-album" onclick="showPage('page-album', this)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><rect x="3" y="5" width="14" height="14" rx="2"/><rect x="7" y="9" width="14" height="14" rx="2" fill="var(--bg)"/></svg>
            Album
        </button>
        <button data-page="page-learn" onclick="showPage('page-learn', this)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><path d="M4 5.5C4 4.7 4.7 4 5.5 4H12v16H5.5A1.5 1.5 0 0 1 4 18.5v-13Z"/><path d="M20 5.5c0-.8-.7-1.5-1.5-1.5H12v16h6.5a1.5 1.5 0 0 0 1.5-1.5v-13Z"/></svg>
            Learn
        </button>
        <button data-page="page-quest" onclick="showPage('page-quest', this)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><circle cx="12" cy="12" r="9"/><path d="m15 9-2 6-6 2 2-6Z"/></svg>
            Quest
        </button>
        <button data-page="page-compose" onclick="showPage('page-compose', this)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><path d="M9 18V6l11-2v12"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/></svg>
            Compose
        </button>
    </nav>

    <div class="modal-backdrop" id="saveModalBackdrop">
        <div class="modal">
            <h3>Name this recording</h3>
            <div class="detect-pill" id="modalDetectPill" style="display:none;"></div>
            <div class="modal-sub" id="modalSub">Saved to your Album with today's date.</div>
            <div class="modal-thumb" id="modalThumb"></div>
            <span class="field-label">Name</span>
            <input type="text" id="modalNameInput" placeholder="e.g. Honeybee near the gate">
            <div class="modal-actions">
                <button class="btn ghost block" onclick="closeSaveModal()">Discard</button>
                <button class="btn block" onclick="confirmSaveModal()">Save to Album</button>
            </div>
        </div>
        <div class="modal-backdrop" id="installModalBackdrop" onclick="if(event.target===this)closeInstallModal()">
        <div class="modal" style="border-radius: 22px 22px 0 0;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
                <div style="width:42px; height:42px; border-radius:12px; background:var(--moss-deep); display:flex; align-items:center; justify-content:center; color:#fff; font-size:22px;">🌿</div>
                <div>
                    <h3 style="margin:0; font-size:16px;">Install NATURA App</h3>
                    <span style="font-size:11px; color:var(--ink-soft);">Run full-screen on your phone's home screen</span>
                </div>
            </div>
            <div id="installGuideText" style="font-size:12px; line-height:1.65; color:var(--ink); margin-bottom:16px;"></div>
            <button class="btn block" onclick="closeInstallModal()">Got it</button>
        </div>
    </div>
</div>
</div>
</div>

<script>
/* ---- Splash screen: ~3.6s animated logo, then fade into the app ---- */
setTimeout(() => {
    const splash = document.getElementById('splash');
    if (splash) splash.classList.add('hide');
}, 3600);

/* =========================================================
   PWA & Mobile App Installation
   ========================================================= */
let deferredPrompt = null;
const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').catch(err => console.log('SW reg error:', err));
    });
}

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    const btn = document.getElementById('installAppBtn');
    if (btn && !isStandalone) btn.style.display = 'inline-flex';
    const banner = document.getElementById('pwaBanner');
    if (banner && !isStandalone) banner.style.display = 'flex';
});

window.addEventListener('appinstalled', () => {
    deferredPrompt = null;
    const btn = document.getElementById('installAppBtn');
    if (btn) btn.style.display = 'none';
    const banner = document.getElementById('pwaBanner');
    if (banner) banner.style.display = 'none';
});

function triggerAppInstall() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                const btn = document.getElementById('installAppBtn');
                if (btn) btn.style.display = 'none';
                const banner = document.getElementById('pwaBanner');
                if (banner) banner.style.display = 'none';
            }
            deferredPrompt = null;
        });
    } else {
        showInstallModal();
    }
}

function showInstallModal() {
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    const isAndroid = /Android/.test(navigator.userAgent);
    const textEl = document.getElementById('installGuideText');
    if (isIOS) {
        textEl.innerHTML = '<b>Install on iPhone / iPad (Safari):</b><br>' +
            '1. Tap the <b>Share</b> button <span style="font-size:15px;">⎋</span> at bottom of Safari.<br>' +
            '2. Scroll down and tap <b>"Add to Home Screen"</b> <span style="font-size:15px;">⊞</span>.<br>' +
            '3. Tap <b>"Add"</b> at the top right.<br><br>' +
            '<span style="color:var(--moss-deep); font-weight:600;">NATURA will install directly as a native app on your home screen!</span>';
    } else if (isAndroid) {
        textEl.innerHTML = '<b>Install on Android (Chrome / Edge):</b><br>' +
            '1. Tap the menu <b>⋮</b> (three dots) at top right.<br>' +
            '2. Tap <b>"Install app"</b> or <b>"Add to Home screen"</b>.<br>' +
            '3. Tap <b>"Install"</b>.<br><br>' +
            '<span style="color:var(--moss-deep); font-weight:600;">Android will compile a WebAPK with its own launcher icon and run full-screen!</span>';
    } else {
        textEl.innerHTML = '<b>Install on Mobile or Desktop:</b><br>' +
            '1. Open this link on your phone (Chrome, Safari, or Edge).<br>' +
            '2. Tap the <b>"Install App"</b> button or browser menu &rarr; <b>"Install App"</b>.<br>' +
            '3. Confirm to install NATURA to your home screen.<br><br>' +
            '<span style="color:var(--moss-deep); font-weight:600;">Runs seamlessly without browser address bars!</span>';
    }
    document.getElementById('installModalBackdrop').classList.add('open');
}

function closeInstallModal() {
    document.getElementById('installModalBackdrop').classList.remove('open');
}

if (!isStandalone) {
    setTimeout(() => {
        const btn = document.getElementById('installAppBtn');
        if (btn) btn.style.display = 'inline-flex';
        const banner = document.getElementById('pwaBanner');
        if (banner) banner.style.display = 'flex';
    }, 3800);
}

/* =========================================================
   Reference field clips (real audio files served by the app)
   ========================================================= */
const CLIPS = {
    bee:     { label: "Honeybee on hibiscus", place: "Chennai · 06:42", url: "/audio/bee",     scene: "bee",     category: "bee" },
    cricket: { label: "Night field cricket",  place: "Backyard · 21:10", url: "/audio/cricket", scene: "cricket", category: "cricket" },
    rain:    { label: "Monsoon on teak leaves", place: "Coorg · 16:20", url: "/audio/rain",     scene: "rain",    category: "rain" },
    bat:     { label: "Bat echolocation",     place: "Auroville · 20:40", url: "/audio/bat",   scene: "night",   category: "bat" },
};

const CATEGORY_META = {
    bee:     { label: "Bee-like hum",        scene: "bee",     learn: "insects" },
    cricket: { label: "Cricket / insect chirp", scene: "cricket", learn: "insects" },
    bird:    { label: "Bird song / whistle", scene: "generic", learn: "insects" },
    rain:    { label: "Rain / wind ambience", scene: "rain",    learn: "weather" },
    bat:     { label: "High-frequency bat echolocation", scene: "night", learn: "night" },
    foliage: { label: "Botanical foliage",   scene: "leaf",    learn: "plants" },
    flower:  { label: "Floral blossom",      scene: "bee",     learn: "plants" },
    sighting:{ label: "Field sighting",      scene: "leaf",    learn: null },
    unknown: { label: "Unclassified sound",  scene: "generic", learn: null },
};

/* Illustrated scene art (no emoji/icons) built from layered gradients + shapes */
const SCENES = {
    bee: '<svg class="scene" viewBox="0 0 200 120" preserveAspectRatio="xMidYMid slice"><rect width="200" height="120" fill="#7a2740"/><ellipse cx="150" cy="20" rx="90" ry="60" fill="#c9506e" opacity="0.55"/><ellipse cx="60" cy="90" rx="80" ry="50" fill="#e88ea0" opacity="0.5"/><circle cx="100" cy="60" r="26" fill="#f0c23a" opacity="0.9"/><circle cx="100" cy="60" r="26" fill="#3a2a12" opacity="0.35"/><ellipse cx="90" cy="52" rx="10" ry="6" fill="#fff" opacity="0.4"/></svg>',
    cricket: '<svg class="scene" viewBox="0 0 200 120" preserveAspectRatio="xMidYMid slice"><rect width="200" height="120" fill="#0f1c0c"/><ellipse cx="40" cy="20" rx="60" ry="40" fill="#22331a" opacity="0.8"/><circle cx="165" cy="20" r="14" fill="#eee9c9" opacity="0.85"/><ellipse cx="120" cy="95" rx="100" ry="45" fill="#233d1c" opacity="0.9"/><ellipse cx="120" cy="95" rx="26" ry="14" fill="#39531f"/></svg>',
    rain: '<svg class="scene" viewBox="0 0 200 120" preserveAspectRatio="xMidYMid slice"><rect width="200" height="120" fill="#28495e"/><ellipse cx="60" cy="15" rx="110" ry="45" fill="#8fb4c9" opacity="0.55"/><ellipse cx="150" cy="90" rx="90" ry="55" fill="#1e3a4a" opacity="0.7"/><path d="M20 40 10 60M45 30 35 55M70 45 60 68M95 25 85 50M120 40 110 62M145 30 135 55M170 45 160 68" stroke="#cfe3ee" stroke-width="2" opacity="0.6"/></svg>',
    night: '<svg class="scene" viewBox="0 0 200 120" preserveAspectRatio="xMidYMid slice"><rect width="200" height="120" fill="#1a1030"/><circle cx="150" cy="25" r="16" fill="#e9d9a8" opacity="0.85"/><ellipse cx="70" cy="100" rx="120" ry="40" fill="#120a22"/><path d="M60 55c-16-20-48-20-56 4 16-4 28 4 32 16-12 0-24 8-28 20 16 0 28-6 36-16 8 10 20 16 36 16-4-12-16-20-28-20 4-12 16-20 32-16-8-24-40-24-56-4Z" fill="#3a2560" opacity="0.85"/></svg>',
    leaf: '<svg class="scene" viewBox="0 0 200 120" preserveAspectRatio="xMidYMid slice"><rect width="200" height="120" fill="#1f3d24"/><ellipse cx="40" cy="20" rx="90" ry="45" fill="#3f6b42" opacity="0.6"/><ellipse cx="160" cy="95" rx="100" ry="50" fill="#6c7a48" opacity="0.55"/><path d="M100 20c30 10 30 70 0 90-30-20-30-80 0-90Z" fill="#294f2b" opacity="0.8"/></svg>',
    generic: '<svg class="scene" viewBox="0 0 200 120" preserveAspectRatio="xMidYMid slice"><rect width="200" height="120" fill="#3c5c37"/><ellipse cx="140" cy="20" rx="100" ry="55" fill="#6c7a48" opacity="0.5"/><ellipse cx="40" cy="100" rx="90" ry="45" fill="#2a4a2c" opacity="0.6"/></svg>',
};
function sceneArt(key) { return SCENES[key] || SCENES.generic; }

const MODE_EXPLAIN = {
    original: "<b>Original —</b> the raw recording, unprocessed.",
    enhanced: "<b>Enhanced —</b> background hiss filtered out and the signal normalized. Listen for a cleaner, less noisy version at the same pitch.",
    sonified: "<b>Sonified —</b> faint or buried detail is boosted so quiet moments become clearly audible, without blowing out the loud parts. This reveals information, it doesn't invent it.",
};

/* =========================================================
   On-device bioacoustic signature match — FFT-based spectral analysis.
   Distinguishes bee wingbeat fundamental (160–380 Hz + harmonics),
   cricket stridulation (4,000–8,000 Hz pulsed peaks),
   ultrasound (>12 kHz), and broadband weather.
   ========================================================= */
let audioCtx = null;
function ensureCtx() { if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)(); return audioCtx; }

function computeRMS(data) {
    let sum = 0;
    for (let i = 0; i < data.length; i++) sum += data[i] * data[i];
    return Math.sqrt(sum / data.length);
}

function fftInPlace(re, im) {
    const n = re.length;
    for (let i = 1, j = 0; i < n; i++) {
        let bit = n >> 1;
        for (; j & bit; bit >>= 1) j ^= bit;
        j ^= bit;
        if (i < j) { let t = re[i]; re[i] = re[j]; re[j] = t; t = im[i]; im[i] = im[j]; im[j] = t; }
    }
    for (let len = 2; len <= n; len <<= 1) {
        const ang = -2 * Math.PI / len;
        const wr0 = Math.cos(ang), wi0 = Math.sin(ang);
        for (let i = 0; i < n; i += len) {
            let curWr = 1, curWi = 0;
            for (let j = 0; j < len / 2; j++) {
                const ur = re[i + j], ui = im[i + j];
                const half = i + j + len / 2;
                const vr = re[half] * curWr - im[half] * curWi;
                const vi = re[half] * curWi + im[half] * curWr;
                re[i + j] = ur + vr; im[i + j] = ui + vi;
                re[half] = ur - vr; im[half] = ui - vi;
                const nwr = curWr * wr0 - curWi * wi0, nwi = curWr * wi0 + curWi * wr0;
                curWr = nwr; curWi = nwi;
            }
        }
    }
}
function largestPow2LE(n) { let p = 1; while (p * 2 <= n) p *= 2; return p; }

function analyzeSpectrum(data, sampleRate) {
    const winSize = Math.max(512, Math.min(4096, largestPow2LE(data.length)));
    if (winSize < 512) return { centroid: 0, flatness: 0, domFreq: 0, beeRatio: 0, cricketRatio: 0 };
    const numWindows = Math.max(1, Math.min(12, Math.floor(data.length / winSize)));
    const half = winSize / 2;
    const magSum = new Float64Array(half + 1);
    const window = new Float64Array(winSize);
    for (let w = 0; w < winSize; w++) window[w] = 0.5 - 0.5 * Math.cos((2 * Math.PI * w) / (winSize - 1)); // Hann
    for (let n = 0; n < numWindows; n++) {
        const offset = n * winSize;
        const re = new Float64Array(winSize), im = new Float64Array(winSize);
        for (let i = 0; i < winSize; i++) re[i] = data[offset + i] * window[i];
        fftInPlace(re, im);
        for (let k = 0; k <= half; k++) magSum[k] += Math.hypot(re[k], im[k]);
    }
    const mag = magSum.map(v => v / numWindows);
    const freqBin = sampleRate / winSize;
    let sumMag = 0, sumFreqMag = 0, sumLogMag = 0;
    let maxAudibleMag = 0, domFreq = 0;
    let beeBandMag = 0, cricketBandMag = 0;
    const eps = 1e-9;
    for (let k = 1; k <= half; k++) { // skip DC bin
        const freq = k * freqBin;
        const m = mag[k];
        sumMag += m;
        sumFreqMag += freq * m;
        sumLogMag += Math.log(m + eps);
        if (freq >= 80 && m > maxAudibleMag) {
            maxAudibleMag = m;
            domFreq = freq;
        }
        if (freq >= 160 && freq <= 380) beeBandMag += m;
        if (freq >= 4000 && freq <= 8000) cricketBandMag += m;
    }
    const centroid = sumMag > 0 ? sumFreqMag / sumMag : 0;
    const meanMag = sumMag / half;
    const flatness = meanMag > 0 ? Math.exp(sumLogMag / half) / meanMag : 0;
    const beeRatio = sumMag > 0 ? beeBandMag / sumMag : 0;
    const cricketRatio = sumMag > 0 ? cricketBandMag / sumMag : 0;
    return { centroid, flatness, domFreq, beeRatio, cricketRatio };
}

async function classifyAudioUrl(url) {
    try {
        const ctx = ensureCtx();
        const resp = await fetch(url);
        const arr = await resp.arrayBuffer();
        const buf = await ctx.decodeAudioData(arr);
        const data = buf.getChannelData(0);
        const rms = computeRMS(data);
        if (rms < 0.003) return { category: 'unknown', confidence: 50, centroid: 0, flatness: 0, domFreq: 0, reason: 'too quiet' };
        
        const { centroid, flatness, domFreq, beeRatio, cricketRatio } = analyzeSpectrum(data, buf.sampleRate);
        
        // Try calling the backend BioacousticClassifier
        try {
            const step = Math.max(1, Math.floor(data.length / 2048));
            const pcmSample = [];
            for (let i = 0; i < data.length; i += step) pcmSample.push(data[i]);
            const apiResp = await fetch('/api/classify_audio', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pcm: pcmSample, sample_rate: buf.sampleRate, dom_freq: domFreq, centroid, flatness })
            });
            if (apiResp.ok) {
                const apiData = await apiResp.json();
                if (apiData.status === 'ok') {
                    return {
                        category: apiData.category,
                        confidence: apiData.confidence,
                        label: apiData.label,
                        centroid: Math.round(centroid),
                        domFreq: Math.round(domFreq),
                        flatness: +flatness.toFixed(2)
                    };
                }
            }
        } catch(netErr) { /* fallback to local classification */ }
        
        let category = 'unknown', confidence = 55;
        // Discriminating decision tree:
        if (centroid > 12000 || domFreq >= 16000) {
            category = 'bat'; confidence = 89;
        } else if ((domFreq >= 160 && domFreq <= 380) || (beeRatio > 0.09 && domFreq < 1200)) {
            category = 'bee'; confidence = (domFreq >= 210 && domFreq <= 270) ? 93 : 88;
        } else if ((domFreq >= 4000 && domFreq <= 8000) || (cricketRatio > 0.09 && domFreq > 3000)) {
            category = 'cricket'; confidence = 91;
        } else if (domFreq >= 1200 && domFreq <= 3800) {
            category = 'bird'; confidence = 86;
        } else if (flatness > 0.72) {
            category = 'rain'; confidence = Math.round(72 + Math.min((flatness - 0.72) / 0.2, 1) * 20);
        } else {
            category = 'unknown'; confidence = 52;
        }
        confidence = Math.max(50, Math.min(96, confidence));
        const meta = CATEGORY_META[category] || CATEGORY_META.unknown;
        return {
            category,
            confidence,
            label: meta.label,
            centroid: Math.round(centroid),
            domFreq: Math.round(domFreq),
            flatness: +flatness.toFixed(2)
        };
    } catch (err) {
        return { category: 'unknown', confidence: 50, centroid: 0, flatness: 0, domFreq: 0 };
    }
}

async function classifyImageData(canvas) {
    const anaCanvas = document.createElement('canvas');
    anaCanvas.width = 64; anaCanvas.height = 64;
    const anaCtx = anaCanvas.getContext('2d');
    anaCtx.drawImage(canvas, 0, 0, 64, 64);
    const imgData = anaCtx.getImageData(0, 0, 64, 64);
    const rgba = Array.from(imgData.data);
    
    // Call backend VisionClassifier
    try {
        const resp = await fetch('/api/classify_image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rgba, width: 64, height: 64 })
        });
        if (resp.ok) {
            const data = await resp.json();
            if (data.status === 'ok') return data;
        }
    } catch (e) { /* local fallback */ }
    
    // Client-side computer vision heuristics
    let floralCount = 0, greenCount = 0, edgeDiff = 0;
    const pixels = 64 * 64;
    for (let i = 0; i < rgba.length; i += 4) {
        const r = rgba[i], g = rgba[i+1], b = rgba[i+2];
        const exg = (2.0 * g - r - b) / (r + g + b + 1e-5);
        if (exg > 0.12 && g > 40) greenCount++;
        // Floral petal colors (yellow, magenta, violet, warm red/pink)
        if ((r > 120 && g > 100 && b < 100 && (r+g) > 2.2*b) || 
            (r > 90 && b > 100 && g < r*0.95 && g < b*0.95) || 
            (r > 130 && g < r*0.8 && b < r*0.8)) {
            floralCount++;
        }
        if (i > 4) edgeDiff += Math.abs((r+g+b) - (rgba[i-4]+rgba[i-3]+rgba[i-2]));
    }
    const edgeVar = edgeDiff / pixels;
    const greenRatio = greenCount / pixels;
    const floralRatio = floralCount / pixels;
    
    if (edgeVar < 18 && greenRatio < 0.08 && floralRatio < 0.03) {
        return { category: 'non_botanical', confidence: 85, label: 'Non-botanical / Flat surface', reason: 'Scene lacks botanical structure, foliage, or floral pigmentation.' };
    }
    if (floralRatio > 0.05 || (floralRatio > 0.02 && greenRatio > 0.12)) {
        return { category: 'flower', confidence: 91, label: 'Floral Blossom / Flower', reason: 'Vibrant petal pigmentation confirmed.' };
    }
    if (greenRatio > 0.10 || edgeVar > 35) {
        return { category: 'foliage', confidence: 88, label: 'Botanical Foliage / Canopy', reason: 'Photosynthetic green leaf index confirmed.' };
    }
    return { category: 'non_botanical', confidence: 75, label: 'Non-nature / Unconfirmed', reason: 'Scene does not show clear flora or pollinators.' };
}

/* =========================================================
   Audio DSP graph: Original / Enhanced / Sonified
   ========================================================= */
const nodeGraphs = new WeakMap();
function applyMode(audioEl, mode) {
    const ctx = ensureCtx();
    let graph = nodeGraphs.get(audioEl);
    if (!graph) {
        const source = ctx.createMediaElementSource(audioEl);
        const filter = ctx.createBiquadFilter();
        const compressor = ctx.createDynamicsCompressor();
        const gain = ctx.createGain();
        source.connect(filter); filter.connect(compressor); compressor.connect(gain); gain.connect(ctx.destination);
        graph = { source, filter, compressor, gain };
        nodeGraphs.set(audioEl, graph);
    }
    if (ctx.state === 'suspended') ctx.resume();
    audioEl.playbackRate = 1;
    if (mode === 'original') {
        graph.filter.type = 'allpass'; graph.filter.frequency.value = 20000;
        graph.compressor.threshold.value = 0; graph.compressor.ratio.value = 1;
        graph.gain.gain.value = 1;
    } else if (mode === 'enhanced') {
        graph.filter.type = 'bandpass'; graph.filter.frequency.value = 2200; graph.filter.Q.value = 0.75;
        graph.compressor.threshold.value = 0; graph.compressor.ratio.value = 1;
        graph.gain.gain.value = 1.7;
    } else if (mode === 'sonified') {
        graph.filter.type = 'allpass'; graph.filter.frequency.value = 20000;
        graph.compressor.threshold.value = -55; graph.compressor.ratio.value = 14;
        graph.compressor.attack.value = 0.003; graph.compressor.release.value = 0.25;
        graph.gain.gain.value = 2.3;
    }
}

/* =========================================================
   Album groups — similar recordings are grouped by category
   ========================================================= */
let albumGroups = [
    { id: 'g-bee', category: 'bee', samples: [ { id: 's-bee', name: 'Honeybee on hibiscus', date: 'Field reference', place: 'Chennai · 06:42', audioUrl: CLIPS.bee.url, photo: null, video: null, badge: null, interpretation: 'Apis mellifera wingbeat at ~240 Hz fundamental frequency, matching foraging flight. 91% signature match.' } ] },
    { id: 'g-cricket', category: 'cricket', samples: [ { id: 's-cricket', name: 'Night field cricket', date: 'Field reference', place: 'Backyard · 21:10', audioUrl: CLIPS.cricket.url, photo: null, video: null, badge: null, interpretation: 'Regular stridulation pulses consistent with a calling male cricket. 87% signature match.' } ] },
    { id: 'g-rain', category: 'rain', samples: [ { id: 's-rain', name: 'Monsoon on teak leaves', date: 'Field reference', place: 'Coorg · 16:20', audioUrl: CLIPS.rain.url, photo: null, video: null, badge: null, interpretation: 'Broadband percussive texture consistent with rainfall on broad-leaf canopy. 95% signature match.' } ] },
    { id: 'g-bat', category: 'bat', samples: [ { id: 's-bat', name: 'Bat echolocation', date: 'Field reference', place: 'Auroville · 20:40', audioUrl: CLIPS.bat.url, photo: null, video: null, badge: null, interpretation: 'Ultrasonic frequency sweep, sonified to audible range. 78% signature match, species unconfirmed.' } ] },
];
let idSeq = 0;
function newId(prefix) { return prefix + '-' + (idSeq++) + '-' + Date.now().toString(36); }

function sampleThumb(sample, category) {
    if (sample.photo) return '<img src="'+sample.photo+'">';
    if (sample.videoThumb) return '<img src="'+sample.videoThumb+'">';
    if (sample.video) return '<video src="'+sample.video+'" muted></video>';
    return sceneArt((CATEGORY_META[category] || CATEGORY_META.unknown).scene);
}
function groupLatestDate(group) { return group.samples[0] ? group.samples[0].date : ''; }
function findGroup(category) { return albumGroups.find(g => g.category === category); }

function addSampleToAlbum(category, sample) {
    let group = findGroup(category);
    if (!group) { group = { id: newId('g'), category, samples: [] }; albumGroups.unshift(group); }
    group.samples.unshift(sample);
    renderAlbum();
    return group;
}

function renderAlbum() {
    const grid = document.getElementById('albumGrid');
    grid.innerHTML = '';
    let totalSamples = 0;
    albumGroups.forEach(group => {
        totalSamples += group.samples.length;
        const meta = CATEGORY_META[group.category] || CATEGORY_META.unknown;
        const fig = document.createElement('figure');
        fig.className = 'field-card';
        const hasQuest = group.samples.some(s => s.badge === 'Quest');
        const badge = hasQuest ? '<span class="badge">QUEST</span>' : '';
        fig.innerHTML = '<div class="field-art">'+sampleThumb(group.samples[0], group.category)+badge+
            '<button class="del-btn" onclick="event.stopPropagation(); deleteGroup(\''+group.id+'\')"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M6 6l12 12M18 6 6 18"/></svg></button></div>' +
            '<figcaption>'+meta.label+'</figcaption><div class="sub">'+group.samples.length+' recording'+(group.samples.length>1?'s':'')+' · '+groupLatestDate(group)+'</div>';
        fig.onclick = () => openDetail(group.id);
        grid.appendChild(fig);
    });
    document.getElementById('albumDiscoveries').textContent = totalSamples;
    document.getElementById('albumGroupsCount').textContent = albumGroups.length;
}
renderAlbum();

function deleteGroup(groupId) {
    albumGroups = albumGroups.filter(g => g.id !== groupId);
    renderAlbum();
}
function deleteGroupFromDetail() { if (detailGroupId) { deleteGroup(detailGroupId); closeDetail(); } }
function deleteSample(groupId, sampleId) {
    const group = albumGroups.find(g => g.id === groupId);
    if (!group) return;
    group.samples = group.samples.filter(s => s.id !== sampleId);
    if (group.samples.length === 0) { albumGroups = albumGroups.filter(g => g.id !== groupId); renderAlbum(); closeDetail(); return; }
    renderAlbum();
    openDetail(groupId);
}

/* =========================================================
   Navigation
   ========================================================= */
let lastMainPage = 'page-listen';
function showPage(id, btn) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    document.querySelectorAll('.bottomnav button').forEach(b => b.classList.remove('active'));
    if (btn) { btn.classList.add('active'); lastMainPage = id; }
    document.querySelector('main').scrollTop = 0;
}
function goToPage(id) {
    const btn = document.querySelector('.bottomnav button[data-page="' + id + '"]');
    showPage(id, btn);
}
function showLiveToast(msg, targetPageId) {
    const toast = document.getElementById('liveToast');
    if (!toast) return;
    toast.innerHTML = '<span>' + msg + '</span>' +
        (targetPageId ? '<button class="btn xs gold" style="padding:3px 8px; font-size:10px; flex-shrink:0;" onclick="goToPage(\'' + targetPageId + '\')">Open Compose →</button>' : '') +
        '<button style="background:none;border:none;color:#fff;font-size:16px;cursor:pointer;line-height:1;margin-left:4px;" onclick="this.parentElement.style.display=\'none\'">×</button>';
    toast.style.display = 'flex';
    setTimeout(() => { if (toast) toast.style.display = 'none'; }, 7000);
}

(function buildTimeline() {
    const el = document.getElementById('timeline');
    const heights = [20, 35, 55, 30, 70, 45, 60, 25, 80, 40, 30, 65, 20, 50, 35];
    const hotIndex = 8;
    heights.forEach((h, i) => {
        const tick = document.createElement('div');
        tick.className = 'tick' + (i === hotIndex ? ' hot' : '');
        tick.style.height = h + '%';
        tick.title = 'Event at ' + (i * 2) + 's';
        tick.onclick = () => { const p = document.getElementById('reprPlayer'); p.currentTime = 0; p.play().catch(()=>{}); };
        el.appendChild(tick);
    });
})();

/* ---- Listen page representation player ---- */
let listenMode = 'original';
function selectListenMode(el) {
    el.parentElement.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
    el.classList.add('active');
    listenMode = el.dataset.mode;
    document.getElementById('listenModeExplain').innerHTML = MODE_EXPLAIN[listenMode];
    playRepresentation();
}
function playRepresentation() {
    const clipKey = document.getElementById('listenClipPicker').value;
    const player = document.getElementById('reprPlayer');
    if (player.dataset.clip !== clipKey) { player.src = CLIPS[clipKey].url; player.dataset.clip = clipKey; }
    applyMode(player, listenMode);
    player.play().catch(()=>{});
}

/* ---- Album detail player ---- */
let detailMode = 'original';
let detailGroupId = null;
let detailSampleId = null;
function openDetail(groupId) {
    detailGroupId = groupId;
    const group = albumGroups.find(g => g.id === groupId);
    if (!group) return;
    detailSampleId = group.samples[0].id;
    renderSampleStrip();
    loadDetailSample();
    showPage('page-detail', null);
}
function renderSampleStrip() {
    const group = albumGroups.find(g => g.id === detailGroupId);
    const strip = document.getElementById('sampleStrip');
    strip.innerHTML = '';
    group.samples.forEach(s => {
        const chip = document.createElement('div');
        chip.className = 'sample-chip' + (s.id === detailSampleId ? ' active' : '');
        chip.innerHTML = '<div class="sc-art">'+sampleThumb(s, group.category)+'</div><div class="sc-label">'+s.date.split(' · ')[0]+'</div><button class="sc-x">×</button>';
        chip.querySelector('.sc-art').onclick = () => { detailSampleId = s.id; renderSampleStrip(); loadDetailSample(); };
        chip.querySelector('.sc-x').onclick = (e) => { e.stopPropagation(); deleteSample(group.id, s.id); };
        strip.appendChild(chip);
    });
}
function loadDetailSample() {
    const group = albumGroups.find(g => g.id === detailGroupId);
    const sample = group.samples.find(s => s.id === detailSampleId);
    const meta = CATEGORY_META[group.category] || CATEGORY_META.unknown;
    document.getElementById('detailHero').innerHTML = sample.video ? '<video src="'+sample.video+'" controls></video>' : sampleThumb(sample, group.category);
    document.getElementById('detailTitle').textContent = sample.name;
    document.getElementById('detailMeta').textContent = sample.place + ' · ' + sample.date;
    document.getElementById('detailInterpretation').textContent = sample.interpretation;
    document.querySelectorAll('#detailModeRow .toggle-btn').forEach(b => b.classList.toggle('active', b.dataset.mode === 'original'));
    detailMode = 'original';
    document.getElementById('detailModeExplain').innerHTML = MODE_EXPLAIN.original;
    const player = document.getElementById('detailPlayer');
    if (sample.audioUrl) {
        player.style.display = '';
        player.src = sample.audioUrl; player.dataset.clip = sample.id;
        applyMode(player, 'original');
    } else { player.style.display = 'none'; }
    document.getElementById('detailLearnBtn').dataset.learn = meta.learn || '';
    document.getElementById('detailLearnBtn').style.display = meta.learn ? '' : 'none';
}
function closeDetail() { showPage(lastMainPage, document.querySelector('.bottomnav button[data-page="'+lastMainPage+'"]')); }
function selectDetailMode(el) {
    el.parentElement.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
    el.classList.add('active');
    detailMode = el.dataset.mode;
    document.getElementById('detailModeExplain').innerHTML = MODE_EXPLAIN[detailMode];
    const player = document.getElementById('detailPlayer');
    applyMode(player, detailMode);
    player.play().catch(()=>{});
}
function goLearnFromDetail() {
    const cat = document.getElementById('detailLearnBtn').dataset.learn;
    if (!cat || !LEARN_CATEGORIES[cat]) return;
    currentCat = cat;
    buildLearnChips(); buildLearnGrid();
    showPage('page-learn', document.querySelector('.bottomnav button[data-page="page-learn"]'));
}

/* =========================================================
   Save-recording modal
   ========================================================= */
let pendingSave = null;
function openSaveModal({ audioUrl, photo, video, videoThumb, category, confidence, place, defaultName, badge, onSaved }) {
    pendingSave = { audioUrl, photo, video, videoThumb, category: category || 'unknown', place: place || 'Current location', defaultName, badge, onSaved };
    const pill = document.getElementById('modalDetectPill');
    if (audioUrl && category && category !== 'unknown') {
        const meta = CATEGORY_META[category] || CATEGORY_META.unknown;
        pill.style.display = 'inline-flex';
        pill.textContent = 'Detected: ' + meta.label + (confidence ? ' · ' + confidence + '% match' : '');
    } else { pill.style.display = 'none'; }
    document.getElementById('modalSub').textContent = "Saved to your Album with today's date. Similar recordings are grouped together.";
    document.getElementById('modalNameInput').value = defaultName || '';
    const thumb = document.getElementById('modalThumb');
    if (video) thumb.innerHTML = '<video src="'+video+'" muted autoplay loop></video>';
    else if (photo) thumb.innerHTML = '<img src="'+photo+'">';
    else thumb.innerHTML = sceneArt((CATEGORY_META[pendingSave.category] || CATEGORY_META.unknown).scene);
    document.getElementById('saveModalBackdrop').classList.add('open');
    setTimeout(() => document.getElementById('modalNameInput').focus(), 50);
}
function closeSaveModal() { document.getElementById('saveModalBackdrop').classList.remove('open'); pendingSave = null; }
function confirmSaveModal() {
    if (!pendingSave) return;
    const name = document.getElementById('modalNameInput').value.trim() || pendingSave.defaultName || 'Untitled recording';
    const now = new Date();
    const dateStr = now.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) + ' · ' + now.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
    const meta = CATEGORY_META[pendingSave.category] || CATEGORY_META.unknown;
    const sample = {
        id: newId('s'), name, date: dateStr, place: pendingSave.place,
        audioUrl: pendingSave.audioUrl || null, photo: pendingSave.photo || null, video: pendingSave.video || null, videoThumb: pendingSave.videoThumb || null,
        badge: pendingSave.badge || null,
        interpretation: pendingSave.audioUrl ? ("On-device signature matched to: " + meta.label + ". Compare Original, Enhanced and Sonified above to hear how the match was reached.") : "Captured by you — filed as a field sighting.",
    };
    const group = addSampleToAlbum(pendingSave.category, sample);
    if (pendingSave.video) {
        const existing = recordedVideos.find(v => v.video === pendingSave.video);
        if (existing) { existing.name = name; }
        renderVideoMixer();
    }
    renderCinemaPickList();
    if (pendingSave.onSaved) pendingSave.onSaved(sample, group);
    closeSaveModal();
}

/* =========================================================
   Audio recording (Listen page)
   ========================================================= */
let mediaRecorder = null, audioChunks = [], isRecording = false;
async function toggleRecord() {
    const audioStage = document.getElementById('audioStage');
    const audioStatus = document.getElementById('audioStatus');
    const recBtn2 = document.getElementById('recBtn2');
    if (isRecording) { mediaRecorder.stop(); isRecording = false; recBtn2.textContent = 'Record'; return; }
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) { audioStatus.textContent = 'Microphone not available.'; return; }
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioChunks = [];
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
        mediaRecorder.onstop = async () => {
            stream.getTracks().forEach(t => t.stop());
            const blob = new Blob(audioChunks, { type: 'audio/webm' });
            const url = URL.createObjectURL(blob);
            audioStage.classList.remove('empty');
            audioStage.innerHTML = '<audio controls src="' + url + '"></audio>';
            audioStatus.textContent = 'Analyzing…';
            const result = await classifyAudioUrl(url);
            audioStatus.textContent = 'Recorded.';
            const meta = CATEGORY_META[result.category] || CATEGORY_META.unknown;
            openSaveModal({ audioUrl: url, photo: lastPhotoDataUrl, category: result.category, confidence: result.confidence, defaultName: meta.label, place: 'Current location', onSaved: () => { audioStatus.textContent = 'Saved to Album.'; } });
        };
        mediaRecorder.start();
        isRecording = true;
        recBtn2.textContent = 'Stop';
        audioStage.classList.add('empty');
        audioStage.innerHTML = '<div class="bars"><i style="animation-delay:0s"></i><i style="animation-delay:.1s"></i><i style="animation-delay:.2s"></i><i style="animation-delay:.3s"></i><i style="animation-delay:.15s"></i><i style="animation-delay:.25s"></i></div>';
        audioStatus.textContent = 'Listening…';
    } catch (err) { audioStatus.textContent = 'Microphone permission denied.'; }
}

/* ---- Camera photo (Listen page) ---- */
let camStream = null, lastPhotoDataUrl = null;
async function openCamera() {
    const camStage = document.getElementById('camStage');
    const camStatus = document.getElementById('camStatus');
    const camBtn = document.getElementById('camBtn');
    if (camBtn.textContent === 'Capture') {
        const video = camStage.querySelector('video');
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth || 320; canvas.height = video.videoHeight || 240;
        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
        lastPhotoDataUrl = canvas.toDataURL('image/jpeg', 0.85);
        if (camStream) camStream.getTracks().forEach(t => t.stop());
        camStage.classList.remove('empty');
        camStage.innerHTML = '<img src="'+lastPhotoDataUrl+'">';
        camBtn.textContent = 'Camera';
        camStatus.textContent = 'Captured.';
        openSaveModal({ photo: lastPhotoDataUrl, category: 'sighting', defaultName: 'Field sighting', place: 'Current location', onSaved: () => { camStatus.textContent = 'Saved to Album.'; } });
        return;
    }
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) { camStatus.textContent = 'Camera not available.'; return; }
    try {
        camStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
        const video = document.createElement('video'); video.autoplay = true; video.playsInline = true; video.srcObject = camStream;
        camStage.classList.remove('empty'); camStage.innerHTML = ''; camStage.appendChild(video);
        camBtn.textContent = 'Capture'; camStatus.textContent = 'Live — tap Capture.';
    } catch (err) { camStatus.textContent = 'Camera permission denied.'; }
}

/* ---- Video recording (Listen page) ---- */
let vidRecorder = null, vidChunks = [], vidStream = null, isVidRecording = false;
async function toggleVideo() {
    const vidStage = document.getElementById('vidStage');
    const vidStatus = document.getElementById('vidStatus');
    const vidBtn = document.getElementById('vidBtn');
    if (isVidRecording) { vidRecorder.stop(); isVidRecording = false; vidBtn.textContent = 'Record'; return; }
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) { vidStatus.textContent = 'Camera not available.'; return; }
    try {
        vidStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: true });
        vidChunks = [];
        const liveVideo = document.createElement('video'); liveVideo.autoplay = true; liveVideo.muted = true; liveVideo.playsInline = true; liveVideo.srcObject = vidStream;
        vidStage.classList.remove('empty'); vidStage.innerHTML = ''; vidStage.appendChild(liveVideo);
        vidRecorder = new MediaRecorder(vidStream);
        vidRecorder.ondataavailable = e => vidChunks.push(e.data);
        vidRecorder.onstop = () => {
            vidStream.getTracks().forEach(t => t.stop());
            const blob = new Blob(vidChunks, { type: 'video/webm' });
            const url = URL.createObjectURL(blob);
            vidStage.innerHTML = '<video src="'+url+'" controls></video>';
            vidStatus.textContent = 'Recorded.';

            const vidItem = {
                id: newId('vid'),
                name: 'Field Video ' + (recordedVideos.length + 1),
                video: url,
                videoThumb: null,
                date: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                category: 'sighting'
            };
            recordedVideos.unshift(vidItem);
            renderVideoMixer();
            renderCinemaPickList();
            showLiveToast('🎬 Field video recorded! Ready in Compose page.', 'page-compose');

            const tmpVideo = document.createElement('video');
            tmpVideo.src = url; tmpVideo.muted = true; tmpVideo.playsInline = true;
            tmpVideo.addEventListener('loadeddata', () => { tmpVideo.currentTime = Math.min(0.3, (tmpVideo.duration || 1) / 2); });
            tmpVideo.addEventListener('seeked', () => {
                const canvas = document.createElement('canvas');
                canvas.width = tmpVideo.videoWidth || 320; canvas.height = tmpVideo.videoHeight || 240;
                canvas.getContext('2d').drawImage(tmpVideo, 0, 0, canvas.width, canvas.height);
                const thumb = canvas.toDataURL('image/jpeg', 0.85);
                vidItem.videoThumb = thumb;
                renderVideoMixer();
                openSaveModal({ video: url, videoThumb: thumb, category: 'sighting', defaultName: vidItem.name, place: 'Current location', onSaved: () => { vidStatus.textContent = 'Saved to Album.'; } });
            }, { once: true });
        };
        vidRecorder.start();
        isVidRecording = true;
        vidBtn.textContent = 'Stop';
        vidStatus.textContent = 'Recording…';
    } catch (err) { vidStatus.textContent = 'Camera/mic permission denied.'; }
}

/* =========================================================
   Learn page
   ========================================================= */
const LEARN_CATEGORIES = {
    insects: {
        label: "Insects", scene: "bee",
        entries: [
            { clip: "bee", title: "Honeybees", know: "Waggle dances plus a ~200–250 Hz wingbeat tone while foraging.", look: "A steady fundamental band with rich harmonics on the spectrogram.", canHear: "The low hum of wingbeats and buzzing.", cantHear: "Fine ultrasonic wing micro-vibrations.", study: "Bioacoustic recorders, spectrogram analysis, field correlation." },
            { clip: "cricket", title: "Crickets", know: "Males stridulate — rubbing wing edges together — to attract mates; rate rises with temperature.", look: "Sharp, evenly spaced pulses repeating several times a second.", canHear: "The familiar chirp.", cantHear: "Pulse-level micro-timing that encodes species identity.", study: "Pulse-rate counting and species call libraries." },
        ]
    },
    weather: {
        label: "Weather", scene: "rain",
        entries: [
            { clip: "rain", title: "Rain & wind", know: "Droplet impact size and canopy density shape the acoustic texture of rainfall.", look: "Dense broadband noise with irregular percussive spikes.", canHear: "Patter on leaves and steady wind hiss.", cantHear: "Individual droplet-impact transients at high time-resolution.", study: "Acoustic rain gauges that estimate rainfall rate from sound." },
        ]
    },
    plants: {
        label: "Plants", scene: "leaf",
        entries: [
            { clip: "rain", title: "Plant vibration", know: "Stems and leaves carry low-frequency vibrations from wind, insects, and internal water transport.", look: "Slow-moving low-frequency energy below typical hearing focus.", canHear: "Rustling when wind is strong enough.", cantHear: "Sub-audible structural vibration in the stem.", study: "Laser vibrometry and contact microphones on the stem." },
        ]
    },
    night: {
        label: "Night & Ultrasound", scene: "night",
        entries: [
            { clip: "bat", title: "Bat echolocation", know: "Bats emit ultrasonic pulses, well above 20 kHz, to navigate and hunt in the dark.", look: "Steep frequency sweeps far above the audible spectrogram band.", canHear: "Nothing directly — it's above the human range.", cantHear: "The entire call, without help.", study: "Heterodyne/time-expansion bat detectors, exactly what NATURA's sonifier emulates." },
        ]
    },
    mine: { label: "My Recordings", scene: "generic", entries: [] },
};
let currentCat = 'insects';
function buildLearnChips() {
    const row = document.getElementById('learnChips');
    row.innerHTML = '';
    Object.keys(LEARN_CATEGORIES).forEach(key => {
        if (key === 'mine' && LEARN_CATEGORIES.mine.entries.length === 0) return;
        const chip = document.createElement('div');
        chip.className = 'cat-chip' + (key === currentCat ? ' active' : '');
        chip.textContent = LEARN_CATEGORIES[key].label;
        chip.onclick = () => { currentCat = key; buildLearnChips(); buildLearnGrid(); };
        row.appendChild(chip);
    });
}
function buildLearnGrid() {
    const grid = document.getElementById('learnGrid');
    grid.innerHTML = '';
    document.getElementById('learnDetailWrap').innerHTML = '';
    LEARN_CATEGORIES[currentCat].entries.forEach((entry, idx) => {
        const fig = document.createElement('figure');
        fig.className = 'field-card';
        const art = entry.photo ? '<img src="'+entry.photo+'">' : sceneArt(CLIPS[entry.clip] ? CLIPS[entry.clip].scene : LEARN_CATEGORIES[currentCat].scene);
        fig.innerHTML = '<div class="field-art">'+art+'</div><figcaption>'+entry.title+'</figcaption><div class="sub">Tap to learn + listen</div>';
        fig.onclick = () => openLearnDetail(currentCat, idx);
        grid.appendChild(fig);
    });
}
function openLearnDetail(cat, idx) {
    const entry = LEARN_CATEGORIES[cat].entries[idx];
    const url = entry.clip ? CLIPS[entry.clip].url : entry.audioUrl;
    const wrap = document.getElementById('learnDetailWrap');
    wrap.innerHTML = '<div class="card" style="margin-top:10px;">' +
        '<div class="layer-title" style="margin-bottom:8px;">'+entry.title+'</div>' +
        '<div class="learn-fact"><b>What we know:</b> '+entry.know+'</div>' +
        '<div class="learn-fact"><b>What the sound looks like:</b> '+entry.look+'</div>' +
        '<div class="learn-fact"><b>What humans can hear:</b> '+entry.canHear+'</div>' +
        '<div class="learn-fact"><b>What humans cannot hear:</b> '+entry.cantHear+'</div>' +
        '<div class="learn-fact"><b>How scientists study it:</b> '+entry.study+'</div>' +
        (url ? '<button class="btn block" style="margin-top:10px;" onclick="new Audio(\''+url+'\').play()">▶ Listen to a real sample</button>' : '') +
        '</div>';
    wrap.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
buildLearnChips();
buildLearnGrid();

/* ---- Record-to-learn ---- */
let learnRecorder = null, learnChunks = [], isLearnRecording = false;
async function toggleLearnRecord() {
    const stage = document.getElementById('learnAudioStage');
    const btn = document.getElementById('learnRecBtn');
    if (isLearnRecording) { learnRecorder.stop(); isLearnRecording = false; btn.textContent = '● Record to learn'; return; }
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) { stage.innerHTML = '<span style="font-size:11px;">Microphone not available.</span>'; return; }
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        learnChunks = [];
        learnRecorder = new MediaRecorder(stream);
        learnRecorder.ondataavailable = e => learnChunks.push(e.data);
        learnRecorder.onstop = async () => {
            stream.getTracks().forEach(t => t.stop());
            const blob = new Blob(learnChunks, { type: 'audio/webm' });
            const url = URL.createObjectURL(blob);
            stage.classList.remove('empty');
            stage.innerHTML = '<audio controls src="'+url+'" style="width:100%;"></audio>';
            const result = await classifyAudioUrl(url);
            const meta = CATEGORY_META[result.category] || CATEGORY_META.unknown;
            openSaveModal({
                audioUrl: url, category: result.category, confidence: result.confidence, defaultName: meta.label, place: 'Current location',
                onSaved: (sample) => {
                    LEARN_CATEGORIES.mine.entries.unshift({ title: sample.name, know: "This is your own recording, matched to a " + meta.label.toLowerCase() + " signature at " + result.confidence + "% confidence.", look: "Waveform captured on your device; compare Original / Enhanced / Sonified from its Album entry.", canHear: "Everything you recorded, unprocessed.", cantHear: "Anything outside your microphone's natural range.", study: "Compare it against the categories on this page, or revisit it any time from your Album.", audioUrl: url });
                    currentCat = 'mine'; buildLearnChips(); buildLearnGrid();
                }
            });
        };
        learnRecorder.start(); isLearnRecording = true; btn.textContent = '■ Stop';
        stage.innerHTML = '<span style="font-size:11px; color:var(--moss-deep); font-weight:700;">Listening…</span>';
    } catch (err) { stage.innerHTML = '<span style="font-size:11px;">Microphone permission denied.</span>'; }
}

/* =========================================================
   Quest — specific missions, validated against what's submitted
   ========================================================= */
const QUEST_ROUNDS = [
    {
        theme: "Mission 1: The Pollinator's Trail",
        steps: [
            { id: 'q1', title: 'Record a foraging honeybee hum', detail: 'Listen for steady 200–260 Hz wingbeat hums. NATURA AI checks for acoustic harmonic flight oscillation.', type: 'audio', targetCategory: 'bee', targetLabel: 'a bee-like hum' },
            { id: 'q2', title: 'Photograph a flower blossom or pollinator', detail: 'Aim your camera at a blooming flower, petal, or pollinator. NATURA AI verifies floral chrominance.', type: 'photo', targetCategories: ['flower', 'bee', 'foliage'] },
            { id: 'q3', title: 'Record ambient wind, rain, or leaf rustle', detail: 'Capture 10+ seconds of background weather or foliage acoustics.', type: 'audio', targetCategory: 'rain', targetLabel: 'rain, wind, or leaf ambience' },
            { id: 'q4', title: 'Mix clips or field videos in Compose', detail: 'Go to Compose, mix your captured videos or field clips into a cinema reel, and save.', type: 'compose' },
            { id: 'q5', title: 'Save session as a Nature Moment', detail: 'Complete the missions above to bundle them into your Nature Album, tagged Quest.', type: 'save' }
        ]
    },
    {
        theme: "Mission 2: Night Chorus & Crepuscular Echoes",
        steps: [
            { id: 'q1', title: 'Record a night cricket chirp or stridulation', detail: 'Listen for rhythmic 4.5k–7.5k Hz chirps. NATURA AI checks for stridulation pulse energy.', type: 'audio', targetCategory: 'cricket', targetLabel: 'a cricket chirp' },
            { id: 'q2', title: 'Photograph garden foliage or canopy leaves', detail: 'Aim camera at green leaf surfaces or botanical vegetation. NATURA AI verifies green vegetation index.', type: 'photo', targetCategories: ['foliage', 'flower', 'bee'] },
            { id: 'q3', title: 'Record bat ultrasound or night acoustics', detail: 'Detect high-frequency bat echolocation sweeps or night atmospheric biophony.', type: 'audio', targetCategory: 'bat', targetLabel: 'bat echolocation or high-frequency buzz' },
            { id: 'q4', title: 'Mix field clips or video reels into Cinema', detail: 'Go to Compose, blend clips with ambient soundscapes and preview.', type: 'compose' },
            { id: 'q5', title: 'Save session as a Nature Moment', detail: 'Bundle your twilight discoveries into your Nature Album.', type: 'save' }
        ]
    },
    {
        theme: "Mission 3: Avian Canopy Symphony",
        steps: [
            { id: 'q1', title: 'Record bird vocalization or whistling chirp', detail: 'Capture modulated 1.5k–3.8k Hz syrinx whistles. NATURA checks for avian frequency contours.', type: 'audio', targetCategory: 'bird', targetLabel: 'bird song or whistle' },
            { id: 'q2', title: 'Photograph tree canopy, branch, or perching flora', detail: 'Point camera at botanical branches, tree bark, or flowers. NATURA AI checks macro flora structure.', type: 'photo', targetCategories: ['foliage', 'flower', 'bee'] },
            { id: 'q3', title: 'Record rainfall patter or leaf impact', detail: 'Record rain or water impact sounds. NATURA checks for stochastic broadband percussion.', type: 'audio', targetCategory: 'rain', targetLabel: 'rain or wind ambience' },
            { id: 'q4', title: 'Compose an Avian Cinema Montage', detail: 'Assemble a sequence of clips in Compose and save the montage.', type: 'compose' },
            { id: 'q5', title: 'Save session as a Nature Moment', detail: 'Save this rich canopy moment into your Nature Album.', type: 'save' }
        ]
    },
    {
        theme: "Mission 4: Micro-Fauna & Forest Floor",
        steps: [
            { id: 'q1', title: 'Record buzzing pollinator or insect stridulation', detail: 'Record close-up insect acoustics (bee hum or cricket chirp).', type: 'audio', targetCategories: ['bee', 'cricket'], targetLabel: 'bee hum or cricket chirp' },
            { id: 'q2', title: 'Photograph flower petals or botanical moss', detail: 'Capture vibrant plant flora, moss, or petals. NATURA AI inspects cellular coloration.', type: 'photo', targetCategories: ['flower', 'foliage'] },
            { id: 'q3', title: 'Record forest wind or canopy rustle', detail: 'Capture 10+ seconds of laminar friction through trees or grass.', type: 'audio', targetCategory: 'rain', targetLabel: 'wind, rain, or rustling leaves' },
            { id: 'q4', title: 'Sequence a Field Video Mix in Compose', detail: 'Pick your recorded videos, add an ambient soundtrack, and preview.', type: 'compose' },
            { id: 'q5', title: 'Save session as a Nature Moment', detail: 'Archive this micro-fauna session into your Nature Album.', type: 'save' }
        ]
    }
];

let questRound = 0;
let QUEST_STEPS = [];
function buildQuestSteps(roundIdx) {
    const round = QUEST_ROUNDS[roundIdx % QUEST_ROUNDS.length];
    const themeEl = document.getElementById('questTheme');
    if (themeEl) themeEl.textContent = round.theme + ' (Round ' + (roundIdx + 1) + ')';
    return round.steps.map(s => ({ ...s }));
}
QUEST_STEPS = buildQuestSteps(0);
let questDone = { q1: false, q2: false, q3: false, q4: false, q5: false };
let questSamples = {};

function renderQuestCards() {
    const wrap = document.getElementById('questCardsWrap');
    wrap.innerHTML = '';
    QUEST_STEPS.forEach((step, i) => {
        const done = questDone[step.id];
        const card = document.createElement('div');
        card.className = 'card quest-card' + (done ? ' complete' : '');
        let actionHtml = '';
        if (!done) {
            if (step.type === 'audio') {
                actionHtml = '<button class="btn sm outline" onclick="questRecordAudio(\''+step.id+'\')" id="qbtn-'+step.id+'">● Record</button>' +
                             '<button class="btn sm ghost" style="color:var(--sand-deep); font-size:11px; margin-left:auto;" onclick="skipQuestStep(\''+step.id+'\')" title="Skip if not found nearby">Skip step ⏭</button>';
            } else if (step.type === 'photo') {
                actionHtml = '<button class="btn sm outline" onclick="questCapturePhoto(\''+step.id+'\')" id="qbtn-'+step.id+'">📷 Capture</button>' +
                             '<button class="btn sm ghost" style="color:var(--sand-deep); font-size:11px; margin-left:auto;" onclick="skipQuestStep(\''+step.id+'\')" title="Skip if not found nearby">Skip step ⏭</button>';
            } else if (step.type === 'compose') {
                actionHtml = '<button class="btn sm outline" onclick="showPage(\'page-compose\', document.querySelector(\'.bottomnav button[data-page=page-compose]\'))">Go to Compose →</button>' +
                             '<button class="btn sm ghost" style="color:var(--sand-deep); font-size:11px; margin-left:auto;" onclick="skipQuestStep(\''+step.id+'\')" title="Skip if not found nearby">Skip step ⏭</button>';
            }
        }
        card.innerHTML =
            '<div class="qhead"><div class="qnum'+(done?' done':'')+'">'+(done?'✓':(i+1))+'</div>' +
            '<div><div class="qtitle">'+step.title+'</div><div class="qdetail">'+step.detail+'</div></div></div>' +
            (actionHtml ? '<div class="qactions">'+actionHtml+'</div>' : '') +
            '<div class="quest-mini-stage empty" id="qstage-'+step.id+'"></div>';
        wrap.appendChild(card);
        const stage = document.getElementById('qstage-'+step.id);
        if (done && questSamples[step.id]) {
            if (questSamples[step.id].skipped) {
                stage.innerHTML = '<div style="display:flex; justify-content:space-between; align-items:center; width:100%;">' +
                    '<span style="font-size:10.5px; color:var(--sand-deep); font-weight:700;">⏭ Skipped (Field pass granted)</span>' +
                    '<button class="btn xs ghost" style="color:var(--ink-soft); font-size:10px; padding:2px 6px;" onclick="undoQuestStep(\''+step.id+'\')">↺ Redo</button>' +
                    '</div>';
            } else {
                stage.innerHTML = '<span style="font-size:10.5px; color:var(--moss-deep); font-weight:700;">✓ Verified — saved to your Album</span>';
            }
        } else {
            stage.textContent = 'Nothing submitted yet';
        }
    });
    updateQuestSaveState();
}

function skipQuestStep(stepId) {
    if (questRecordingStepId === stepId && questAudioRecorder) {
        try { questAudioRecorder.stop(); } catch(e){}
        questRecordingStepId = null;
    }
    if (questCamStream) {
        try { questCamStream.getTracks().forEach(t => t.stop()); } catch(e){}
        questCamStream = null;
    }
    const step = QUEST_STEPS.find(s => s.id === stepId);
    questDone[stepId] = true;
    questSamples[stepId] = {
        id: newId('skip'),
        name: (step ? step.title : 'Field Quest Mission') + ' (Field pass)',
        date: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        place: 'Nature Quest Field Pass',
        skipped: true
    };
    renderQuestCards();
}

function undoQuestStep(stepId) {
    questDone[stepId] = false;
    delete questSamples[stepId];
    renderQuestCards();
}

function skipNextQuestStep() {
    const nextStep = QUEST_STEPS.find(s => !questDone[s.id] && s.type !== 'save');
    if (nextStep) {
        skipQuestStep(nextStep.id);
    } else {
        alert('All quest missions have already been completed or skipped!');
    }
}
renderQuestCards();

let questAudioRecorder = null, questAudioChunks = [], questRecordingStepId = null;
async function questRecordAudio(stepId) {
    const stage = document.getElementById('qstage-'+stepId);
    const btn = document.getElementById('qbtn-'+stepId);
    if (questRecordingStepId === stepId) { questAudioRecorder.stop(); questRecordingStepId = null; btn.textContent = '● Record'; return; }
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) { stage.textContent = 'Microphone not available.'; return; }
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        questAudioChunks = [];
        questAudioRecorder = new MediaRecorder(stream);
        questAudioRecorder.ondataavailable = e => questAudioChunks.push(e.data);
        questAudioRecorder.onstop = async () => {
            stream.getTracks().forEach(t => t.stop());
            const blob = new Blob(questAudioChunks, { type: 'audio/webm' });
            const url = URL.createObjectURL(blob);
            stage.textContent = 'Analyzing bioacoustic signature…';
            const step = QUEST_STEPS.find(s => s.id === stepId);
            const result = await classifyAudioUrl(url);
            
            const isMatch = step.targetCategory ? (result.category === step.targetCategory) : (step.targetCategories && step.targetCategories.includes(result.category));
            if (isMatch) {
                const meta = CATEGORY_META[result.category] || CATEGORY_META.unknown;
                openSaveModal({
                    audioUrl: url, category: result.category, confidence: result.confidence, defaultName: step.title, place: 'Quest field session', badge: 'Quest',
                    onSaved: (sample) => { questDone[stepId] = true; questSamples[stepId] = sample; renderQuestCards(); }
                });
            } else {
                const gotMeta = CATEGORY_META[result.category] || CATEGORY_META.unknown;
                stage.innerHTML = '<span class="quest-fail">That matched "'+gotMeta.label+'", not '+step.targetLabel+'. Try again.</span>' +
                    '<div style="margin-top:6px;"><button class="btn xs ghost" style="color:var(--sand-deep); text-decoration:underline;" onclick="skipQuestStep(\''+stepId+'\')">Can\'t find this sound? Skip step ⏭</button></div>';
            }
        };
        questAudioRecorder.start(); questRecordingStepId = stepId; btn.textContent = '■ Stop';
        stage.classList.add('empty'); stage.textContent = 'Listening…';
    } catch (err) { stage.textContent = 'Microphone permission denied.'; }
}

let questCamStream = null;
async function questCapturePhoto(stepId) {
    const stage = document.getElementById('qstage-'+stepId);
    const btn = document.getElementById('qbtn-'+stepId);
    if (btn.textContent === '📸 Snap') {
        const video = stage.querySelector('video');
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth || 320; canvas.height = video.videoHeight || 240;
        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
        if (questCamStream) questCamStream.getTracks().forEach(t => t.stop());
        btn.textContent = '📷 Capture';
        
        stage.innerHTML = '<img src="'+dataUrl+'" style="height:70px;object-fit:cover;border-radius:8px;">' +
            '<div style="font-size:11px; color:var(--moss-deep); font-weight:700; margin-top:4px;">🔍 AI Vision analyzing botanical subject…</div>';
        
        const visionRes = await classifyImageData(canvas);
        const step = QUEST_STEPS.find(s => s.id === stepId);
        const validCategories = step.targetCategories || ['flower', 'bee', 'foliage'];
        
        if (visionRes.category === 'non_botanical' || !validCategories.includes(visionRes.category)) {
            stage.innerHTML = '<img src="'+dataUrl+'" style="height:70px;object-fit:cover;border-radius:8px;filter:grayscale(0.7);">' +
                '<div class="quest-fail" style="margin-top:6px;">✗ '+visionRes.label+': No botanical subject or bloom detected.</div>' +
                '<div style="font-size:10px; color:var(--ink-soft); margin-bottom:6px;">'+(visionRes.reason || 'Point camera at a flower, leaf, or pollinator.')+'</div>' +
                '<div style="display:flex; gap:8px; align-items:center;">' +
                '<button class="btn xs outline" onclick="questCapturePhoto(\''+stepId+'\')">📷 Retake photo</button>' +
                '<button class="btn xs ghost" style="color:var(--sand-deep); text-decoration:underline;" onclick="skipQuestStep(\''+stepId+'\')">Can\'t find a plant? Skip step ⏭</button>' +
                '</div>';
            return;
        }
        
        // AI Vision verified!
        stage.innerHTML = '<img src="'+dataUrl+'" style="height:70px;object-fit:cover;border-radius:8px;">' +
            '<div style="font-size:11px; color:var(--moss-deep); font-weight:700; margin-top:4px;">✓ AI Verified: '+visionRes.label+' ('+visionRes.confidence+'% match)</div>';
        
        openSaveModal({
            photo: dataUrl, category: visionRes.category === 'flower' ? 'flower' : (visionRes.category === 'bee' ? 'bee' : 'foliage'),
            defaultName: visionRes.label, place: 'Quest field session', badge: 'Quest',
            onSaved: (sample) => { questDone[stepId] = true; questSamples[stepId] = sample; renderQuestCards(); }
        });
        return;
    }
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) { stage.textContent = 'Camera not available.'; return; }
    try {
        questCamStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
        const video = document.createElement('video'); video.autoplay = true; video.playsInline = true; video.srcObject = questCamStream;
        stage.classList.remove('empty'); stage.innerHTML = ''; stage.appendChild(video);
        btn.textContent = '📸 Snap';
    } catch (err) { stage.textContent = 'Camera permission denied.'; }
}

function updateQuestSaveState() {
    const ready = questDone.q1 && questDone.q2 && questDone.q3 && questDone.q4 && !questDone.q5;
    const saveBtn = document.getElementById('questSaveBtn');
    saveBtn.disabled = !ready;
    saveBtn.textContent = questDone.q5 ? 'Nature Moment saved ✓' : 'Save Nature Moment to Album';
}
function saveQuestMoment() {
    if (document.getElementById('questSaveBtn').disabled) return;
    questDone.q5 = true;
    document.getElementById('questSaveBtn').disabled = true;
    document.getElementById('questSaveBtn').textContent = 'Nature Moment saved ✓';
    renderQuestCards();
    
    // Display celebration card with prompt to generate a new quest
    const celeb = document.getElementById('questCelebration');
    if (celeb) celeb.style.display = 'block';
    celeb.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function startNewQuestRound() {
    questRound++;
    QUEST_STEPS = buildQuestSteps(questRound);
    questDone = { q1: false, q2: false, q3: false, q4: false, q5: false };
    questSamples = {};
    clearInterval(questInterval);
    questRunning = false;
    questSeconds = 600;
    document.getElementById('questTime').textContent = '10:00';
    document.getElementById('questProgress').style.width = '0%';
    const btn = document.getElementById('questBtn');
    btn.disabled = false; btn.textContent = 'Begin quest';
    document.getElementById('questState').textContent = 'New quest ready';
    const saveBtn = document.getElementById('questSaveBtn');
    saveBtn.disabled = true; saveBtn.textContent = 'Save Nature Moment to Album';
    const celeb = document.getElementById('questCelebration');
    if (celeb) celeb.style.display = 'none';
    renderQuestCards();
}

let questInterval = null, questSeconds = 600, questRunning = false;
function toggleQuest() {
    const btn = document.getElementById('questBtn');
    const state = document.getElementById('questState');
    if (questRunning) { clearInterval(questInterval); questRunning = false; btn.textContent = 'Resume quest'; state.textContent = 'Paused'; return; }
    questRunning = true; btn.textContent = 'Pause quest'; state.textContent = 'In progress';
    questInterval = setInterval(() => {
        questSeconds--;
        if (questSeconds <= 0) { clearInterval(questInterval); questSeconds = 0; state.textContent = 'Time up'; btn.textContent = 'Time up'; btn.disabled = true; }
        const m = Math.floor(questSeconds / 60).toString().padStart(2, '0');
        const s = (questSeconds % 60).toString().padStart(2, '0');
        document.getElementById('questTime').textContent = m + ':' + s;
        document.getElementById('questProgress').style.width = ((600 - questSeconds) / 600 * 100) + '%';
    }, 1000);
}

/* =========================================================
   Composer mixer
   ========================================================= */
const mixState = {};
const mixPlayers = {};
function buildMixer() {
    const card = document.getElementById('mixerCard');
    card.innerHTML = '';
    Object.keys(CLIPS).forEach(key => {
        const c = CLIPS[key];
        mixState[key] = { on: false, vol: 70 };
        const row = document.createElement('div');
        row.className = 'mix-row';
        row.innerHTML =
            '<div class="mix-art">'+sceneArt(c.scene)+'</div>' +
            '<div class="mix-info"><b>'+c.label+'</b><span>'+c.place+'</span><div class="mix-track-bar"><div id="bar-'+key+'"></div></div></div>' +
            '<input class="mix-vol" type="range" min="0" max="100" value="70" oninput="setVol(\''+key+'\', this.value)">' +
            '<button class="mix-toggle" id="tog-'+key+'" onclick="toggleClip(\''+key+'\')">+</button>';
        card.appendChild(row);
    });
}
buildMixer();

function toggleClip(key) {
    mixState[key].on = !mixState[key].on;
    const btn = document.getElementById('tog-'+key);
    btn.classList.toggle('on', mixState[key].on);
    btn.textContent = mixState[key].on ? '✓' : '+';
    if (mixPlaying) syncMixPlayers();
}
function setVol(key, val) { mixState[key].vol = val; if (mixPlayers[key]) mixPlayers[key].volume = val / 100; }

let mixPlaying = false;
function syncMixPlayers() {
    Object.keys(CLIPS).forEach(key => {
        if (mixState[key].on) {
            if (!mixPlayers[key]) { const a = new Audio(CLIPS[key].url); a.loop = true; a.volume = mixState[key].vol / 100; mixPlayers[key] = a; }
            mixPlayers[key].play().catch(()=>{});
            document.getElementById('bar-'+key).style.width = '100%';
        } else if (mixPlayers[key]) {
            mixPlayers[key].pause();
            document.getElementById('bar-'+key).style.width = '0%';
        }
    });
}
function toggleMixPlay() {
    const btn = document.getElementById('mixPlayBtn');
    const anyOn = Object.values(mixState).some(s => s.on);
    if (!mixPlaying) {
        if (!anyOn) { alert('Turn on at least one clip with the + button first.'); return; }
        mixPlaying = true; btn.textContent = '⏸ Pause mix'; syncMixPlayers();
    } else {
        mixPlaying = false; btn.textContent = '▶ Play mix';
        Object.values(mixPlayers).forEach(p => p.pause());
        Object.keys(CLIPS).forEach(key => { const b = document.getElementById('bar-'+key); if (b) b.style.width = '0%'; });
    }
}

/* ---- Saved compositions: stored + replayable through the mixer itself ---- */
let savedCompositions = [];
function renderSavedComps() {
    const wrap = document.getElementById('savedComps');
    wrap.innerHTML = '';
    if (!savedCompositions.length) { wrap.innerHTML = '<p class="desc" style="margin:0;">No compositions saved yet — build a mix above and hit Save.</p>'; return; }
    savedCompositions.forEach(entry => {
        const row = document.createElement('div');
        row.className = 'saved-comp';
        const used = entry.keys.map(k => CLIPS[k].label).join(' + ');
        row.innerHTML = '<span style="font-size:16px;">🎼</span><div><b>'+entry.name+'</b><br><span style="font-size:10.5px;color:var(--ink-soft)">'+used+'</span></div>' +
            '<button class="btn xs outline" style="margin-left:auto;" onclick="viewSavedComposition(\''+entry.id+'\')">▶ View</button>' +
            '<button class="sc-del" onclick="deleteSavedComposition(\''+entry.id+'\')"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M6 6l12 12M18 6 6 18"/></svg></button>';
        wrap.appendChild(row);
    });
}
function viewSavedComposition(id) {
    const entry = savedCompositions.find(e => e.id === id);
    if (!entry) return;
    Object.keys(CLIPS).forEach(key => {
        mixState[key].on = entry.keys.includes(key);
        const btn = document.getElementById('tog-'+key);
        btn.classList.toggle('on', mixState[key].on);
        btn.textContent = mixState[key].on ? '✓' : '+';
    });
    if (!mixPlaying) { mixPlaying = true; document.getElementById('mixPlayBtn').textContent = '⏸ Pause mix'; }
    syncMixPlayers();
    document.getElementById('mixerCard').scrollIntoView({ behavior: 'smooth', block: 'start' });
}
function deleteSavedComposition(id) {
    savedCompositions = savedCompositions.filter(e => e.id !== id);
    renderSavedComps();
}
function saveComposition() {
    const anyOn = Object.values(mixState).some(s => s.on);
    if (!anyOn) { alert('Turn on at least one clip before saving.'); return; }
    const name = document.getElementById('compName').value || 'Untitled composition';
    const keys = Object.keys(CLIPS).filter(k => mixState[k].on);
    savedCompositions.unshift({ id: newId('mix'), name, keys });
    renderSavedComps();
    document.getElementById('journeyComps').textContent = (parseInt(document.getElementById('journeyComps').textContent, 10) + 1);
    questDone.q4 = true; renderQuestCards();
}
renderSavedComps();

/* =========================================================
   Field Video Mixer & Nature Cinema
   ========================================================= */
let recordedVideos = [];
let videoMixSelection = [];
let cinemaSelection = [];

function createFieldDemoVideo(title, hue, iconText) {
    try {
        const canvas = document.createElement('canvas');
        canvas.width = 320; canvas.height = 200;
        const ctx = canvas.getContext('2d');
        const stream = canvas.captureStream ? canvas.captureStream(25) : null;
        if (!stream || typeof MediaRecorder === 'undefined') {
            ctx.fillStyle = 'hsl(' + hue + ', 35%, 22%)';
            ctx.fillRect(0, 0, 320, 200);
            ctx.fillStyle = '#fff';
            ctx.font = '28px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(iconText, 160, 90);
            ctx.font = 'bold 13px sans-serif';
            ctx.fillText(title, 160, 125);
            const thumb = canvas.toDataURL('image/jpeg', 0.85);
            recordedVideos.push({
                id: newId('vid'),
                name: title,
                video: null,
                videoThumb: thumb,
                photo: thumb,
                date: 'Demo clip',
                category: 'sighting'
            });
            renderVideoMixer();
            renderCinemaPickList();
            return;
        }
        const rec = new MediaRecorder(stream, { mimeType: 'video/webm' });
        const chunks = [];
        rec.ondataavailable = e => chunks.push(e.data);
        let frame = 0;
        const draw = () => {
            if (frame > 75) { rec.stop(); return; }
            ctx.fillStyle = 'hsl(' + hue + ', 38%, 20%)';
            ctx.fillRect(0, 0, 320, 200);
            ctx.fillStyle = 'hsla(' + (hue + 30) + ', 65%, 45%, 0.35)';
            ctx.beginPath();
            ctx.arc(160 + Math.sin(frame / 8) * 35, 100 + Math.cos(frame / 8) * 20, 50 + Math.sin(frame / 4) * 12, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#fff';
            ctx.font = '30px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(iconText, 160, 85);
            ctx.font = 'bold 13px Inter, sans-serif';
            ctx.fillText(title, 160, 120);
            ctx.font = '10px Inter, sans-serif';
            ctx.fillStyle = 'rgba(255,255,255,0.7)';
            ctx.fillText('NATURA Field Cam · 0:0' + Math.floor(frame / 25), 160, 145);
            frame++;
            requestAnimationFrame(draw);
        };
        rec.onstop = () => {
            const blob = new Blob(chunks, { type: 'video/webm' });
            const url = URL.createObjectURL(blob);
            const thumb = canvas.toDataURL('image/jpeg', 0.85);
            recordedVideos.push({
                id: newId('vid'),
                name: title,
                video: url,
                videoThumb: thumb,
                date: 'Demo clip',
                category: 'sighting'
            });
            renderVideoMixer();
            renderCinemaPickList();
        };
        rec.start();
        draw();
    } catch (e) {
        console.warn('Demo video fallback', e);
    }
}

function renderVideoMixer() {
    const grid = document.getElementById('videoMixGrid');
    if (!grid) return;
    grid.innerHTML = '';

    if (!recordedVideos.length) {
        grid.innerHTML = '<div style="grid-column:1/-1; padding:16px 10px; font-size:11.5px; color:var(--ink-soft); text-align:center; background:var(--panel); border:1px dashed var(--line); border-radius:10px;">' +
            'No videos recorded yet.<br><span style="font-size:10.5px; color:var(--sand-deep);">Record a video on the <b>Listen</b> page, or create a demo field clip below.</span>' +
            '<div style="margin-top:8px;"><button class="btn xs outline" onclick="seedDemoFieldVideo()">+ Generate Demo Video Clip</button></div>' +
            '</div>';
        renderVideoMixChips();
        return;
    }

    recordedVideos.forEach((vid, idx) => {
        const item = document.createElement('div');
        const isSelected = videoMixSelection.some(s => s.id === vid.id);
        item.className = 'video-mix-item' + (isSelected ? ' selected' : '');
        item.innerHTML = '<div class="vm-thumb">' +
            (vid.videoThumb ? '<img src="' + vid.videoThumb + '">' : '<video src="' + vid.video + '" muted></video>') +
            '<span class="vm-badge">' + (isSelected ? '✓ In Mix' : 'Clip ' + (idx + 1)) + '</span>' +
            '</div>' +
            '<div class="vm-title">' + vid.name + '</div>';
        item.onclick = () => toggleVideoMixItem(vid);
        grid.appendChild(item);
    });
    renderVideoMixChips();
}

function toggleVideoMixItem(vid) {
    const idx = videoMixSelection.findIndex(s => s.id === vid.id);
    if (idx >= 0) {
        videoMixSelection.splice(idx, 1);
    } else {
        videoMixSelection.push({ ...vid });
    }
    renderVideoMixer();
}

function renderVideoMixChips() {
    const wrap = document.getElementById('videoMixChips');
    if (!wrap) return;
    wrap.innerHTML = '';
    if (!videoMixSelection.length) {
        wrap.innerHTML = '<span style="font-size:10.5px; color:var(--ink-soft); font-style:italic;">Tap clips above to sequence into your mix (ordered 1, 2, 3...)</span>';
        return;
    }
    videoMixSelection.forEach((s, i) => {
        const chip = document.createElement('div');
        chip.className = 'video-mix-chip';
        chip.innerHTML = (i + 1) + '. ' + s.name + ' <button onclick="removeVideoMixItem(\'' + s.id + '\')">×</button>';
        wrap.appendChild(chip);
    });
}

function removeVideoMixItem(id) {
    videoMixSelection = videoMixSelection.filter(s => s.id !== id);
    renderVideoMixer();
}

function seedDemoFieldVideo() {
    const count = recordedVideos.length + 1;
    const hue = count % 2 === 0 ? 140 : 200;
    const title = count % 2 === 0 ? 'Meadow Flutter ' + count : 'River Current ' + count;
    const icon = count % 2 === 0 ? '🌿' : '🌊';
    createFieldDemoVideo(title, hue, icon);
}

function playVideoMix() {
    if (!videoMixSelection.length) {
        alert('Please select at least one recorded video from the grid above to mix.');
        return;
    }
    stopCinema();
    const trackSelect = document.getElementById('videoMixTrackSelect');
    const ambientTrackKey = trackSelect ? trackSelect.value : 'none';

    cinemaSelection = videoMixSelection.map(item => ({ ...item }));
    renderCinemaChips();
    renderCinemaPickList();

    const stage = document.getElementById('cinemaStage');
    if (stage) stage.scrollIntoView({ behavior: 'smooth', block: 'center' });

    cinemaPlaying = true;
    if (ambientTrackKey !== 'none' && CLIPS[ambientTrackKey]) {
        cinemaAudio = new Audio(CLIPS[ambientTrackKey].url);
        cinemaAudio.loop = true;
        cinemaAudio.play().catch(()=>{});
    }

    playCinemaFrame(0);
}

function saveVideoMix() {
    if (!videoMixSelection.length) {
        alert('Please select at least one recorded video to save this mix.');
        return;
    }
    const nameInput = document.getElementById('videoMixName');
    const name = (nameInput && nameInput.value.trim()) ? nameInput.value.trim() : ('Field Video Mix ' + (savedCinemas.length + 1));
    const trackSelect = document.getElementById('videoMixTrackSelect');
    const ambientTrack = trackSelect ? trackSelect.value : 'none';

    const newMix = {
        id: newId('cinema'),
        name: name,
        type: 'video_mix',
        ambientTrack: ambientTrack,
        items: videoMixSelection.map(item => ({ ...item })),
        date: new Date().toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
    };
    savedCinemas.unshift(newMix);
    renderSavedCinemas();

    const countEl = document.getElementById('journeyCinemas');
    if (countEl) countEl.textContent = parseInt(countEl.textContent, 10) + 1;

    questDone.q4 = true;
    renderQuestCards();

    alert('🎬 Video Mix "' + name + '" saved to your Cinema collection!');
    document.getElementById('savedCinemas').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function flattenAllSamples() {
    const items = [];
    albumGroups.forEach(group => {
        group.samples.forEach(sample => items.push({ groupCategory: group.category, sample }));
    });
    recordedVideos.forEach(vid => {
        if (!items.some(it => it.sample.video === vid.video)) {
            items.push({ groupCategory: 'sighting', sample: vid });
        }
    });
    return items;
}

function renderCinemaPickList() {
    const list = document.getElementById('cinemaPickList');
    if (!list) return;
    list.innerHTML = '';
    const all = flattenAllSamples();
    all.forEach(({ groupCategory, sample }) => {
        const row = document.createElement('div');
        row.className = 'cinema-pick-item';
        const checked = cinemaSelection.some(s => s.id === sample.id) ? 'checked' : '';
        row.innerHTML = '<input type="checkbox" ' + checked + '><div class="cp-art">' + sampleThumb(sample, groupCategory) + '</div><div>' + sample.name + '</div>';
        row.querySelector('input').onchange = (e) => { toggleCinemaItem(sample, groupCategory, e.target.checked); };
        row.onclick = (e) => { if (e.target.tagName !== 'INPUT') row.querySelector('input').click(); };
        list.appendChild(row);
    });
    if (!all.length) list.innerHTML = '<div style="padding:14px; font-size:11px; color:var(--ink-soft); text-align:center;">No recordings in your Album yet.</div>';
}

function toggleCinemaItem(sample, groupCategory, on) {
    if (on) {
        if (!cinemaSelection.some(s => s.id === sample.id)) cinemaSelection.push({ ...sample, groupCategory });
    } else {
        cinemaSelection = cinemaSelection.filter(s => s.id !== sample.id);
    }
    renderCinemaChips();
}

function renderCinemaChips() {
    const wrap = document.getElementById('cinemaChips');
    if (!wrap) return;
    wrap.innerHTML = '';
    cinemaSelection.forEach((s, i) => {
        const chip = document.createElement('div');
        chip.className = 'cinema-chip';
        chip.innerHTML = (i + 1) + '. ' + s.name + ' <button onclick="removeCinemaItem(\'' + s.id + '\')">×</button>';
        wrap.appendChild(chip);
    });
}

function removeCinemaItem(id) {
    cinemaSelection = cinemaSelection.filter(s => s.id !== id);
    renderCinemaChips();
    renderCinemaPickList();
}

let cinemaPlaying = false, cinemaTimer = null, cinemaAudio = null;
function stopCinema() {
    cinemaPlaying = false;
    if (cinemaTimer) { clearTimeout(cinemaTimer); cinemaTimer = null; }
    if (cinemaAudio) { cinemaAudio.pause(); cinemaAudio = null; }
    const stage = document.getElementById('cinemaStage');
    if (stage) {
        const v = stage.querySelector('video'); if (v) v.pause();
    }
}

function previewCinema() {
    if (!cinemaSelection.length) { alert('Select at least one clip from the list above.'); return; }
    stopCinema();
    cinemaPlaying = true;
    playCinemaFrame(0);
}

function playCinemaFrame(index) {
    if (!cinemaPlaying) return;
    const stage = document.getElementById('cinemaStage');
    if (!stage) return;
    if (index >= cinemaSelection.length) {
        stage.innerHTML = '<div style="text-align:center; padding:18px 10px;"><span style="font-size:24px; display:block; margin-bottom:4px;">✨</span><b>Reel finished</b><p style="font-size:11px; color:var(--ink-soft); margin-top:4px;">Save it below, or Preview again.</p></div>';
        cinemaPlaying = false;
        if (cinemaAudio) { cinemaAudio.pause(); cinemaAudio = null; }
        return;
    }
    const item = cinemaSelection[index];
    const caption = '<div class="cs-caption">' + (index + 1) + ' / ' + cinemaSelection.length + ' · ' + item.name + '</div>';
    if (item.video) {
        stage.innerHTML = '<video src="' + item.video + '" autoplay playsinline style="width:100%; height:100%; object-fit:cover;"></video>' + caption;
        const v = stage.querySelector('video');
        if (cinemaAudio) {
            v.muted = true;
        } else {
            v.muted = false;
        }
        v.play().catch(() => {
            v.muted = true;
            v.play().catch(()=>{});
        });
        v.onended = () => playCinemaFrame(index + 1);
        cinemaTimer = setTimeout(() => {
            if (cinemaPlaying && stage.querySelector('video') === v) {
                playCinemaFrame(index + 1);
            }
        }, 10000);
    } else {
        stage.innerHTML = (item.photo ? '<img src="' + item.photo + '">' : sceneArt((CATEGORY_META[item.groupCategory] || CATEGORY_META.unknown).scene)) + caption;
        if (item.audioUrl && !cinemaAudio) {
            const clipAudio = new Audio(item.audioUrl);
            clipAudio.play().catch(()=>{});
            clipAudio.onended = () => playCinemaFrame(index + 1);
            cinemaTimer = setTimeout(() => { if (cinemaPlaying) playCinemaFrame(index + 1); }, 6000);
        } else {
            cinemaTimer = setTimeout(() => playCinemaFrame(index + 1), 3500);
        }
    }
}

let savedCinemas = [];
function renderSavedCinemas() {
    const wrap = document.getElementById('savedCinemas');
    if (!wrap) return;
    if (!savedCinemas.length) { wrap.style.display = 'none'; wrap.innerHTML = ''; return; }
    wrap.style.display = '';
    wrap.innerHTML = '';
    savedCinemas.forEach(entry => {
        const row = document.createElement('div');
        row.className = 'saved-comp';
        const icon = entry.type === 'video_mix' ? '🎥' : '🎬';
        const label = entry.type === 'video_mix' ? 'Video Mix · ' : '';
        row.innerHTML = '<span style="font-size:16px;">' + icon + '</span><div><b>' + entry.name + '</b><br><span style="font-size:10.5px;color:var(--ink-soft)">' + label + entry.items.length + ' clips</span></div>' +
            '<button class="btn xs outline" style="margin-left:auto;" onclick="viewSavedCinema(\'' + entry.id + '\')">▶ View</button>' +
            '<button class="sc-del" onclick="deleteSavedCinema(\'' + entry.id + '\')"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M6 6l12 12M18 6 6 18"/></svg></button>';
        wrap.appendChild(row);
    });
}

function viewSavedCinema(id) {
    const entry = savedCinemas.find(e => e.id === id);
    if (!entry) return;
    stopCinema();
    cinemaSelection = entry.items.map(item => ({ ...item }));
    renderCinemaChips();
    renderCinemaPickList();

    if (entry.ambientTrack && entry.ambientTrack !== 'none' && CLIPS[entry.ambientTrack]) {
        cinemaAudio = new Audio(CLIPS[entry.ambientTrack].url);
        cinemaAudio.loop = true;
        cinemaAudio.play().catch(()=>{});
    }

    const stage = document.getElementById('cinemaStage');
    if (stage) stage.scrollIntoView({ behavior: 'smooth', block: 'center' });
    cinemaPlaying = true;
    playCinemaFrame(0);
}

function deleteSavedCinema(id) {
    savedCinemas = savedCinemas.filter(e => e.id !== id);
    renderSavedCinemas();
}

function saveCinema() {
    if (!cinemaSelection.length) { alert('Select at least one clip first.'); return; }
    const name = document.getElementById('cinemaName').value || 'Untitled cinema';
    savedCinemas.unshift({ id: newId('cinema'), name, type: 'cinema', items: cinemaSelection.map(item => ({ ...item })) });
    renderSavedCinemas();
    document.getElementById('journeyCinemas').textContent = (parseInt(document.getElementById('journeyCinemas').textContent, 10) + 1);
    questDone.q4 = true; renderQuestCards();
}

renderVideoMixer();
renderCinemaPickList();
renderSavedCinemas();

setTimeout(() => {
    createFieldDemoVideo("Hibiscus Bloom Flutter", 145, "🌺");
    createFieldDemoVideo("Stream Current at Dusk", 200, "🌊");
}, 250);
</script>
</body>
</html>
"""

class NaturaDashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif parsed.path.startswith("/audio/"):
            key = parsed.path.split("/audio/", 1)[1]
            filename = SAMPLE_FILES.get(key)
            if not filename:
                self.send_error(404, "Unknown clip")
                return
            file_path = SAMPLES_DIR / filename
            if not file_path.exists():
                self.send_error(404, "Sample file missing")
                return
            data = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-type", "audio/wav")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif parsed.path == "/api/status":
            bridge = VivoOfficeKitBridge()
            data = asdict(bridge.get_bridge_status())
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
        elif parsed.path == "/api/lessons":
            book = NatureLanguageBook()
            lessons = [asdict(l) for l in book.get_all_lessons()]
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(lessons).encode("utf-8"))
        elif parsed.path in ("/manifest.json", "/manifest.webmanifest"):
            manifest = {
                "name": "NATURA — AI Multimodal Nature Explorer",
                "short_name": "NATURA",
                "description": "On-device multimodal nature explorer. Bioacoustics, camera vision, and soundscape cinema.",
                "start_url": "/",
                "display": "standalone",
                "background_color": "#f6f2ea",
                "theme_color": "#2a4a2c",
                "orientation": "portrait",
                "icons": [
                    {
                        "src": "/icon.svg",
                        "sizes": "any",
                        "type": "image/svg+xml",
                        "purpose": "any maskable"
                    },
                    {
                        "src": "/icon-192.png",
                        "sizes": "192x192",
                        "type": "image/svg+xml",
                        "purpose": "any maskable"
                    },
                    {
                        "src": "/icon-512.png",
                        "sizes": "512x512",
                        "type": "image/svg+xml",
                        "purpose": "any maskable"
                    }
                ]
            }
            data = json.dumps(manifest, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-type", "application/manifest+json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif parsed.path == "/sw.js":
            sw_code = (
                "const CACHE_NAME = 'natura-pwa-v1';\n"
                "const ASSETS = ['/', '/manifest.json'];\n"
                "self.addEventListener('install', e => {\n"
                "  e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(ASSETS)));\n"
                "  self.skipWaiting();\n"
                "});\n"
                "self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));\n"
                "self.addEventListener('fetch', e => {\n"
                "  if (e.request.method !== 'GET') return;\n"
                "  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));\n"
                "});\n"
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-type", "application/javascript; charset=utf-8")
            self.send_header("Content-Length", str(len(sw_code)))
            self.end_headers()
            self.wfile.write(sw_code)
        elif parsed.path in ("/icon.svg", "/icon-192.png", "/icon-512.png", "/apple-touch-icon.png"):
            icon_svg = (
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">'
                '<rect width="512" height="512" rx="120" fill="#2a4a2c"/>'
                '<g transform="translate(106, 106) scale(3)" stroke="none" fill="#f6f2ea">'
                '<rect x="2" y="48" width="3.4" height="18" rx="1.7" fill="#f6f2ea" opacity="0.85"/>'
                '<rect x="9" y="42" width="3.4" height="30" rx="1.7" fill="#f6f2ea" opacity="0.85"/>'
                '<rect x="16" y="35" width="3.4" height="44" rx="1.7" fill="#f6f2ea" opacity="0.85"/>'
                '<rect x="80.6" y="35" width="3.4" height="44" rx="1.7" fill="#f6f2ea" opacity="0.85"/>'
                '<rect x="87.6" y="42" width="3.4" height="30" rx="1.7" fill="#f6f2ea" opacity="0.85"/>'
                '<rect x="94.6" y="48" width="3.4" height="18" rx="1.7" fill="#f6f2ea" opacity="0.85"/>'
                '<circle cx="50" cy="58" r="29" fill="none" stroke="#f6f2ea" stroke-width="2.2"/>'
                '<path d="M50 43c7 3 10 10 6 18-7-2-12-9-12-15 0-1.5 2.5-3.5 6-3Z" fill="#f6f2ea"/>'
                '<path d="M50 6c15 6 21 19 14 33-4-2-8-5-10-9 6-2 8-8 5-15-5 4-9 11-7 19-7-6-9-17-5-27 1-0.5 2-1 3-1Z" fill="#f6f2ea"/>'
                '</g>'
                '</svg>'
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-type", "image/svg+xml")
            self.send_header("Content-Length", str(len(icon_svg)))
            self.end_headers()
            self.wfile.write(icon_svg)
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len) if content_len > 0 else b"{}"

        if parsed.path == "/api/classify_audio":
            try:
                payload = json.loads(post_body.decode("utf-8"))
                classifier = BioacousticClassifier()
                pcm_data = payload.get("pcm")
                sr = int(payload.get("sample_rate", 48000))
                classifier.sample_rate = sr

                if pcm_data and len(pcm_data) > 32:
                    audio_arr = np.array(pcm_data, dtype=np.float32)
                    res = classifier.classify(audio_arr)
                    label = res.primary_label
                    conf = res.confidence
                    sci = res.scientific_name
                    pattern = res.pattern_type
                    feats = classifier.extract_features(audio_arr)
                else:
                    dom_freq = float(payload.get("dom_freq", 0))
                    centroid = float(payload.get("centroid", 0))
                    flatness = float(payload.get("flatness", 0))
                    if 150 <= dom_freq <= 380:
                        label = "honeybee_wingbeat"
                        conf = 0.93
                        sci = "Apis mellifera"
                        pattern = "Harmonic wingbeat oscillation"
                    elif 4000 <= dom_freq <= 8000:
                        label = "tree_cricket_stridulation"
                        conf = 0.91
                        sci = "Oecanthus fultoni"
                        pattern = "Rhythmic resonant stridulation"
                    elif centroid > 12000 or dom_freq >= 16000:
                        label = "ultrasonic_echolocation"
                        conf = 0.89
                        sci = "Pipistrellus pipistrellus"
                        pattern = "Ultrasonic sweep"
                    elif flatness > 0.75:
                        label = "rain_percussion"
                        conf = 0.85
                        sci = "Hydrometeorological"
                        pattern = "Broadband droplet impact"
                    elif 1200 <= dom_freq <= 3800:
                        label = "songbird_vocalization"
                        conf = 0.87
                        sci = "Passeriformes spp."
                        pattern = "Avian whistle"
                    else:
                        label = "unknown_acoustic_event"
                        conf = 0.50
                        sci = "Incertae sedis"
                        pattern = "Ambient nature"
                    feats = {"dom_freq": dom_freq, "centroid": centroid, "flatness": flatness}

                if "bee" in label:
                    category = "bee"
                    ui_label = "Bee-like hum"
                elif "cricket" in label:
                    category = "cricket"
                    ui_label = "Cricket / insect chirp"
                elif "echolocation" in label or "ultrasonic" in label:
                    category = "bat"
                    ui_label = "High-frequency bat echolocation"
                elif "rain" in label or "droplet" in label:
                    category = "rain"
                    ui_label = "Rain / wind ambience"
                elif "bird" in label or "songbird" in label:
                    category = "bird"
                    ui_label = "Bird song / whistle"
                else:
                    category = "unknown"
                    ui_label = "Unclassified sound"

                out = {
                    "status": "ok",
                    "category": category,
                    "label": ui_label,
                    "scientific_name": sci,
                    "confidence": int(conf * 100),
                    "pattern": pattern,
                    "features": feats
                }
            except Exception as e:
                out = {"status": "error", "message": str(e), "category": "unknown", "confidence": 50}

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(out).encode("utf-8"))

        elif parsed.path == "/api/classify_image":
            try:
                payload = json.loads(post_body.decode("utf-8"))
                rgba = payload.get("rgba", [])
                w = int(payload.get("width", 0))
                h = int(payload.get("height", 0))
                classifier = VisionClassifier()
                res = classifier.analyze_pixels(rgba, w, h)
                out = {
                    "status": "ok",
                    "category": res.get("category", "non_botanical"),
                    "confidence": int(res.get("confidence", 0.5) * 100),
                    "label": res.get("label", "Unconfirmed"),
                    "species": res.get("species", "Flora"),
                    "reason": res.get("reason", "")
                }
            except Exception as e:
                out = {"status": "error", "message": str(e), "category": "non_botanical", "confidence": 30}

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(out).encode("utf-8"))
        else:
            self.send_error(404, "Not Found")

class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def run_server(port: int = 8080, host: str = "0.0.0.0"):
    handler = NaturaDashboardHandler
    with ThreadingHTTPServer((host, port), handler) as httpd:
        print(f"NATURA Web Dashboard running at http://{host}:{port}")
        httpd.serve_forever()

if __name__ == "__main__":
    import argparse
    default_port = int(os.environ.get("PORT", 8080))
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=default_port, help="Port to serve on (defaults to $PORT env var, then 8080)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host/interface to bind to")
    args = parser.parse_args()
    run_server(args.port, args.host)
