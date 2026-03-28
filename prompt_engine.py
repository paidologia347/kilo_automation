import random

from config import PROMPT_COUNT_MAX, PROMPT_COUNT_MIN


THEMES = (
    "business",
    "technology",
    "health",
    "lifestyle",
    "abstract background",
    "food",
    "nature",
    "finance",
    "education",
    "social media",
)
NON_ABSTRACT_THEMES = tuple(theme for theme in THEMES if theme != "abstract background")
LIGHTING_OPTIONS = ("soft light", "natural light", "cinematic")
STYLE_OPTIONS = ("minimal", "modern", "clean")
COMPOSITION_OPTIONS = ("close-up", "top view", "wide shot")
COLOR_OPTIONS = (
    "neutral tones",
    "soft pastel colors",
    "vibrant contrast",
    "cool blue palette",
    "warm earthy palette",
    "fresh green accents",
)
SUBJECTS_BY_CATEGORY = {
    "object": (
        "professional workspace with laptop and notebook",
        "smartphone with analytics dashboard",
        "healthy meal bowl with fresh ingredients",
        "stacked textbooks and digital tablet",
        "coffee cup beside strategic planning notes",
        "savings jar with calculator and documents",
    ),
    "people": (
        "confident entrepreneur presenting growth ideas",
        "developer collaborating in a modern office",
        "doctor consulting a patient in a clinic",
        "student learning through an online class",
        "content creator recording short-form videos",
        "family enjoying a balanced daily routine",
    ),
    "background": (
        "blurred corporate interior backdrop",
        "clean tech-inspired workspace backdrop",
        "organic wellness texture backdrop",
        "editorial food photography backdrop",
        "nature-inspired gradient backdrop",
        "social media ready studio backdrop",
    ),
}
ABSTRACT_SUBJECTS = (
    "abstract gradient background",
    "abstract geometric background",
    "abstract fluid wave background",
    "abstract soft blur background",
    "abstract paper-cut background",
    "abstract glowing line background",
)


def _build_prompt(theme: str, subject: str) -> str:
    lighting = random.choice(LIGHTING_OPTIONS)
    style = random.choice(STYLE_OPTIONS)
    composition = random.choice(COMPOSITION_OPTIONS)
    color = random.choice(COLOR_OPTIONS)
    return (
        f"{subject} for {theme}, {style} style, {lighting}, {color}, {composition}, "
        "clean background, commercial use, high resolution"
    )


def generate_daily_prompts() -> list[str]:
    """Generate 100-150 high-selling microstock prompts with balanced themes."""
    count = random.randint(PROMPT_COUNT_MIN, PROMPT_COUNT_MAX)
    abstract_target = max(1, int(round(count * 0.30)))
    non_abstract_target = count - abstract_target

    prompts: list[str] = []
    seen: set[str] = set()

    while len(prompts) < abstract_target:
        candidate = _build_prompt("abstract background", random.choice(ABSTRACT_SUBJECTS))
        if candidate not in seen:
            seen.add(candidate)
            prompts.append(candidate)

    category_sequence = ["object", "people", "background"] * ((non_abstract_target // 3) + 2)
    random.shuffle(category_sequence)

    index = 0
    attempts = 0
    max_attempts = non_abstract_target * 30
    while len(prompts) < count and attempts < max_attempts:
        attempts += 1
        theme = random.choice(NON_ABSTRACT_THEMES)
        category = category_sequence[index % len(category_sequence)]
        index += 1
        subject = random.choice(SUBJECTS_BY_CATEGORY[category])
        candidate = _build_prompt(theme, subject)
        if candidate in seen:
            continue
        seen.add(candidate)
        prompts.append(candidate)

    random.shuffle(prompts)
    return prompts
