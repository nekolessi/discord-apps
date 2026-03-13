import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("anonymous-comment-bot")


@dataclass(frozen=True)
class Settings:
    discord_token: str
    comments_channel_id: int
    case_store_path: Path
    guild_id: int | None


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _optional_int_env(name: str) -> int | None:
    value = os.getenv(name, "").strip()
    if not value:
        return None
    return int(value)


def load_settings() -> Settings:
    comments_channel = os.getenv("COMMENTS_CHANNEL_ID", "").strip()
    legacy_feedback_channel = os.getenv("FEEDBACK_CHANNEL_ID", "").strip()
    if not comments_channel and not legacy_feedback_channel:
        raise RuntimeError("Missing required environment variable: COMMENTS_CHANNEL_ID")

    return Settings(
        discord_token=_require_env("DISCORD_TOKEN"),
        comments_channel_id=int(comments_channel or legacy_feedback_channel),
        case_store_path=Path(os.getenv("CASE_STORE_PATH", "./data/comment-cases.json")),
        guild_id=_optional_int_env("GUILD_ID"),
    )


SETTINGS = load_settings()
CASE_ID_PREFIX = "MEOW"
CASE_TAG_EMOJI = os.getenv("CASE_TAG_EMOJI", "\N{PAW PRINTS}")


def _extract_case_number(case_id: str) -> int | None:
    raw = case_id.strip()
    if raw.isdigit():
        return int(raw)

    upper = raw.upper()
    prefixed = f"{CASE_ID_PREFIX}-"
    if upper.startswith(prefixed):
        suffix = upper[len(prefixed) :]
        if suffix.isdigit():
            return int(suffix)

    return None


def _format_case_id(case_number: int) -> str:
    return f"{CASE_ID_PREFIX}-{case_number:04d}"


def normalize_case_id(case_id: str) -> str:
    case_number = _extract_case_number(case_id)
    if case_number is not None:
        return _format_case_id(case_number)
    return case_id.strip().upper()


