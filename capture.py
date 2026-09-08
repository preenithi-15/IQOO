from playwright.sync_api import sync_playwright
import time
from pathlib import Path

out_dir = Path("docs/screenshots")
out_dir.mkdir(parents=True, exist_ok=True)
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=chrome_path, headless=True)
    page = browser.new_page(
        viewport={"width": 430, "height": 1200},
        device_scale_factor=2
    )
    page.goto("http://localhost:8080/")
    time.sleep(1.2)

    page.evaluate("const s = document.getElementById('splash'); if(s) s.remove();")
    page.add_style_tag(content="""
        html, body { height: auto !important; overflow: visible !important; background: #f6f2ea !important; }
        #phone-wrap { height: auto !important; min-height: auto !important; display: block !important; }
        #app { height: auto !important; min-height: auto !important; max-height: none !important; width: 100% !important; border: none !important; border-radius: 0 !important; box-shadow: none !important; }
        main { overflow: visible !important; height: auto !important; min-height: auto !important; }
        .page { display: none !important; height: auto !important; min-height: auto !important; }
        .page.capture-active { display: block !important; padding-bottom: 50px !important; }
        .bottomnav { display: none !important; }
    """)
    time.sleep(0.3)

    pages_to_capture = [
        ("01_listen_live.png", "page-listen", ""),
        ("02_album_grid.png", "page-album", ""),
        ("03_moment_detail.png", "page-detail", "if(typeof openDetail === 'function' && albumGroups && albumGroups.length > 0) openDetail(albumGroups[0].id);"),
        ("04_learn_guide.png", "page-learn", "if(typeof openLearnDetail === 'function') openLearnDetail('insects', 0);"),
        ("05_nature_quest.png", "page-quest", ""),
        ("06_compose_mixer.png", "page-compose", ""),
    ]

    for filename, page_id, action in pages_to_capture:
        page.evaluate(f"""
            document.querySelectorAll('.page').forEach(p => p.classList.remove('capture-active'));
            {action}
            document.getElementById('{page_id}').classList.add('capture-active');
        """)
        time.sleep(0.5)
        needed_height = page.evaluate("Math.max(document.getElementById('app').scrollHeight, document.body.scrollHeight) + 50")
        page.set_viewport_size({"width": 430, "height": max(int(needed_height), 900)})
        time.sleep(0.3)
        page.locator("#app").screenshot(path=str(out_dir / filename))
        print(f"Captured {filename} with height {needed_height}px")

    browser.close()
    print("All screenshots successfully captured!")
