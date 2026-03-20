from __future__ import annotations

import os
import random
from io import BytesIO
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DISCORD_TOKEN = (os.getenv("DISCORD_TOKEN") or "").strip()
if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN is required")

GUILD_ID_RAW = (os.getenv("GUILD_ID") or "").strip()
GUILD_ID = int(GUILD_ID_RAW) if GUILD_ID_RAW else None

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=20)
DEFAULT_HEADERS = {
    "User-Agent": "neko-catgirl-bot/1.0 (+https://github.com/nekolessi/discord-apps)"
}

NEKOS_BEST_IMAGE_URL = "https://nekos.best/api/v2/neko"
NEKOS_BEST_GIF_URL = "https://nekos.best/api/v2/nya"
NEKOS_API_NSFW_URL = "https://api.nekosapi.com/v4/images/random"
DANBOORU_POSTS_URL = "https://danbooru.donmai.us/posts.json"
MAX_DISCORD_VIDEO_BYTES = 10 * 1024 * 1024
RECENT_NSFW_ANIMATED_IDS: deque[int] = deque(maxlen=12)
RECENT_ASSET_URLS: dict[str, deque[str]] = {
    "sfw_image": deque(maxlen=12),
    "sfw_animated": deque(maxlen=12),
    "nsfw_image": deque(maxlen=12),
    "nsfw_animated": deque(maxlen=12),
}


@dataclass(slots=True)
class NekoAsset:
    post_id: Optional[int]
    title: str
    url: str
    preview_url: Optional[str]
    source_url: Optional[str]
    artist_name: Optional[str]
    artist_url: Optional[str]
    provider: str
    kind: str
    note: Optional[str]
    is_nsfw: bool
    attachment_name: Optional[str] = None


@dataclass(frozen=True, slots=True)
class NekoTheme:
    caption: str
    color: int
    footer: str


SFW_THEMES = [
    NekoTheme("Soft paws and cute meows. :3", 0x9FD8A8, "A cozy neko delivery for you"),
    NekoTheme("A little neko visit to brighten the chat.", 0xA7C7E7, "Served with extra sparkle"),
    NekoTheme(
        "Fresh catgirl energy, straight from the sunbeam.",
        0xF6B8C9,
        "Purring softly in the background",
    ),
    NekoTheme("One random catgirl, lovingly selected.", 0xF2A7A7, "Certified cozy neko moment"),
    NekoTheme("Cat ears up, vibes immaculate.", 0xC7B8EA, "Cute mode fully enabled"),
    NekoTheme("Tiny paws, warm heart, zero thoughts.", 0xF4C27A, "From the comfy neko corner"),
    NekoTheme("A sweet little neko came by to be admired.", 0xF7B7D2, "Soft and sparkly catgirl hours"),
    NekoTheme("Pretty paws, pretty eyes, pretty little mood.", 0xB8E1FF, "Girly neko delivery"),
    NekoTheme("A ribbon-coded catgirl moment just for you.", 0xF9C6D3, "Cute mode all the way up"),
    NekoTheme("Nya~ a darling catgirl has entered the room.", 0xD8C3F0, "Fresh from the pastel corner"),
    NekoTheme("Sweet, fluffy, and absolutely princess-coded.", 0xFFD6A5, "A tiny dose of catgirl glam"),
    NekoTheme("Just a cute neko being unfairly adorable again.", 0xAEE6B8, "Delivered with a little blush"),
    NekoTheme("Girly little paws and a face made for attention.", 0xFBCFE8, "Sparkles included"),
    NekoTheme("A soft neko drop for your daily dose of cute.", 0xCDEAC0, "Cozy catgirl pick of the moment"),
    NekoTheme("All dressed up in sweetness and cat ears.", 0xF4B6C2, "Pretty neko energy"),
    NekoTheme("A dreamy catgirl moment with extra charm.", 0xC7D2FE, "Floating in on soft vibes"),
    NekoTheme("Nya~ this one is cute enough to cause problems.", 0xFDE68A, "A little trouble, a lot of cute"),
    NekoTheme("Soft blush, tiny paws, and a very girly vibe.", 0xF9A8D4, "Cutie picked just for this chat"),
]

