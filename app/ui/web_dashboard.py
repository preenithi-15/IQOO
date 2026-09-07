import http.server
import socketserver
import json
import urllib.parse
import sys
from pathlib import Path

# Add project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.natura_live.live_session import NaturaLiveSession
from app.ui.office_kit_bridge import VivoOfficeKitBridge
from data.lessons import NatureLanguageBook

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>■ NATURA — iQOO 15 Multimodal Nature Explorer</title>
    <style>
        :root {
            --bg-dark: #0a0f0d;
            --card-bg: #111a16;
            --accent-green: #00e676;
            --accent-gold: #ffd600;
            --accent-cyan: #00e5ff;
            --text-main: #e0f2f1;
            --text-muted: #80cbc4;
            --border-color: #1e3329;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: var(--bg-dark); color: var(--text-main); padding: 20px; }
        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--border-color); padding-bottom: 15px; margin-bottom: 20px; }
        .logo { font-size: 24px; font-weight: 800; letter-spacing: 2px; color: var(--accent-green); }
        .badge { background: #004d40; color: #a7ffeb; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; }
        .card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        .card h2 { font-size: 16px; text-transform: uppercase; color: var(--accent-cyan); margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
        .meter-container { margin-bottom: 12px; }
        .meter-label { display: flex; justify-content: space-between; font-size: 12px; color: var(--text-muted); margin-bottom: 4px; }
        .meter-bar { height: 8px; background: #1e2d26; border-radius: 4px; overflow: hidden; }
        .meter-fill { height: 100%; width: 75%; background: linear-gradient(90deg, var(--accent-green), var(--accent-gold)); border-radius: 4px; }
        .layer-box { background: #0c1410; border-left: 3px solid var(--accent-green); padding: 10px 14px; border-radius: 0 8px 8px 0; margin-bottom: 10px; font-size: 13px; }
        .layer-title { font-weight: 700; color: var(--accent-green); font-size: 11px; text-transform: uppercase; margin-bottom: 2px; }
        .stem-tag { display: inline-block; background: #132b20; color: #69f0ae; border: 1px solid #1b5e20; border-radius: 6px; padding: 3px 8px; font-size: 11px; margin: 2px; }
        .btn { background: var(--accent-green); color: #003318; border: none; padding: 10px 18px; border-radius: 8px; font-weight: 700; cursor: pointer; transition: 0.2s; }
        .btn:hover { background: #69f0ae; }
        pre { background: #080d0b; padding: 10px; border-radius: 8px; font-family: monospace; font-size: 11px; color: #a7ffeb; overflow-x: auto; line-height: 1.3; }
        .quest-item { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #16261e; font-size: 13px; }
        .quest-check { width: 18px; height: 18px; border-radius: 50%; background: #00e676; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 11px; color: #000; }
    </style>
</head>
<body>
    <header>
        <div>
            <div class="logo">■ NATURA</div>
            <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">iQOO 15 AI-Powered Multimodal Nature Explorer • Snapdragon 8 Elite Gen 5</p>
        </div>
        <div>
            <span class="badge">vivo Office Kit: GREEN LIGHT (Connected)</span>
            <span class="badge" style="background:#1a237e; color:#8c9eff;">NPU: 6.8ms</span>
        </div>
    </header>

    <div class="grid">
        <!-- NATURA LIVE SENSING -->
        <div class="card">
            <h2><span style="color:var(--accent-green)">●</span> NATURA LIVE — Multimodal Sensing</h2>
            <div class="meter-container">
                <div class="meter-label"><span>Acoustic SNR (Acoustic Clarity)</span><span>24.8 dB (EXCELLENT)</span></div>
                <div class="meter-bar"><div class="meter-fill" style="width: 85%;"></div></div>
            </div>
            <div class="meter-container">
                <div class="meter-label"><span>Peak Wingbeat Frequency</span><span>240.0 Hz (Locked)</span></div>
                <div class="meter-bar"><div class="meter-fill" style="width: 60%; background: var(--accent-cyan);"></div></div>
            </div>
            <div style="margin-top: 15px;">
                <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 6px;">LIVE ACOUSTIC SPECTROGRAM (48 kHz)</div>
                <pre>
 1.2kHz |   .   .   :   =   +   *   #   %   @   #
 600 Hz | :   =   +   *   #   %   @   %   #   *
 240 Hz | @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
   0 Hz | -------------------------------------
        | 0.0s    1.0s    2.0s    3.0s    4.0s
                </pre>
            </div>
            <div style="margin-top: 15px; display: flex; gap: 8px;">
                <button class="btn" onclick="alert('Capturing synchronized Nature Moment...')">Capture Nature Moment</button>
                <button class="btn" style="background:#263238; color:#cfd8dc;" onclick="alert('Frequency sonifier toggled to Heterodyne Ultrasonic Mode')">Sonify Ultrasound</button>
            </div>
        </div>

        <!-- NATURE INTERPRETER -->
        <div class="card">
            <h2>Evidence-Based Nature Interpreter</h2>
            <div class="layer-box" style="border-color: var(--accent-green);">
                <div class="layer-title">Layer 1: Scientific Interpretation (93% Confidence)</div>
                <p>Apis mellifera wingbeat observed at ~240 Hz fundamental frequency. Matches thoracic flight muscle contraction during floral nectar foraging.</p>
            </div>
            <div class="layer-box" style="border-color: var(--accent-cyan);">
                <div class="layer-title">Layer 2: AI Multimodal Fusion Reasoning</div>
                <p>Triple 50MP camera macro classifier correlated with acoustic harmonic series. Context engine confirmed optimal diurnal nectar secretion window.</p>
            </div>
            <div class="layer-box" style="border-color: var(--accent-gold);">
                <div class="layer-title">Layer 3: Poetic Nature Message</div>
                <p>"A golden weaver dances between blossoms, humming the ancient anthem of blooming life."</p>
            </div>
        </div>

        <!-- NATURE COMPOSER -->
        <div class="card">
            <h2>Nature Composer — Generative Music</h2>
            <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 12px;">Transforms natural recordings into music by mapping acoustic traits:</p>
            <div>
                <span class="stem-tag">Bee Activity → Rhythm / Clock (108 BPM)</span>
                <span class="stem-tag">Tree Cricket → Pentatonic Lead (E Minor)</span>
                <span class="stem-tag">Canopy Wind → Organic Ambient Pad</span>
                <span class="stem-tag">Rain Droplets → Stochastic Percussion</span>
            </div>
            <div style="margin-top: 20px; background: #0c1410; padding: 12px; border-radius: 8px; text-align: center;">
                <div style="font-size: 14px; font-weight: 700; color: var(--accent-green);">Track: "Morning in Chennai — 02:14"</div>
                <p style="font-size: 12px; color: var(--text-muted); margin: 6px 0 12px 0;">Generated directly from local bioacoustic field recording</p>
                <button class="btn" style="width: 100%;" onclick="alert('Playing synthesized Nature Soundscape...')">▶ Play Composition</button>
            </div>
        </div>

        <!-- 10-MINUTE NATURE QUEST -->
        <div class="card">
            <h2>Feature 10: 10-Minute Nature Quest</h2>
            <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 12px;">Active Mission: Biodiversity Micro-Expedition</p>
            <div class="quest-item">
                <div class="quest-check">✓</div>
                <div>Find 3 distinct natural sounds (Logged: Bee, Cricket, Bird)</div>
            </div>
            <div class="quest-item">
                <div class="quest-check">✓</div>
                <div>Visual sighting and macro lock of 1 pollinator</div>
            </div>
            <div class="quest-item">
                <div class="quest-check">✓</div>
                <div>Record plant acoustic substrate vibration</div>
            </div>
            <div class="quest-item">
                <div class="quest-check" style="background:#ffd600;">➔</div>
                <div>Render 30-second generative nature composition</div>
            </div>
        </div>
    </div>
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
        else:
            self.send_error(404, "Not Found")

def run_server(port: int = 8080):
    handler = NaturaDashboardHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"NATURA Web Dashboard & vivo Office Kit Server running at http://localhost:{port}")
        httpd.serve_forever()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080, help="Port to serve on")
    args = parser.parse_args()
    run_server(args.port)
