from __future__ import annotations

import datetime as dt
import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

VALID_MODE_VALUES = {
    "balanced",
    "vowel-heavy",
    "consonant-heavy",
    "hardmode-safe",
    "daily-rotation",
}
DEFAULT_STARTER_MODE = "balanced"
VOWELS = set("aeiou")

FALLBACK_WORDS = [
    "adieu",
    "alert",
    "alone",
    "arise",
    "audio",
    "baker",
    "blend",
    "caper",
    "cater",
    "chime",
    "clamp",
    "crane",
    "crisp",
    "earth",
    "glint",
    "irate",
    "later",
    "learn",
    "least",
    "metal",
    "ocean",
    "paint",
    "place",
    "point",
    "ratio",
    "react",
    "rhyme",
    "roast",
    "scale",
    "share",
    "slate",
    "smile",
    "snare",
    "sound",
    "spore",
    "stare",
    "stern",
    "tares",
    "trace",
    "train",
]

CURATED_BALANCED = [
    "slate",
    "crane",
    "trace",
    "stare",
    "arise",
    "irate",
    "raise",
    "react",
    "alter",
    "later",
    "snare",
    "least",
    "cater",
    "crate",
    "alert",
]

CURATED_VOWEL_HEAVY = [
    "adieu",
    "audio",
    "irate",
    "ouija",
    "aurei",
    "arise",
    "aisle",
    "alone",
    "ocean",
    "ratio",
]

CURATED_CONSONANT_HEAVY = [
    "stern",
    "clamp",
    "crisp",
    "blend",
    "print",
    "torch",
    "shunt",
    "chord",
    "glint",
    "wring",
]

CURATED_HARDMODE_SAFE = [
    "slate",
    "crane",
    "trace",
    "stare",
    "arise",
    "clamp",
    "stern",
    "point",
    "learn",
    "sound",
]


def _resolve_path(raw_path: str) -> Path:
    p = Path(raw_path)
    if p.is_absolute():
        return p
    return (BASE_DIR / p).resolve()


