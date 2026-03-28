import json
import logging
import os
import random
import time
from pathlib import Path
from uuid import uuid4

from playwright.sync_api import sync_playwright


logger = logging.getLogger(__name__)

IMAGE_GENERATOR_URL = os.getenv("IMAGE_GENERATOR_URL", "https://example.com/")
PROMPT_INPUT_SELECTOR = os.getenv("PROMPT_INPUT_SELECTOR", "textarea[name='prompt']")
GENERATE_BUTTON_SELECTOR = os.getenv(
    "GENERATE_BUTTON_SELECTOR",
    "button:has-text('Generate')",
)
GENERATED_IMAGE_SELECTOR = os.getenv("GENERATED_IMAGE_SELECTOR", "img.generated-image")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/output")
MAX_RETRIES = 2
RANDOM_DELAY_MIN = float(os.getenv("RANDOM_DELAY_MIN", "5"))
RANDOM_DELAY_MAX = float(os.getenv("RANDOM_DELAY_MAX", "10"))
TIMEOUT_MS = 60_000
_VIEWPORT_WIDTH = 1024
_VIEWPORT_HEIGHT = 1024


def _get_random_delay_bounds() -> tuple[float, float]:
    delay_min = RANDOM_DELAY_MIN
    delay_max = RANDOM_DELAY_MAX
    if delay_min > delay_max:
        delay_min, delay_max = delay_max, delay_min
    return delay_min, delay_max


def _load_cookies(context) -> None:
    cookies_path = Path("cookies.json")
    if not cookies_path.exists():
        print("[browser] cookies.json not found, skipping cookie load")
        return

    try:
        cookies = json.loads(cookies_path.read_text(encoding="utf-8"))
        if isinstance(cookies, list):
            context.add_cookies(cookies)
            print(f"[browser] loaded {len(cookies)} cookie(s) from cookies.json")
    except Exception as error:
        print(f"[browser] failed loading cookies.json: {error}")


def generate_image(prompt: str) -> str:
    """Generate an image for *prompt* using a Playwright browser session."""
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    total_attempts = MAX_RETRIES + 1

    for attempt in range(1, total_attempts + 1):
        output_path = output_dir / f"generated_{uuid4().hex}.png"
        print(f"[browser] starting generation attempt {attempt}/{total_attempts}")
        try:
            with sync_playwright() as playwright:
                print("[browser] launching headless Chromium")
                browser = playwright.chromium.launch(headless=True)
                context = None
                try:
                    context = browser.new_context(accept_downloads=True)
                    _load_cookies(context)

                    page = context.new_page()
                    print(f"[browser] opening generator website: {IMAGE_GENERATOR_URL}")
                    page.goto(IMAGE_GENERATOR_URL, wait_until="domcontentloaded", timeout=TIMEOUT_MS)

                    print(f"[browser] filling prompt input: {PROMPT_INPUT_SELECTOR}")
                    page.fill(PROMPT_INPUT_SELECTOR, prompt, timeout=TIMEOUT_MS)

                    print(f"[browser] clicking generate button: {GENERATE_BUTTON_SELECTOR}")
                    page.click(GENERATE_BUTTON_SELECTOR, timeout=TIMEOUT_MS)

                    delay_min, delay_max = _get_random_delay_bounds()
                    delay = random.uniform(delay_min, delay_max)
                    print(f"[browser] waiting random delay: {delay:.2f}s")
                    time.sleep(delay)

                    print(f"[browser] waiting for generated image: {GENERATED_IMAGE_SELECTOR}")
                    image = page.locator(GENERATED_IMAGE_SELECTOR).first
                    image.wait_for(state="visible", timeout=TIMEOUT_MS)

                    print(f"[browser] saving generated image to {output_path}")
                    image_bytes = image.screenshot()
                    output_path.write_bytes(image_bytes)
                finally:
                    if context is not None:
                        context.close()
                    browser.close()

            logger.info("Image generated for prompt %r: %s", prompt, output_path)
            print(f"[browser] generation complete: {output_path}")
            return str(output_path)
        except Exception as error:
            logger.exception("Image generation attempt %s failed: %s", attempt, error)
            print(f"[browser] attempt {attempt} failed: {error}")
            if output_path.exists():
                output_path.unlink(missing_ok=True)
            if attempt == total_attempts:
                raise


def generate(prompt: str) -> dict:
    """Backward-compatible wrapper used by older call sites."""
    start = time.monotonic()
    image_path = generate_image(prompt)
    return {
        "image_path": image_path,
        "prompt": prompt,
        "width": _VIEWPORT_WIDTH,
        "height": _VIEWPORT_HEIGHT,
        "render_time": time.monotonic() - start,
    }
