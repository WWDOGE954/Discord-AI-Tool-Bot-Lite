from __future__ import annotations

import discord
from discord import app_commands

import config
from views import LiteControlView

if config.TOOL_MODE == "mcp_like":
    from mods.mcp_like_mod import handle_tool
else:
    from mods.tool_router_mod import handle_tool


intents = discord.Intents.default()
intents.message_content = config.REPLY_ON_MENTION
intents.messages = True
intents.guilds = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


def _allowed_channel(channel_id: int | None) -> bool:
    if config.TARGET_CHANNEL_ID == 0:
        return True
    return channel_id == config.TARGET_CHANNEL_ID


async def _send_tool_result(interaction: discord.Interaction, result, private: bool = True):
    content = result.message[:1900] if result.message else "Done."
    if interaction.response.is_done():
        await interaction.followup.send(content, ephemeral=private)
    else:
        await interaction.response.send_message(content, ephemeral=private)


@client.event
async def on_ready():
    if config.GUILD_ID:
        guild = discord.Object(id=config.GUILD_ID)
        tree.copy_global_to(guild=guild)
        await tree.sync(guild=guild)
        print(f"✅ Synced commands to guild {config.GUILD_ID}")
    else:
        await tree.sync()
        print("✅ Synced global commands")
    print(f"✅ Bot online: {client.user}")
    print(f"Tool mode: {config.TOOL_MODE}")
    print(f"AI provider: {config.AI_PROVIDER}")
    print(f"AI model: {config.AI_MODEL or 'not set'}")


@client.event
async def on_message(message: discord.Message):
    if message.author.bot or not config.REPLY_ON_MENTION:
        return
    if not _allowed_channel(getattr(message.channel, "id", None)):
        return
    if client.user is None or client.user not in message.mentions:
        return

    prompt = message.content
    prompt = prompt.replace(f"<@{client.user.id}>", "").replace(f"<@!{client.user.id}>", "").strip()
    if not prompt:
        await message.channel.send("請在標記我時附上想問的內容。")
        return

    thinking = await message.channel.send("🤖 Thinking...")
    result = await handle_tool(
        "ask_ai",
        prompt=prompt,
        user_id=str(message.author.id),
        display_name=message.author.display_name,
    )
    await thinking.edit(content=result.message[:1900])


@tree.command(name="ai", description="Chat with the configured AI model.")
@app_commands.describe(prompt="What do you want to ask?", private="Only show the reply to you")
async def ai_command(interaction: discord.Interaction, prompt: str, private: bool = True):
    if not _allowed_channel(getattr(interaction.channel, "id", None)):
        await interaction.response.send_message("This bot is not enabled in this channel.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=private, thinking=True)
    result = await handle_tool(
        "ask_ai",
        prompt=prompt,
        user_id=str(interaction.user.id),
        display_name=interaction.user.display_name,
    )
    await interaction.followup.send(result.message[:1900], ephemeral=private)


@tree.command(name="forget", description="Clear your temporary AI memory.")
async def forget_command(interaction: discord.Interaction):
    result = await handle_tool("forget", user_id=str(interaction.user.id))
    await _send_tool_result(interaction, result, private=True)


@tree.command(name="status", description="Show bot status and current architecture mode.")
async def status_command(interaction: discord.Interaction):
    result = await handle_tool("status")
    view = LiteControlView(handle_tool, user_id=str(interaction.user.id))
    await interaction.response.send_message(result.message[:1900], view=view, ephemeral=True)


@tree.command(name="usage", description="Show your token usage summary.")
async def usage_command(interaction: discord.Interaction):
    result = await handle_tool("usage", user_id=str(interaction.user.id))
    await _send_tool_result(interaction, result, private=True)


@tree.command(name="privacy", description="Show the cloud API privacy notice.")
async def privacy_command(interaction: discord.Interaction):
    result = await handle_tool("privacy")
    await _send_tool_result(interaction, result, private=True)


if __name__ == "__main__":
    if not config.DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN is not set. Create a .env file from .env.example.")
    client.run(config.DISCORD_TOKEN)