NSFW_THEMES = [
    NekoTheme(
        "Late-night catgirl delivery, dressed to misbehave.",
        0xE38BA8,
        "NSFW neko drop",
    ),
    NekoTheme("Velvet paws, bedroom eyes, and trouble on purpose.", 0xD16BA5, "For NSFW channels only"),
    NekoTheme("A needy little neko slipped into the after-hours feed.", 0xC06C84, "Handle with care"),
    NekoTheme("After-dark catgirl energy with a shameless little tease.", 0xB565A7, "Restricted to the spicy corner"),
    NekoTheme("A spoiled little neko showed up looking hungry for attention.", 0xE879F9, "Keep it in the naughty corner"),
    NekoTheme("Cat ears up, morals down, and acting bratty about it.", 0xDB2777, "Lewd neko hours"),
    NekoTheme("A clingy little catgirl is begging to be stared at.", 0xC026D3, "After-dark delivery"),
    NekoTheme("Bedroom eyes, needy paws, and not a shred of shame.", 0xBE185D, "Strictly NSFW"),
    NekoTheme("A slutty little neko came over to be admired properly.", 0xF472B6, "For the late-night timeline"),
    NekoTheme("Silky thighs, smug eyes, and a very bad influence.", 0xEC4899, "Too spicy for daylight"),
    NekoTheme("A teasing catgirl slipped in just to ruin your focus.", 0xD946EF, "Naughty neko drop"),
    NekoTheme("That look says she knows exactly what she is doing.", 0xFB7185, "Handle with both hands"),
    NekoTheme("Sweet little paws, filthy little intentions.", 0xE11D48, "For after-hours only"),
    NekoTheme("A shameless neko is putting on quite a show tonight.", 0xA21CAF, "Keep this one in NSFW"),
    NekoTheme("Pretty face, dirty thoughts, and trouble in lace.", 0xF43F5E, "Late-night catgirl service"),
    NekoTheme("A bratty catgirl is feeling extra lewd tonight.", 0xD946EF, "Spicy little neko energy"),
]


class NekoBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.http_session: Optional[aiohttp.ClientSession] = None

    async def setup_hook(self) -> None:
        self.http_session = aiohttp.ClientSession(
            timeout=REQUEST_TIMEOUT,
            headers=DEFAULT_HEADERS,
        )
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            print(f"[sync] Synced {len(synced)} command(s) to guild {GUILD_ID}")
        else:
            synced = await self.tree.sync()
            print(f"[sync] Synced {len(synced)} global command(s)")

    async def close(self) -> None:
        if self.http_session and not self.http_session.closed:
            await self.http_session.close()
        await super().close()


bot = NekoBot()


def _first_result(payload: Any) -> dict[str, Any]:
    if isinstance(payload, list):
        if payload and isinstance(payload[0], dict):
            return payload[0]
        raise RuntimeError("API returned an empty list")

    if isinstance(payload, dict):
        results = payload.get("results")
        if isinstance(results, list) and results and isinstance(results[0], dict):
            return results[0]

        items = payload.get("items")
        if isinstance(items, list) and items and isinstance(items[0], dict):
            return items[0]

        value = payload.get("value")
        if isinstance(value, list) and value and isinstance(value[0], dict):
            return value[0]

    raise RuntimeError("API response did not contain media")


def _pick_non_recent_item(
    items: list[dict[str, Any]],
    *,
    history_key: str,
    url_getter: callable,
) -> dict[str, Any]:
    recent_urls = RECENT_ASSET_URLS[history_key]
    fresh_items = [item for item in items if str(url_getter(item)) not in recent_urls]
    return random.choice(fresh_items or items)


def _remember_asset_url(history_key: str, url: str) -> None:
    RECENT_ASSET_URLS[history_key].append(url)


async def _fetch_json(url: str, *, params: Optional[dict[str, str]] = None) -> Any:
    if bot.http_session is None:
        raise RuntimeError("HTTP session is not ready")

    async with bot.http_session.get(url, params=params) as response:
        if response.status != 200:
            detail = await response.text()
            raise RuntimeError(
                f"API request failed with status {response.status}: {detail[:200]}"
            )
        return await response.json()


