import random

from config import PROMPT_COUNT_MAX, PROMPT_COUNT_MIN


THEMES = ("islamic", "ramadan", "eid")
PROMPT_TEMPLATES = (
    "High-detail {theme} calligraphy art with elegant gold accents",
    "Minimalist {theme} lantern composition, soft cinematic lighting",
    "Premium {theme} greeting card design, floral arabesque pattern",
    "Modern {theme} geometric wallpaper, rich emerald palette",
    "Beautiful {theme} mosque silhouette at dusk, ultra-detailed",
    "Festive {theme} social media banner, clean typography space",
    "Luxury {theme} invitation background with crescent moon motif",
    "Warm {theme} family celebration scene, realistic style",
    "Serene {theme} prayer corner interior render, natural light",
    "Traditional {theme} ornament pattern, seamless high-resolution texture",
)


def generate_daily_prompts() -> list[str]:
    """Generate 100-150 daily prompts across islamic/ramadan/eid themes."""
    count = random.randint(PROMPT_COUNT_MIN, PROMPT_COUNT_MAX)
    prompts: list[str] = []
    for _ in range(count):
        template = random.choice(PROMPT_TEMPLATES)
        theme = random.choice(THEMES)
        prompts.append(template.format(theme=theme))
    return prompts
