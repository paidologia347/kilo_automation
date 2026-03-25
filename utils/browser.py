import json
import logging
import random
import time
from pathlib import Path

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright


logger = logging.getLogger(__name__)


def generate(prompt):
    try:
        output_dir = Path("outputs")
        output_dir.mkdir(parents=True, exist_ok=True)

        safe_name = abs(hash(prompt))
        output_path = output_dir / f"output_{safe_name}.jpg"

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()

            cookies_path = Path("cookies.json")
            if cookies_path.exists():
                try:
                    cookies = json.loads(cookies_path.read_text(encoding="utf-8"))
                    if isinstance(cookies, list):
                        context.add_cookies(cookies)
                        logger.info("Loaded cookies from cookies.json")
                except Exception as cookie_error:
                    logger.warning("Failed loading cookies.json: %s", cookie_error)

            page = context.new_page()
            page.goto("about:blank")

            image = Image.new("RGB", (1024, 1024), color=(245, 245, 245))
            draw = ImageDraw.Draw(image)
            draw.text((40, 40), f"Generated prompt: {prompt}", fill=(20, 20, 20))
            image.save(output_path)

            delay_seconds = random.randint(5, 10)
            logger.info("Waiting %s seconds to simulate image generation", delay_seconds)
            time.sleep(delay_seconds)

            context.close()
            browser.close()

        logger.info("Image generated: %s", output_path)
        return str(output_path)
    except Exception as error:
        logger.exception("Failed generating image: %s", error)
        raise