async def fetch_sfw_catgirl(media: str) -> NekoAsset:
    chosen_media = media
    if chosen_media == "any":
        chosen_media = random.choice(["image", "gif"])

    if chosen_media == "gif":
        item = None
        for _ in range(5):
            payload = await _fetch_json(NEKOS_BEST_GIF_URL)
            candidate = _first_result(payload)
            if candidate["url"] not in RECENT_ASSET_URLS["sfw_animated"]:
                item = candidate
                break
            item = candidate
        _remember_asset_url("sfw_animated", item["url"])
        return NekoAsset(
            post_id=None,
            title="SFW Neko GIF",
            url=item["url"],
            preview_url=item["url"],
            source_url=item.get("source_url"),
            artist_name=item.get("artist_name"),
            artist_url=item.get("artist_href"),
            provider="nekos.best",
            kind="gif",
            note=None,
            is_nsfw=False,
            attachment_name=None,
        )

    item = None
    for _ in range(5):
        payload = await _fetch_json(NEKOS_BEST_IMAGE_URL)
        candidate = _first_result(payload)
        if candidate["url"] not in RECENT_ASSET_URLS["sfw_image"]:
            item = candidate
            break
        item = candidate
    _remember_asset_url("sfw_image", item["url"])
    return NekoAsset(
        post_id=None,
        title="SFW Catgirl",
        url=item["url"],
        preview_url=item["url"],
        source_url=item.get("source_url"),
        artist_name=item.get("artist_name"),
        artist_url=item.get("artist_href"),
        provider="nekos.best",
        kind="image",
        note=None,
        is_nsfw=False,
        attachment_name=None,
    )


async def fetch_nsfw_catgirl(media: str) -> NekoAsset:
    chosen_media = media
    if chosen_media == "any":
        chosen_media = random.choice(["image", "gif"])

    if chosen_media == "gif":
        payload = await _fetch_json(
            DANBOORU_POSTS_URL,
            params={"limit": "20", "tags": "cat_girl animated rating:explicit"},
        )
        if not isinstance(payload, list):
            raise RuntimeError("Danbooru did not return a post list")

        candidates = [
            post
            for post in payload
            if isinstance(post, dict)
            and post.get("file_url")
            and str(post.get("file_ext", "")).lower() in {"gif", "mp4", "webm"}
        ]
        if not candidates:
            raise RuntimeError("Danbooru did not return an animated NSFW catgirl post")

        non_recent_candidates = [
            post
            for post in candidates
            if int(post.get("id") or 0) not in RECENT_NSFW_ANIMATED_IDS
            and str(post.get("file_url") or "") not in RECENT_ASSET_URLS["nsfw_animated"]
        ]
        if non_recent_candidates:
            candidates = non_recent_candidates

        attachable_candidates = [
            post
            for post in candidates
            if int(post.get("file_size") or 0) > 0
            and int(post.get("file_size") or 0) <= MAX_DISCORD_VIDEO_BYTES
        ]
        if attachable_candidates:
            candidates = attachable_candidates

        item = random.choice(candidates)
        artist_tag = str(item.get("tag_string_artist", "")).strip()
        artist_name = artist_tag.replace("_", " ") if artist_tag else None
        source_url = str(item.get("source") or "").strip() or f"https://danbooru.donmai.us/posts/{item['id']}"
        preview_url = str(item.get("preview_file_url") or item.get("large_file_url") or item.get("file_url"))
        file_ext = str(item.get("file_ext", "video")).lower()
        file_url = str(item["file_url"])
        note = "animated post from Danbooru"
        if not attachable_candidates:
            note = "animated Danbooru post; direct video link used because the file is too large to upload"

        post_id = int(item["id"])
        RECENT_NSFW_ANIMATED_IDS.append(post_id)
        _remember_asset_url("nsfw_animated", file_url)

        return NekoAsset(
            post_id=post_id,
            title="NSFW Animated Catgirl",
            url=file_url,
            preview_url=preview_url,
            source_url=source_url,
            artist_name=artist_name,
            artist_url=None,
            provider="Danbooru",
            kind=file_ext,
            note=note,
            is_nsfw=True,
            attachment_name=f"nsfw-catgirl-{item['id']}.{file_ext}",
        )

    payload = await _fetch_json(
        NEKOS_API_NSFW_URL,
        params={"tags": "catgirl", "rating": "explicit", "limit": "20"},
    )
    items = payload.get("value") if isinstance(payload, dict) else payload
    if not isinstance(items, list) or not items:
        raise RuntimeError("NSFW image source did not return any catgirls")
    item = _pick_non_recent_item(
        [candidate for candidate in items if isinstance(candidate, dict) and candidate.get("url")],
        history_key="nsfw_image",
        url_getter=lambda candidate: candidate["url"],
    )
    _remember_asset_url("nsfw_image", item["url"])

    return NekoAsset(
        post_id=None,
        title="NSFW Catgirl",
        url=item["url"],
        preview_url=item["url"],
        source_url=item.get("source_url"),
        artist_name=item.get("artist_name"),
        artist_url=None,
        provider="nekosapi.com",
        kind="image",
        note=None,
        is_nsfw=True,
        attachment_name=None,
    )


