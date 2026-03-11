import asyncio
import os
import uuid
from pathlib import Path
from urllib.parse import urlparse

import discord
import imageio
import requests
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

# ---------------- ENV ----------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID_RAW = os.getenv("GUILD_ID")
SYNC_GLOBAL_COMMANDS = os.getenv("SYNC_GLOBAL_COMMANDS", "false").lower() == "true"

if not TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN in environment or .env file.")

if not GUILD_ID_RAW:
    raise RuntimeError("Missing GUILD_ID in environment or .env file.")

try:
    GUILD_ID = int(GUILD_ID_RAW)
except ValueError as exc:
    raise RuntimeError("GUILD_ID must be a valid integer Discord guild ID.") from exc

# ---------------- PATHS / LIMITS ----------------
BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)

SAFE_MARGIN = 12
DOWNLOAD_TIMEOUT = (5, 25)
MAX_INPUT_BYTES = 20 * 1024 * 1024
MAX_FRAMES = 300
MAX_PIXELS_PER_FRAME = 1920 * 1080 * 2
ALLOWED_EXTENSIONS = {".gif", ".png", ".apng"}
MAX_DISCORD_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_CONCURRENT_JOBS = max(1, int(os.getenv("MAX_CONCURRENT_JOBS", "2")))
JOB_TIMEOUT_SECONDS = max(15, int(os.getenv("JOB_TIMEOUT_SECONDS", "120")))

# ---------------- BOT ----------------
intents = discord.Intents.none()
bot = commands.Bot(command_prefix=None, intents=intents)
_has_synced = False
processing_semaphore = asyncio.Semaphore(MAX_CONCURRENT_JOBS)

# ---------------- FONT OPTIONS ----------------
FONT_MAP = {
    "impact": BASE_DIR / "impact.ttf",
    "arial": BASE_DIR / "arial.ttf",
    "comic": BASE_DIR / "comic.ttf",
}

FONT_CHOICES = [
    app_commands.Choice(name="Impact (Meme)", value="impact"),
    app_commands.Choice(name="Arial", value="arial"),
    app_commands.Choice(name="Comic Sans", value="comic"),
]

OUTLINE_CHOICES = [
    app_commands.Choice(name="None", value=0),
    app_commands.Choice(name="Thin", value=2),
    app_commands.Choice(name="Medium", value=3),
    app_commands.Choice(name="Thick", value=5),
]

FORMAT_CHOICES = [
    app_commands.Choice(name="Auto (recommended)", value="auto"),
    app_commands.Choice(name="GIF (classic)", value="gif"),
    app_commands.Choice(name="APNG (best quality)", value="apng"),
]


# ---------------- HELPERS ----------------
def _normalize_ext(value: str | None, default: str = ".gif") -> str:
    if not value:
        return default
    ext = value.lower()
    if not ext.startswith("."):
        ext = f".{ext}"
    return ext if ext in ALLOWED_EXTENSIONS else default


def _ext_from_url(url: str) -> str:
    parsed = urlparse(url)
    return _normalize_ext(Path(parsed.path).suffix)


def _ext_from_filename(filename: str | None) -> str:
    return _normalize_ext(Path(filename or "").suffix)


def download_file(url: str, path: Path, max_bytes: int = MAX_INPUT_BYTES) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http/https URLs are supported.")

    with requests.get(url, stream=True, timeout=DOWNLOAD_TIMEOUT) as response:
        response.raise_for_status()

        content_type = (response.headers.get("Content-Type") or "").lower()
        if content_type and not content_type.startswith("image/"):
            raise ValueError("URL did not return an image.")

        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > max_bytes:
            raise ValueError("Input file is too large (max 20MB).")

        total = 0
        with open(path, "wb") as file:
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if not chunk:
                    continue
                total += len(chunk)
                if total > max_bytes:
                    raise ValueError("Input file is too large (max 20MB).")
                file.write(chunk)


def has_transparency(img: Image.Image) -> bool:
    if img.mode in ("RGBA", "LA"):
        alpha = img.getchannel("A")
        return alpha.getextrema()[0] < 255
    return False


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""

    for word in words:
        test = current + (" " if current else "") + word
        if draw.textlength(test, font=font) <= max_width:
            current = test
        elif current:
            lines.append(current)
            current = word
        else:
            lines.append(word)

    if current:
        lines.append(current)

    return lines or [""]


def autoscale_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_path: Path,
    max_width: int,
    start_size: int,
) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    size = start_size
    font = ImageFont.truetype(str(font_path), size)
    lines = wrap_text(draw, text, font, max_width)

    while size >= 14:
        font = ImageFont.truetype(str(font_path), size)
        lines = wrap_text(draw, text, font, max_width)
        if max(draw.textlength(line, font=font) for line in lines) <= max_width:
            return font, lines
        size -= 2

    return font, lines


