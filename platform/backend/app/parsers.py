from typing import Any


def extract_module_number(module_id: str) -> int:
    parts = module_id.split("-")

    if len(parts) < 2:
        return 0

    try:
        return int(parts[1])
    except ValueError:
        return 0


def extract_title(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        stripped = line.strip()

        if stripped.startswith("# "):
            return stripped.removeprefix("# ").strip()

    return fallback


def slugify_heading(value: str) -> str:
    return (
        value.lower()
        .replace("ą", "a")
        .replace("ć", "c")
        .replace("ę", "e")
        .replace("ł", "l")
        .replace("ń", "n")
        .replace("ó", "o")
        .replace("ś", "s")
        .replace("ź", "z")
        .replace("ż", "z")
    )


def normalize_exercise_level(heading: str) -> str:
    normalized = slugify_heading(heading)

    if "rozgrzew" in normalized:
        return "warmup"

    if "sred" in normalized:
        return "medium"

    if "prakty" in normalized:
        return "practical"

    return "general"


def level_label(level: str) -> str:
    labels = {
        "warmup": "Rozgrzewka",
        "medium": "Srednie",
        "practical": "Praktyczne",
        "general": "Ogolne",
    }

    return labels.get(level, "Ogolne")


def split_exercise_sections(markdown: str) -> dict[str, str]:
    section_aliases = {
        "cel": "goal",
        "opis": "description_markdown",
        "ograniczenia / wskazowki": "constraints_markdown",
        "ograniczenia": "constraints_markdown",
        "wskazowki": "constraints_markdown",
        "oczekiwany efekt": "expected_effect_markdown",
    }
    sections = {
        "goal": "",
        "description_markdown": "",
        "constraints_markdown": "",
        "expected_effect_markdown": "",
    }
    current_section: str | None = None
    current_lines: list[str] = []

    def flush_section() -> None:
        if current_section is not None:
            sections[current_section] = "\n".join(current_lines).strip()

    for line in markdown.splitlines():
        stripped = line.strip()
        section_name = stripped.removesuffix(":")
        inline_value = ""

        if ":" in stripped:
            possible_name, possible_value = stripped.split(":", maxsplit=1)
            section_name = possible_name
            inline_value = possible_value.strip()

        section_key = section_aliases.get(slugify_heading(section_name))

        if section_key is not None:
            flush_section()
            current_section = section_key
            current_lines = [inline_value] if inline_value else []
            continue

        if current_section is None:
            current_section = "description_markdown"

        current_lines.append(line)

    flush_section()

    return sections


def parse_exercises_markdown(markdown: str) -> list[dict[str, str | int]]:
    exercises: list[dict[str, str | int]] = []
    current_level = "general"
    current_level_label = level_label(current_level)
    current_exercise: dict[str, Any] | None = None
    current_lines: list[str] = []

    def flush_exercise() -> None:
        if current_exercise is None:
            return

        sections = split_exercise_sections("\n".join(current_lines).strip())
        exercises.append({**current_exercise, **sections})

    for line in markdown.splitlines():
        if line.startswith("## ") and not line.startswith("### "):
            flush_exercise()
            current_exercise = None
            current_lines = []
            current_level_label = line.removeprefix("## ").strip()
            current_level = normalize_exercise_level(current_level_label)
            continue

        if line.startswith("### Ćwiczenie ") or line.startswith("### Cwiczenie "):
            flush_exercise()
            heading = line.removeprefix("### ").strip()
            title = heading
            exercise_number = len(exercises) + 1

            if ":" in heading:
                number_part, title_part = heading.split(":", maxsplit=1)
                title = title_part.strip()
                digits = "".join(character for character in number_part if character.isdigit())

                if digits:
                    exercise_number = int(digits)

            current_exercise = {
                "id": f"exercise-{exercise_number}",
                "number": exercise_number,
                "title": title,
                "level": current_level,
                "level_label": current_level_label,
            }
            current_lines = []
            continue

        if current_exercise is not None:
            current_lines.append(line)

    flush_exercise()

    return exercises


def normalize_knowledge_check_category(heading: str) -> str:
    normalized = slugify_heading(heading)

    if "pytania otwarte" in normalized:
        return "open_questions"

    if "krotkie scenariusze" in normalized:
        return "scenarios"

    if "co by bylo gdyby" in normalized:
        return "what_if"

    if "typowe bledy" in normalized:
        return "common_mistakes"

    if "samoocena" in normalized:
        return "self_assessment"

    if "mini zadanie" in normalized:
        return "active_task"

    return "general"


def parse_knowledge_check_markdown(markdown: str) -> list[dict[str, str | int]]:
    items: list[dict[str, str | int]] = []
    current_category = "general"
    current_category_label = "Ogolne"
    pending_lines: list[str] = []

    def flush_pending() -> None:
        nonlocal pending_lines

        prompt_markdown = "\n".join(pending_lines).strip()

        if not prompt_markdown:
            pending_lines = []
            return

        item_number = len(items) + 1
        items.append(
            {
                "id": f"knowledge-check-{item_number}",
                "number": item_number,
                "category": current_category,
                "category_label": current_category_label,
                "prompt_markdown": prompt_markdown,
            }
        )
        pending_lines = []

    for line in markdown.splitlines():
        if line.startswith("# "):
            continue

        if line.startswith("## "):
            flush_pending()
            current_category_label = line.removeprefix("## ").strip()
            current_category = normalize_knowledge_check_category(current_category_label)
            continue

        stripped = line.strip()
        starts_numbered_item = bool(stripped) and stripped[0].isdigit() and ". " in stripped[:5]
        starts_bullet_item = stripped.startswith("- ")

        if current_category == "active_task":
            if stripped:
                pending_lines.append(line)
            elif pending_lines:
                pending_lines.append(line)
            continue

        if starts_numbered_item or starts_bullet_item:
            flush_pending()
            if starts_bullet_item:
                pending_lines = [stripped.removeprefix("- ").strip()]
            else:
                _, item_text = stripped.split(". ", maxsplit=1)
                pending_lines = [item_text.strip()]
            continue

        if pending_lines or stripped:
            pending_lines.append(line)

    flush_pending()

    return items


def extract_markdown_section(markdown: str, heading: str) -> str:
    target = slugify_heading(heading)
    current_heading = ""
    current_lines: list[str] = []

    for line in markdown.splitlines():
        if line.startswith("## "):
            if slugify_heading(current_heading) == target:
                return "\n".join(current_lines).strip()

            current_heading = line.removeprefix("## ").strip()
            current_lines = []
            continue

        if current_heading:
            current_lines.append(line)

    if slugify_heading(current_heading) == target:
        return "\n".join(current_lines).strip()

    return ""
