import json
import logging
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


logger = logging.getLogger(__name__)

# Viewport dimensions used for the screenshot
_VIEWPORT_WIDTH = 1024
_VIEWPORT_HEIGHT = 1024


def _build_html(prompt: str) -> str:
    """Return a self-contained HTML page that renders *prompt* for screenshotting."""
    escaped = (
        prompt
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width={_VIEWPORT_WIDTH}, initial-scale=1.0" />
  <title>Generated Image</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
      width: {_VIEWPORT_WIDTH}px;
      height: {_VIEWPORT_HEIGHT}px;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    }}
    .card {{
      width: 880px;
      padding: 60px 64px;
      background: rgba(255, 255, 255, 0.07);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 24px;
      backdrop-filter: blur(12px);
      box-shadow: 0 32px 64px rgba(0, 0, 0, 0.5);
    }}
    .label {{
      font-size: 13px;
      font-weight: 600;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: rgba(255, 255, 255, 0.45);
      margin-bottom: 24px;
    }}
    .prompt {{
      font-size: 28px;
      font-weight: 400;
      line-height: 1.55;
      color: #f0f4ff;
      word-break: break-word;
    }}
    .footer {{
      margin-top: 48px;
      font-size: 12px;
      color: rgba(255, 255, 255, 0.25);
      letter-spacing: 0.06em;
    }}
  </style>
</head>
<body>
  <div class="card">
    <p class="label">Generated prompt</p>
    <p class="prompt">{escaped}</p>
    <p class="footer">Rendered by browser automation pipeline</p>
  </div>
</body>
</html>"""


def generate(prompt: str) -> dict:
    """Render *prompt* in a headless Chromium browser and save a screenshot.

    Returns a dict with keys:
        ``image_path``  – absolute-ish path to the saved JPEG file (str)
        ``prompt``      – the original prompt string
        ``width``       – screenshot width in pixels
        ``height``      – screenshot height in pixels
        ``render_time`` – wall-clock seconds spent inside Playwright (float)
    """
    try:
        output_dir = Path("outputs")
        output_dir.mkdir(parents=True, exist_ok=True)

        safe_name = abs(hash(prompt))
        output_path = output_dir / f"output_{safe_name}.jpg"

        html_content = _build_html(prompt)

        render_start = time.monotonic()

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": _VIEWPORT_WIDTH, "height": _VIEWPORT_HEIGHT},
            )

            cookies_path = Path("cookies.json")
            if cookies_path.exists():
                try:
                    cookies = json.loads(cookies_path.read_text(encoding="utf-8"))
                    if isinstance(cookies, list):
                        context.add_cookies(cookies)
                        logger.info("Loaded %d cookie(s) from cookies.json", len(cookies))
                except Exception as cookie_error:
                    logger.warning("Failed loading cookies.json: %s", cookie_error)

            page = context.new_page()

            # Load the rendered HTML directly — no network round-trip needed.
            page.set_content(html_content, wait_until="networkidle")

            # Capture a full-page screenshot as JPEG.
            page.screenshot(
                path=str(output_path),
                type="jpeg",
                quality=95,
                full_page=False,
            )

            context.close()
            browser.close()

        render_time = time.monotonic() - render_start

        logger.info(
            "Image generated in %.2fs: %s", render_time, output_path
        )

        return {
            "image_path": str(output_path),
            "prompt": prompt,
            "width": _VIEWPORT_WIDTH,
            "height": _VIEWPORT_HEIGHT,
            "render_time": render_time,
        }
    except Exception as error:
        logger.exception("Failed generating image for prompt %r: %s", prompt, error)
        raise
