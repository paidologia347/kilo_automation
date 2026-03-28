import random


THEMES = ("business", "abstract", "tech", "lifestyle", "food", "nature")
SUBJECTS_BY_THEME = {
    "business": (
        "team strategy meeting with growth charts",
        "startup founder reviewing quarterly roadmap",
        "executive desk setup with financial reports",
        "remote work collaboration on productivity tools",
    ),
    "abstract": (
        "fluid gradient pattern with layered lighting",
        "geometric composition with minimalist textures",
        "soft blurred color waves with depth",
        "dynamic abstract lines in modern composition",
    ),
    "tech": (
        "developer workstation with code on multiple screens",
        "cloud infrastructure dashboard with system metrics",
        "ai concept scene with futuristic interface panels",
        "cybersecurity control center visualization",
    ),
    "lifestyle": (
        "morning routine with natural window lighting",
        "wellness-focused home workspace arrangement",
        "urban commuting scene in clean modern style",
        "minimal interior scene with daily essentials",
    ),
    "food": (
        "fresh plated meal shot from top-down angle",
        "artisan coffee and pastry in cozy cafe setting",
        "healthy ingredients flat lay with vibrant colors",
        "chef preparing gourmet dish in soft light",
    ),
    "nature": (
        "misty forest landscape at sunrise",
        "mountain trail with cinematic sky",
        "calm lakeside scene with reflections",
        "tropical foliage close-up with detailed texture",
    ),
}
STYLE_OPTIONS = ("minimal", "modern", "clean", "editorial")
LIGHTING_OPTIONS = ("soft light", "natural light", "cinematic")
COMPOSITION_OPTIONS = ("close-up", "top view", "wide shot", "symmetrical framing")


def _build_prompt(theme: str, subject: str) -> str:
    return (
        f"{subject}, {theme} theme, {random.choice(STYLE_OPTIONS)} style, "
        f"{random.choice(LIGHTING_OPTIONS)}, {random.choice(COMPOSITION_OPTIONS)}, "
        "commercial use, high resolution"
    )


def generate_daily_prompts() -> list[str]:
    """Generate exactly 100 prompts per day."""
    prompts = []
    for index in range(100):
        theme = THEMES[index % len(THEMES)]
        subject = random.choice(SUBJECTS_BY_THEME[theme])
        prompts.append(_build_prompt(theme, subject))

    random.shuffle(prompts)
    return prompts