def pick_theme(*, is_nsfw: bool) -> NekoTheme:
    return random.choice(NSFW_THEMES if is_nsfw else SFW_THEMES)


def channel_is_nsfw(
    channel: Optional[
        discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel
    ]
) -> bool:
    if channel is None:
        return False

    if isinstance(channel, discord.Thread):
        parent = channel.parent
        if parent is None:
            return False
        if hasattr(parent, "is_nsfw"):
            return bool(parent.is_nsfw())
        return bool(getattr(parent, "nsfw", False))

    if isinstance(channel, discord.DMChannel):
        return False

    if hasattr(channel, "is_nsfw"):
        return bool(channel.is_nsfw())

    return bool(getattr(channel, "nsfw", False))


def build_embed(
    asset: NekoAsset,
    *,
    requested_by: discord.abc.User,
    include_image: bool = True,
) -> discord.Embed:
    theme = pick_theme(is_nsfw=asset.is_nsfw)
    embed = discord.Embed(description=theme.caption, color=theme.color)
    if include_image:
        embed.set_image(url=asset.preview_url or asset.url)

    credit_bits: list[str] = []
    if asset.artist_name:
        if asset.artist_url:
            credit_bits.append(f"art by [{asset.artist_name}]({asset.artist_url})")
        else:
            credit_bits.append(f"art by {asset.artist_name}")
    if asset.source_url:
        credit_bits.append(f"[source]({asset.source_url})")
    if asset.note:
        credit_bits.append(asset.note)

    if credit_bits:
        embed.description = f"{theme.caption}\n\n*{' | '.join(credit_bits)}*"

    try:
        embed.set_footer(
            text=f"Requested by {requested_by.display_name}",
            icon_url=requested_by.display_avatar.url,
        )
    except Exception:
        embed.set_footer(
            text=f"Requested by {getattr(requested_by, 'display_name', 'someone')}"
        )
    return embed


def build_tiny_caption(asset: NekoAsset) -> Optional[str]:
    bits: list[str] = []
    if asset.artist_name:
        bits.append(f"art by {asset.artist_name}")
    if asset.source_url:
        bits.append(f"source: <{asset.source_url}>")
    if not bits:
        return None
    return " | ".join(bits)


async def download_attachment(url: str, filename: str) -> discord.File:
    if bot.http_session is None:
        raise RuntimeError("HTTP session is not ready")

    async with bot.http_session.get(url) as response:
        if response.status != 200:
            detail = await response.text()
            raise RuntimeError(
                f"Video download failed with status {response.status}: {detail[:200]}"
            )
        data = await response.read()

    return discord.File(BytesIO(data), filename=filename)