def draw_caption(
    img: Image.Image,
    text: str,
    font_path: Path,
    font_size: int,
    position: str,
    outline_thickness: int,
    background: bool,
) -> None:
    draw = ImageDraw.Draw(img)
    max_width = img.width - SAFE_MARGIN * 2

    font, lines = autoscale_font(draw, text, font_path, max_width, font_size)
    ascent, descent = font.getmetrics()
    line_height = ascent + descent + 4
    block_height = line_height * len(lines)

    y = SAFE_MARGIN if position == "top" else img.height - block_height - SAFE_MARGIN

    if background:
        pad = 10 + outline_thickness
        draw.rectangle(
            (
                SAFE_MARGIN - pad,
                y - pad,
                img.width - SAFE_MARGIN + pad,
                y + block_height + pad,
            ),
            fill=(0, 0, 0, 160),
        )

    for line in lines:
        width = draw.textlength(line, font=font)
        x = (img.width - width) // 2

        if outline_thickness > 0:
            for dx in range(-outline_thickness, outline_thickness + 1):
                for dy in range(-outline_thickness, outline_thickness + 1):
                    draw.text((x + dx, y + dy), line, font=font, fill="black")

        draw.text((x, y), line, font=font, fill="white")
        y += line_height


def build_caption_overlay(
    size: tuple[int, int],
    text: str,
    font_path: Path,
    font_size: int,
    position: str,
    outline: int,
    background: bool,
) -> Image.Image:
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw_caption(overlay, text, font_path, font_size, position, outline, background)
    return overlay


def caption_animation(
    input_path: Path,
    output_stem: Path,
    format_mode: str,
    top_text: str | None,
    bottom_text: str | None,
    font_path: Path,
    font_size: int,
    outline: int,
    background: bool,
) -> tuple[Path, int, str]:
    reader = imageio.get_reader(str(input_path))
    frames: list[Image.Image] = []
    transparency_found = False
    overlay_cache: dict[tuple[int, int], tuple[Image.Image | None, Image.Image | None]] = {}

    try:
        for frame in reader:
            if len(frames) >= MAX_FRAMES:
                raise ValueError(f"Animation has too many frames (max {MAX_FRAMES}).")

            img = Image.fromarray(frame).convert("RGBA")
            if img.width * img.height > MAX_PIXELS_PER_FRAME:
                raise ValueError("Animation frames are too large to process safely.")

            if has_transparency(img):
                transparency_found = True

            size_key = (img.width, img.height)
            if size_key not in overlay_cache:
                top_overlay = (
                    build_caption_overlay(img.size, top_text, font_path, font_size, "top", outline, background)
                    if top_text
                    else None
                )
                bottom_overlay = (
                    build_caption_overlay(img.size, bottom_text, font_path, font_size, "bottom", outline, background)
                    if bottom_text
                    else None
                )
                overlay_cache[size_key] = (top_overlay, bottom_overlay)

            top_overlay, bottom_overlay = overlay_cache[size_key]
            if top_overlay:
                img.alpha_composite(top_overlay)
            if bottom_overlay:
                img.alpha_composite(bottom_overlay)

            frames.append(img)

        if not frames:
            raise ValueError("No frames were found in the animation.")

        meta = reader.get_meta_data()
    finally:
        reader.close()

    durations = meta.get("durations")
    if not durations:
        durations = [meta.get("duration", 0.08)] * len(frames)

    if isinstance(durations, (int, float)):
        durations = [float(durations)] * len(frames)

    durations = [float(duration) for duration in durations]
    if len(durations) < len(frames):
        fill = durations[-1] if durations else 0.08
        durations += [fill] * (len(frames) - len(durations))
    durations = durations[: len(frames)]

    if format_mode == "auto":
        format_mode = "apng" if transparency_found else "gif"

    output_ext = ".gif" if format_mode == "gif" else ".png"
    output_path = output_stem.with_suffix(output_ext)

    if format_mode == "gif":
        imageio.mimsave(
            str(output_path),
            frames,
            format="GIF",
            duration=durations,
            loop=0,
        )
    else:
        frames[0].save(
            str(output_path),
            save_all=True,
            append_images=frames[1:],
            duration=[max(1, int(duration * 1000)) for duration in durations],
            loop=0,
            disposal=2,
            optimize=False,
        )

    return output_path, len(frames), format_mode