class CaseStore:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self._lock = asyncio.Lock()

    async def create_case(self, user_id: int, guild_id: int) -> dict[str, Any]:
        async with self._lock:
            payload = self._read_payload()
            case_id = self._build_next_case_id(payload["cases"])
            record = {
                "case_id": case_id,
                "user_id": str(user_id),
                "guild_id": str(guild_id),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            payload["cases"].append(record)
            self._write_payload(payload)
            return record

    async def get_case(self, case_id: str) -> dict[str, Any] | None:
        normalized = normalize_case_id(case_id)
        async with self._lock:
            payload = self._read_payload()
            return next((entry for entry in payload["cases"] if entry["case_id"] == normalized), None)

    async def set_comment_message_id(self, case_id: str, message_id: int) -> None:
        normalized = normalize_case_id(case_id)
        async with self._lock:
            payload = self._read_payload()
            for entry in payload["cases"]:
                if entry["case_id"] == normalized:
                    entry["comment_message_id"] = str(message_id)
                    self._write_payload(payload)
                    return

    async def delete_case(self, case_id: str) -> None:
        normalized = normalize_case_id(case_id)
        async with self._lock:
            payload = self._read_payload()
            original_len = len(payload["cases"])
            payload["cases"] = [entry for entry in payload["cases"] if entry["case_id"] != normalized]
            if len(payload["cases"]) != original_len:
                self._write_payload(payload)

    def _read_payload(self) -> dict[str, list[dict[str, Any]]]:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            initial = {"cases": []}
            self.file_path.write_text(json.dumps(initial, indent=2) + "\n", encoding="utf-8")
            return initial

        raw = self.file_path.read_text(encoding="utf-8").strip()
        if not raw:
            return {"cases": []}

        parsed = json.loads(raw)
        if not isinstance(parsed, dict) or not isinstance(parsed.get("cases"), list):
            raise RuntimeError(f"Malformed case store at {self.file_path}")

        # Normalize legacy numeric IDs (e.g. 0001) to current prefixed format.
        for entry in parsed["cases"]:
            if not isinstance(entry, dict):
                continue
            case_number = _extract_case_number(str(entry.get("case_id", "")))
            if case_number is not None:
                entry["case_id"] = _format_case_id(case_number)

        return {"cases": parsed["cases"]}

    def _write_payload(self, payload: dict[str, list[dict[str, Any]]]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    @staticmethod
    def _build_next_case_id(existing_cases: list[dict[str, Any]]) -> str:
        max_seen = 0
        for case in existing_cases:
            case_number = _extract_case_number(str(case.get("case_id", "")))
            if case_number is not None:
                max_seen = max(max_seen, case_number)

        return _format_case_id(max_seen + 1)


case_store = CaseStore(SETTINGS.case_store_path)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree
_did_initial_sync = False


class CommentModal(discord.ui.Modal, title="Anonymous Comment"):
    comment = discord.ui.TextInput(
        label="Comment",
        style=discord.TextStyle.paragraph,
        placeholder="Type your anonymous comment",
        max_length=1000,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if interaction.guild_id is None:
            await interaction.response.send_message(
                "Anonymous comments can only be submitted inside a server.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True, thinking=True)
        comments_channel = interaction.client.get_channel(SETTINGS.comments_channel_id)
        if not isinstance(comments_channel, discord.TextChannel):
            try:
                fetched = await interaction.client.fetch_channel(SETTINGS.comments_channel_id)
            except discord.HTTPException as exc:
                logger.exception("Failed to fetch comments channel: %s", exc)
                await interaction.followup.send(
                    "Comments channel is not configured correctly. Please contact moderators.",
                    ephemeral=True,
                )
                return
            if not isinstance(fetched, discord.TextChannel):
                await interaction.followup.send(
                    "Comments channel is not configured as a text channel.",
                    ephemeral=True,
                )
                return
            comments_channel = fetched

        comment_text = str(self.comment).strip()
        if not comment_text:
            await interaction.followup.send("Comment cannot be empty.", ephemeral=True)
            return

        record = await case_store.create_case(
            user_id=interaction.user.id,
            guild_id=interaction.guild_id,
        )

        public_message = f"{comment_text}\n\n{CASE_TAG_EMOJI} `{record['case_id']}`"

        try:
            if comments_channel.guild.id != interaction.guild_id:
                await interaction.followup.send(
                    "Comments channel is configured for a different server.",
                    ephemeral=True,
                )
                await case_store.delete_case(record["case_id"])
                return

            sent = await comments_channel.send(public_message, allowed_mentions=discord.AllowedMentions.none())
            await case_store.set_comment_message_id(record["case_id"], sent.id)
        except discord.HTTPException:
            await case_store.delete_case(record["case_id"])
            logger.exception("Failed posting anonymous comment case %s", record["case_id"])
            await interaction.followup.send(
                "Your comment could not be delivered right now. Please try again in a bit.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            f"Thanks. Your anonymous comment was submitted as case `{record['case_id']}`.",
            ephemeral=True,
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        logger.exception("Unhandled modal error: %s", error)
        if interaction.response.is_done():
            await interaction.followup.send("Something went wrong. Please try again.", ephemeral=True)
        else:
            await interaction.response.send_message(
                "Something went wrong. Please try again.",
                ephemeral=True,
            )


@tree.command(name="comment", description="Submit an anonymous comment")
async def comment(interaction: discord.Interaction) -> None:
    await interaction.response.send_modal(CommentModal())


@tree.command(name="reply", description="Reply privately to an anonymous comment case")
@app_commands.default_permissions(manage_messages=True)
@app_commands.describe(case_id="Case ID from the comments channel", message="Private reply message")
async def reply(interaction: discord.Interaction, case_id: str, message: str) -> None:
    if interaction.guild_id is None:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    if not interaction.permissions or not interaction.permissions.manage_messages:
        await interaction.response.send_message(
            "You need Manage Messages permission to use this command.",
            ephemeral=True,
        )
        return

    normalized_case_id = normalize_case_id(case_id)
    record = await case_store.get_case(normalized_case_id)
    if not record:
        await interaction.response.send_message(
            f"No comment case found for `{normalized_case_id}`.",
            ephemeral=True,
        )
        return

    if int(record["guild_id"]) != interaction.guild_id:
        await interaction.response.send_message(
            "That case belongs to a different server.",
            ephemeral=True,
        )
        return

    try:
        user = bot.get_user(int(record["user_id"])) or await bot.fetch_user(int(record["user_id"]))
        dm_content = (
            f"You received a moderator response for comment case **{record['case_id']}**.\n\n{message.strip()}"
        )
        await user.send(dm_content)
    except discord.Forbidden:
        await interaction.response.send_message(
            "Could not DM that user. They may have DMs disabled.",
            ephemeral=True,
        )
        return
    except discord.HTTPException:
        logger.exception("Failed to send reply DM for case %s", normalized_case_id)
        await interaction.response.send_message(
            "DM delivery failed due to a Discord API error. Please try again.",
            ephemeral=True,
        )
        return

    await interaction.response.send_message(
        f"Sent a private reply to case `{record['case_id']}`.",
        ephemeral=True,
    )


@tree.command(name="help", description="Show anonymous comment bot commands")
async def help_command(interaction: discord.Interaction) -> None:
    lines = [
        "**Available commands**",
        "- `/comment` - open anonymous comment form",
        "- `/reply case_id message` - moderator-only private reply",
        "- `/help` - show this message",
    ]
    await interaction.response.send_message("\n".join(lines), ephemeral=True)


@bot.event
async def on_ready() -> None:
    global _did_initial_sync

    if not _did_initial_sync:
        try:
            if SETTINGS.guild_id:
                guild_obj = discord.Object(id=SETTINGS.guild_id)
                tree.copy_global_to(guild=guild_obj)
                synced = await tree.sync(guild=guild_obj)
                logger.info("Synced %s command(s) to guild %s", len(synced), SETTINGS.guild_id)
            else:
                synced = await tree.sync()
                logger.info("Synced %s global command(s)", len(synced))
            _did_initial_sync = True
        except Exception:
            logger.exception("Command sync failed")

    if bot.user:
        logger.info("Logged in as %s (%s)", bot.user, bot.user.id)


def main() -> None:
    bot.run(SETTINGS.discord_token)


if __name__ == "__main__":
    main()
