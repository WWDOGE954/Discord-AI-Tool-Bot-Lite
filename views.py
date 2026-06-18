from __future__ import annotations

from typing import Callable, Awaitable
import discord

from mods.common import ToolResult

HandleTool = Callable[..., Awaitable[ToolResult]]


class LiteControlView(discord.ui.View):
    def __init__(self, handle_tool: HandleTool, user_id: str, timeout: float = 120):
        super().__init__(timeout=timeout)
        self.handle_tool = handle_tool
        self.user_id = user_id

    @discord.ui.button(label="Privacy", style=discord.ButtonStyle.secondary)
    async def privacy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = await self.handle_tool("privacy")
        await interaction.response.send_message(result.message[:1900], ephemeral=True)

    @discord.ui.button(label="My Usage", style=discord.ButtonStyle.secondary)
    async def usage_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        result = await self.handle_tool("usage", user_id=str(interaction.user.id))
        await interaction.response.send_message(result.message[:1900], ephemeral=True)