# ---------------- DISCORD ----------------
@bot.event
async def on_ready() -> None:
    global _has_synced

    if _has_synced:
        return

    dev_guild = discord.Object(id=GUILD_ID)
    bot.tree.copy_global_to(guild=dev_guild)
    await bot.tree.sync(guild=dev_guild)

    if SYNC_GLOBAL_COMMANDS:
        await bot.tree.sync()

    _has_synced = True
    print("Dev guild commands synced.")


@bot.tree.command(
    name="captiongif",
    description="Caption a GIF/APNG using Neko's bot!",
)
@app_commands.describe(
    top_text="Top caption",
    bottom_text="Bottom caption",
    gif_url="GIF/APNG URL",
    gif_file="Upload GIF/APNG",
    output_format="Auto, GIF, or APNG",
    public="Show publicly?",
    font="Choose font",
    font_size="Font size",
    outline="Outline thickness",
    background="Background box?",
)
@app_commands.choices(
    font=FONT_CHOICES,
    outline=OUTLINE_CHOICES,
    output_format=FORMAT_CHOICES,
)
@app_commands.checks.cooldown(1, 8.0, key=lambda interaction: interaction.user.id)
async def captiongif(
    interaction: discord.Interaction,
    top_text: str | None = None,
    bottom_text: str | None = None,
    gif_url: str | None = None,
    gif_file: discord.Attachment | None = None,
    output_format: str = "auto",
    public: bool = True,
    font: str = "impact",
    font_size: app_commands.Range[int, 20, 96] = 48,
    outline: int = 3,
    background: bool = False,
) -> None:
    await interaction.response.defer(ephemeral=not public)
    top_text = (top_text or "").strip()
    bottom_text = (bottom_text or "").strip()

    if not gif_url and not gif_file:
        await interaction.followup.send("You forgot the animation, silly :3", ephemeral=True)
        return

    if not top_text and not bottom_text:
        await interaction.followup.send("Add at least one caption (top or bottom).", ephemeral=True)
        return

    if gif_file and gif_file.size and gif_file.size > MAX_INPUT_BYTES:
        await interaction.followup.send("That file is too large (max 20MB).", ephemeral=True)
        return

    font_path = FONT_MAP.get(font)
    if not font_path or not font_path.exists():
        await interaction.followup.send("Selected font is unavailable on the bot host.", ephemeral=True)
        return

    uid = str(uuid.uuid4())
    input_ext = _ext_from_url(gif_url) if gif_url else _ext_from_filename(gif_file.filename)
    input_path = TEMP_DIR / f"{uid}_in{input_ext}"
    output_stem = TEMP_DIR / f"{uid}_out"
    output_path: Path | None = None
    frame_count = 0
    used_format = output_format
    start = asyncio.get_running_loop().time()

    try:
        async with processing_semaphore:
            if gif_url:
                await asyncio.wait_for(
                    asyncio.to_thread(download_file, gif_url, input_path, MAX_INPUT_BYTES),
                    timeout=JOB_TIMEOUT_SECONDS,
                )
            else:
                await gif_file.save(str(input_path))

            output_path, frame_count, used_format = await asyncio.wait_for(
                asyncio.to_thread(
                    caption_animation,
                    input_path,
                    output_stem,
                    output_format,
                    top_text,
                    bottom_text,
                    font_path,
                    font_size,
                    outline,
                    background,
                ),
                timeout=JOB_TIMEOUT_SECONDS,
            )

        if output_path.stat().st_size > MAX_DISCORD_UPLOAD_BYTES:
            await interaction.followup.send(
                "Finished processing, but the result is too large to upload to Discord (max 25MB).",
                ephemeral=True,
            )
            return

        elapsed = asyncio.get_running_loop().time() - start

        await interaction.followup.send(
            content=f"Done: {frame_count} frames, {used_format.upper()} output, {elapsed:.1f}s.",
            file=discord.File(str(output_path)),
            ephemeral=not public,
        )
    except asyncio.TimeoutError:
        await interaction.followup.send(
            "Processing timed out. Try a shorter or smaller animation.",
            ephemeral=True,
        )
    except Exception as exc:
        await interaction.followup.send(f"I hit an error while processing that animation:\n`{exc}`", ephemeral=True)
    finally:
        for path in (input_path, output_path):
            if path and path.exists():
                try:
                    path.unlink()
                except OSError:
                    pass


@captiongif.error
async def captiongif_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
    if isinstance(error, app_commands.CommandOnCooldown):
        wait_time = max(1, int(error.retry_after))
        message = f"You're using this command quickly. Try again in about {wait_time}s."
    else:
        message = "Command check failed before processing. Please try again."

    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


bot.run(TOKEN)
