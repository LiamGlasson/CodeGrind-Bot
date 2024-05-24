from typing import TYPE_CHECKING

import discord

from ui.modals.users import RegisterModal
from utils.preferences import update_user_preferences_prompt

if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot


class LoginView(discord.ui.View):
    def __init__(self, bot: "DiscordBot", *, timeout=180) -> None:
        self.bot = bot
        super().__init__(timeout=timeout)

    @discord.ui.button(label="Connect", style=discord.ButtonStyle.blurple)
    async def connect(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ) -> None:
        await interaction.response.send_modal(RegisterModal(self.bot))
        await update_user_preferences_prompt(interaction)