async def send_asset_response(
    interaction: discord.Interaction,
    *,
    asset: NekoAsset,
) -> None:
    if asset.kind in {"mp4", "webm"}:
        if asset.attachment_name:
            try:
                file = await download_attachment(asset.url, asset.attachment_name)
                if asset.is_nsfw:
                    tiny_caption = build_tiny_caption(asset)
                    await interaction.followup.send(
                        content=tiny_caption if tiny_caption else None,
                        file=file,
                    )
                    return

                embed = build_embed(asset, requested_by=interaction.user, include_image=False)
                await interaction.followup.send(embed=embed, file=file)
                return
            except Exception:
                pass

        if asset.is_nsfw:
            tiny_caption = build_tiny_caption(asset)
            if tiny_caption:
                await interaction.followup.send(content=f"{tiny_caption}\n{asset.url}")
            else:
                await interaction.followup.send(content=asset.url)
            return

        embed = build_embed(asset, requested_by=interaction.user)
        await interaction.followup.send(content=asset.url, embed=embed)
        return

    embed = build_embed(asset, requested_by=interaction.user)
    await interaction.followup.send(embed=embed)


MEDIA_CHOICES = [
    app_commands.Choice(name="Any", value="any"),
    app_commands.Choice(name="Image", value="image"),
    app_commands.Choice(name="Animated", value="gif"),
]

neko_group = app_commands.Group(name="neko", description="Fetch random catgirl media")


@app_commands.describe(media="Whether you want an image, a gif, or either")
@app_commands.choices(media=MEDIA_CHOICES)
@neko_group.command(name="catgirl", description="Fetch a random SFW catgirl image or gif")
async def neko_catgirl(
    interaction: discord.Interaction,
    media: Optional[app_commands.Choice[str]] = None,
) -> None:
    await interaction.response.defer(thinking=True)
    selected_media = media.value if media else "any"

    try:
        asset = await fetch_sfw_catgirl(selected_media)
    except Exception as error:
        await interaction.followup.send(
            f"Could not fetch a SFW catgirl right now: {error}",
            ephemeral=True,
        )
        return

    await send_asset_response(interaction, asset=asset)


@app_commands.describe(media="Whether you want an image, a gif, or either")
@app_commands.choices(media=MEDIA_CHOICES)
@neko_group.command(name="nsfwcatgirl", description="Fetch a random NSFW catgirl image or animated post")
async def neko_nsfw_catgirl(
    interaction: discord.Interaction,
    media: Optional[app_commands.Choice[str]] = None,
) -> None:
    if interaction.guild is None:
        await interaction.response.send_message(
            "NSFW catgirl content is only available inside a server NSFW channel.",
            ephemeral=True,
        )
        return

    if not channel_is_nsfw(interaction.channel):
        await interaction.response.send_message(
            "Use this command in a channel marked NSFW.",
            ephemeral=True,
        )
        return

    await interaction.response.defer(thinking=True)
    selected_media = media.value if media else "any"

    try:
        asset = await fetch_nsfw_catgirl(selected_media)
    except Exception as error:
        await interaction.followup.send(
            f"Could not fetch an NSFW catgirl right now: {error}",
            ephemeral=True,
        )
        return

    await send_asset_response(interaction, asset=asset)


@bot.tree.command(name="sync", description="Resync slash commands for this bot")
@app_commands.default_permissions(administrator=True)
async def sync_slash(interaction: discord.Interaction) -> None:
    await interaction.response.defer(thinking=True, ephemeral=True)

    try:
        global_synced = await bot.tree.sync()
        results = [f"Global sync complete: {len(global_synced)} command(s)."]

        if interaction.guild is not None:
            bot.tree.copy_global_to(guild=interaction.guild)
            guild_synced = await bot.tree.sync(guild=interaction.guild)
            results.append(
                f"Guild sync complete for {interaction.guild.name}: {len(guild_synced)} command(s)."
            )

        await interaction.followup.send("\n".join(results), ephemeral=True)
    except Exception as error:
        await interaction.followup.send(f"Sync failed: {error}", ephemeral=True)


@bot.event
async def on_ready() -> None:
    user_tag = str(bot.user) if bot.user else "unknown"
    print(f"[ready] Logged in as {user_tag}")


@bot.tree.error
async def on_tree_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError,
) -> None:
    print(f"[command-error] {error}")
    message = "Command failed. Please try again in a moment."
    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


bot.tree.add_command(neko_group)


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