def _safe_getenv(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return value.strip()


load_dotenv(BASE_DIR / ".env")

DISCORD_TOKEN = _safe_getenv("DISCORD_TOKEN", "")
if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN is required")

GUILD_ID_RAW = _safe_getenv("GUILD_ID", "")
GUILD_ID = int(GUILD_ID_RAW) if GUILD_ID_RAW else None

WORD_LIST_PATH = _resolve_path(_safe_getenv("WORD_LIST_PATH", "./data/words_5.txt"))
STARTER_PREFS_PATH = _resolve_path(
    _safe_getenv("STARTER_PREFS_PATH", "./data/starter_prefs.json")
)
STARTER_PREFS_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_word_list(path: Path) -> List[str]:
    words: List[str] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            w = line.strip().lower()
            if re.fullmatch(r"[a-z]{5}", w):
                words.append(w)
    if not words:
        words = FALLBACK_WORDS.copy()
    return sorted(set(words))


WORDS = load_word_list(WORD_LIST_PATH)


def build_stats(words: Sequence[str]) -> Tuple[Counter[str], List[Counter[str]]]:
    letter_presence: Counter[str] = Counter()
    positional = [Counter() for _ in range(5)]
    for word in words:
        seen = set()
        for idx, ch in enumerate(word):
            positional[idx][ch] += 1
            if ch not in seen:
                letter_presence[ch] += 1
                seen.add(ch)
    return letter_presence, positional


GLOBAL_LETTER_PRESENCE, GLOBAL_POSITIONAL = build_stats(WORDS)


def parse_pattern(raw: str) -> str:
    value = raw.strip().lower().replace(" ", "")
    if not value:
        value = "_____"
    if not re.fullmatch(r"[a-z_]{5}", value):
        raise ValueError("pattern must be 5 chars using letters and _")
    return value


def parse_absent(raw: str) -> set[str]:
    value = re.sub(r"[^a-z]", "", raw.lower())
    return set(value)


def parse_yellow(raw: str) -> List[Tuple[str, int]]:
    value = raw.strip().lower()
    if not value:
        return []

    items = [token.strip() for token in value.split(",") if token.strip()]
    parsed: List[Tuple[str, int]] = []

    for token in items:
        match = re.fullmatch(r"([a-z])([1-5])", token)
        if not match:
            raise ValueError("yellow must look like a2,r5")
        letter = match.group(1)
        index = int(match.group(2)) - 1
        parsed.append((letter, index))

    return parsed


def required_letter_minimums(pattern: str, yellow: Sequence[Tuple[str, int]]) -> Dict[str, int]:
    minima: Dict[str, int] = {}
    for ch in pattern:
        if ch != "_":
            minima[ch] = minima.get(ch, 0) + 1
    for ch, _ in yellow:
        minima[ch] = max(minima.get(ch, 0), 1)
    return minima


def filter_candidates(
    words: Sequence[str],
    pattern: str,
    yellow: Sequence[Tuple[str, int]],
    absent: set[str],
) -> List[str]:
    minima = required_letter_minimums(pattern, yellow)
    blocked_absent = absent - set(minima.keys())

    output: List[str] = []

    for word in words:
        if any(pattern[idx] != "_" and word[idx] != pattern[idx] for idx in range(5)):
            continue

        yellow_ok = True
        for ch, idx in yellow:
            if word[idx] == ch or ch not in word:
                yellow_ok = False
                break
        if not yellow_ok:
            continue

        if any(ch in word for ch in blocked_absent):
            continue

        wc = Counter(word)
        if any(wc[ch] < need for ch, need in minima.items()):
            continue

        output.append(word)

    return output


def score_word(
    word: str,
    letter_presence: Counter[str],
    positional: Sequence[Counter[str]],
    total: int,
) -> float:
    unique = set(word)
    unique_count = len(unique)
    total_f = float(max(total, 1))

    coverage = sum(letter_presence[ch] for ch in unique) / total_f
    positional_fit = sum(positional[idx][ch] for idx, ch in enumerate(word)) / total_f
    vowel_count = sum(1 for ch in word if ch in VOWELS)

    vowel_balance_bonus = 1.0 - abs(vowel_count - 2) * 0.3
    repeat_penalty = max(0, 5 - unique_count) * 0.4

    return (
        coverage * 4.0
        + positional_fit * 2.8
        + unique_count * 0.7
        + vowel_balance_bonus
        - repeat_penalty
    )


def rank_words(words: Sequence[str], limit: int) -> List[Tuple[str, float]]:
    if not words:
        return []
    letter_presence, positional = build_stats(words)
    total = len(words)
    scored = [
        (word, score_word(word, letter_presence, positional, total)) for word in words
    ]
    scored.sort(key=lambda entry: entry[1], reverse=True)
    return scored[:limit]


def _starter_mode_weight(mode: str, word: str) -> float:
    vowels = sum(1 for ch in word if ch in VOWELS)
    unique_count = len(set(word))

    if mode == "vowel-heavy":
        return vowels * 1.7 - abs(unique_count - 5) * 0.2
    if mode == "consonant-heavy":
        return (5 - vowels) * 1.3 - max(0, vowels - 2) * 1.0 + unique_count * 0.2
    if mode == "hardmode-safe":
        return 1.5 if unique_count == 5 and 1 <= vowels <= 2 else -3.0
    return 0.0


def _curated_for_mode(mode: str) -> List[str]:
    base: List[str]
    if mode == "balanced":
        base = CURATED_BALANCED
    elif mode == "vowel-heavy":
        base = CURATED_VOWEL_HEAVY
    elif mode == "consonant-heavy":
        base = CURATED_CONSONANT_HEAVY
    elif mode == "hardmode-safe":
        base = CURATED_HARDMODE_SAFE
    else:
        base = CURATED_BALANCED
    return [w for w in base if w in WORDS]


def _rank_starters_for_mode(mode: str, limit: int) -> List[str]:
    letter_presence = GLOBAL_LETTER_PRESENCE
    positional = GLOBAL_POSITIONAL
    total = len(WORDS)

    scored: List[Tuple[str, float]] = []
    for word in WORDS:
        base = score_word(word, letter_presence, positional, total)
        total_score = base + _starter_mode_weight(mode, word)

        if mode == "vowel-heavy" and sum(1 for c in word if c in VOWELS) < 3:
            total_score -= 1.8
        if mode == "consonant-heavy" and sum(1 for c in word if c in VOWELS) > 2:
            total_score -= 2.0
        if mode == "hardmode-safe" and len(set(word)) < 5:
            total_score -= 2.2

        scored.append((word, total_score))

    scored.sort(key=lambda item: item[1], reverse=True)

    curated = _curated_for_mode(mode)
    merged: List[str] = []
    for word in curated + [word for word, _ in scored]:
        if word not in merged:
            merged.append(word)
        if len(merged) >= limit:
            break

    return merged


def get_daily_starter() -> str:
    pool = _rank_starters_for_mode("balanced", 120)
    if not pool:
        return "slate"
    day_index = dt.date.today().toordinal() % len(pool)
    return pool[day_index]


def load_prefs(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(data, dict):
        return {}

    prefs: Dict[str, str] = {}
    for user_id, mode in data.items():
        if isinstance(user_id, str) and isinstance(mode, str) and mode in VALID_MODE_VALUES:
            prefs[user_id] = mode
    return prefs


def save_prefs(path: Path, prefs: Dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(prefs, indent=2, sort_keys=True), encoding="utf-8")


STARTER_PREFS = load_prefs(STARTER_PREFS_PATH)


def user_starter_mode(user_id: int) -> str:
    mode = STARTER_PREFS.get(str(user_id), DEFAULT_STARTER_MODE)
    if mode in VALID_MODE_VALUES:
        return mode
    return DEFAULT_STARTER_MODE


def set_user_starter_mode(user_id: int, mode: str) -> None:
    STARTER_PREFS[str(user_id)] = mode
    save_prefs(STARTER_PREFS_PATH, STARTER_PREFS)


def explain_guess_quality(
    guess: str,
    pattern: str,
    yellow: Sequence[Tuple[str, int]],
    absent: set[str],
) -> Tuple[float, int, List[str], List[str], List[str], List[str]]:
    candidates = filter_candidates(WORDS, pattern, yellow, absent)
    baseline_pool = candidates if candidates else WORDS

    letter_presence, positional = build_stats(baseline_pool)
    total = len(baseline_pool)

    guess_score = score_word(guess, letter_presence, positional, total)
    score_list = [score_word(w, letter_presence, positional, total) for w in baseline_pool]
    score_list.sort()

    better_or_equal = sum(1 for s in score_list if s <= guess_score)
    percentile = int((better_or_equal / max(1, len(score_list))) * 100)

    strengths: List[str] = []
    cautions: List[str] = []
    violations: List[str] = []

    unique_letters = len(set(guess))
    vowel_count = sum(1 for ch in guess if ch in VOWELS)

    if unique_letters >= 5:
        strengths.append("Uses five unique letters for strong coverage.")
    elif unique_letters == 4:
        strengths.append("Uses four unique letters, still decent for info gain.")
    else:
        cautions.append("Repeated letters reduce early information gain.")

    if 1 <= vowel_count <= 3:
        strengths.append("Vowel balance is healthy for an early/mid guess.")
    else:
        cautions.append("Vowel balance is unusual; consider a more balanced follow-up.")

    for idx, pch in enumerate(pattern):
        if pch != "_" and guess[idx] != pch:
            violations.append(
                f"Position {idx + 1} is fixed as `{pch.upper()}`, but guess has `{guess[idx].upper()}`."
            )

    for letter, idx in yellow:
        if guess[idx] == letter:
            violations.append(
                f"`{letter.upper()}` is known yellow at pos {idx + 1}, but guess reuses that blocked slot."
            )
        if letter not in guess:
            cautions.append(f"Guess does not include known present letter `{letter.upper()}`.")

    minima = required_letter_minimums(pattern, yellow)
    guess_counter = Counter(guess)
    for ch, minimum in minima.items():
        if guess_counter[ch] < minimum:
            violations.append(f"Guess is missing required letter `{ch.upper()}`.")

    blocked_absent = absent - set(minima.keys())
    present_blocked = sorted(ch for ch in guess if ch in blocked_absent)
    if present_blocked:
        violations.append(
            "Guess includes excluded letters: "
            + ", ".join(f"`{ch.upper()}`" for ch in sorted(set(present_blocked)))
            + "."
        )

    top_next = [word for word, _ in rank_words(baseline_pool, 3)]

    return guess_score, percentile, strengths, cautions, violations, top_next


class WordleHelperBot(commands.Bot):
    async def setup_hook(self) -> None:
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f"[sync] Synced commands to guild {GUILD_ID}")
        else:
            await self.tree.sync()
            print("[sync] Synced commands globally")


intents = discord.Intents.default()
bot = WordleHelperBot(command_prefix="!", intents=intents)


@bot.event
async def on_ready() -> None:
    user_tag = str(bot.user) if bot.user else "unknown"
    print(f"[ready] Logged in as {user_tag}")


@app_commands.describe(
    mode="Starter strategy",
    save_as_default="Save this mode for your next /starter call",
)
@app_commands.choices(
    mode=[
        app_commands.Choice(name="Balanced", value="balanced"),
        app_commands.Choice(name="Vowel-heavy", value="vowel-heavy"),
        app_commands.Choice(name="Consonant-heavy", value="consonant-heavy"),
        app_commands.Choice(name="Hardmode-safe", value="hardmode-safe"),
        app_commands.Choice(name="Daily rotation", value="daily-rotation"),
    ]
)
@bot.tree.command(name="starter", description="Get strong Wordle starting words")
async def starter_slash(
    interaction: discord.Interaction,
    mode: Optional[app_commands.Choice[str]] = None,
    save_as_default: bool = False,
) -> None:
    selected_mode = mode.value if mode else user_starter_mode(interaction.user.id)
    if selected_mode not in VALID_MODE_VALUES:
        selected_mode = DEFAULT_STARTER_MODE

    if selected_mode == "daily-rotation":
        today_word = get_daily_starter()
        alternates = _rank_starters_for_mode("balanced", 5)
        line = f"Today's rotation pick: `{today_word.upper()}`"
        if alternates:
            line += "\nAlternates: " + ", ".join(f"`{w.upper()}`" for w in alternates)
        response = line
    else:
        picks = _rank_starters_for_mode(selected_mode, 5)
        response = (
            f"Mode: **{selected_mode}**\n"
            f"Top starters: {', '.join(f'`{w.upper()}`' for w in picks)}"
        )

    if save_as_default:
        set_user_starter_mode(interaction.user.id, selected_mode)
        response += "\nSaved as your default starter mode."

    await interaction.response.send_message(response)


@app_commands.describe(
    pattern="Known green letters using _ for unknowns (example: _r__e)",
    yellow="Known yellow slots as letter+position (example: a2,r5)",
    absent="Known absent letters (example: tns)",
    limit="How many suggestions to return",
)
@bot.tree.command(name="solve", description="Suggest strong next guesses from your clues")
async def solve_slash(
    interaction: discord.Interaction,
    pattern: str = "_____",
    yellow: str = "",
    absent: str = "",
    limit: app_commands.Range[int, 1, 10] = 5,
) -> None:
    try:
        parsed_pattern = parse_pattern(pattern)
        parsed_yellow = parse_yellow(yellow)
        parsed_absent = parse_absent(absent)
    except ValueError as exc:
        await interaction.response.send_message(f"Input error: {exc}", ephemeral=True)
        return

    candidates = filter_candidates(WORDS, parsed_pattern, parsed_yellow, parsed_absent)

    if not candidates:
        await interaction.response.send_message(
            "No candidates matched those clues. Double-check pattern/yellow/absent.",
            ephemeral=True,
        )
        return

    ranked = rank_words(candidates, int(limit))
    lines = [
        f"Candidates left: **{len(candidates)}**",
        "Best next guesses: " + ", ".join(f"`{word.upper()}`" for word, _ in ranked),
    ]
    await interaction.response.send_message("\n".join(lines))


@app_commands.describe(
    guess="Your planned guess word (5 letters)",
    pattern="Known green letters using _ for unknowns (example: _r__e)",
    yellow="Known yellow slots as letter+position (example: a2,r5)",
    absent="Known absent letters (example: tns)",
)
@bot.tree.command(name="teach", description="Score a guess and explain how strong it is")
async def teach_slash(
    interaction: discord.Interaction,
    guess: str,
    pattern: str = "_____",
    yellow: str = "",
    absent: str = "",
) -> None:
    normalized_guess = guess.strip().lower()
    if not re.fullmatch(r"[a-z]{5}", normalized_guess):
        await interaction.response.send_message(
            "Guess must be exactly 5 letters.", ephemeral=True
        )
        return

    try:
        parsed_pattern = parse_pattern(pattern)
        parsed_yellow = parse_yellow(yellow)
        parsed_absent = parse_absent(absent)
    except ValueError as exc:
        await interaction.response.send_message(f"Input error: {exc}", ephemeral=True)
        return

    score, percentile, strengths, cautions, violations, top_next = explain_guess_quality(
        normalized_guess,
        parsed_pattern,
        parsed_yellow,
        parsed_absent,
    )

    band = "excellent" if percentile >= 85 else "good" if percentile >= 65 else "okay"

    lines = [
        f"Guess: `{normalized_guess.upper()}`",
        f"Teaching score: **{band}** ({percentile}th percentile among current candidates)",
        f"Raw score: `{score:.2f}`",
    ]

    if strengths:
        lines.append("Strengths: " + " ".join(strengths))
    if cautions:
        lines.append("Cautions: " + " ".join(cautions))
    if violations:
        lines.append("Clue conflicts: " + " ".join(violations))

    if top_next:
        lines.append("Strong alternatives: " + ", ".join(f"`{w.upper()}`" for w in top_next))

    await interaction.response.send_message("\n".join(lines))


@bot.tree.command(name="wordlehelp", description="Show Wordle helper command usage")
async def wordle_help_slash(interaction: discord.Interaction) -> None:
    text = "\n".join(
        [
            "**Wordle Helper Commands**",
            "- `/starter [mode] [save_as_default]` get strong opening words",
            "- `/solve pattern:<_r__e> yellow:<a2,r5> absent:<tns>` solve from clues",
            "- `/teach guess:<crane> ...` score your guess quality and get coaching",
        ]
    )
    await interaction.response.send_message(text, ephemeral=True)


@bot.tree.error
async def on_tree_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
) -> None:
    print(f"[command-error] {error}")
    if interaction.response.is_done():
        await interaction.followup.send("Command failed. Please try again.", ephemeral=True)
    else:
        await interaction.response.send_message(
            "Command failed. Please try again.", ephemeral=True
        )


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
