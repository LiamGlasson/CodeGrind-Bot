import json
import os

import discord
from discord.ext import commands

from bot_globals import DIFFICULTY_SCORE, RANK_EMOJI, TIMEFRAME_TITLE, logger


class Pagination(discord.ui.View):
    def __init__(self, user_id, pages=None, page=0):
        super().__init__()
        self.page = page
        self.user_id = user_id

        if pages is None:
            self.pages = []
        else:
            self.pages = pages

        self.max_page = len(self.pages) - 1

        if self.page == 0:
            self.previous.style = discord.ButtonStyle.gray
            self.previous.disabled = True

        if self.page == self.max_page:
            self.next.style = discord.ButtonStyle.gray
            self.next.disabled = True

    @discord.ui.button(label='<', style=discord.ButtonStyle.blurple)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer()
            return

        if self.page - 1 >= 0:
            self.page -= 1
            await interaction.message.edit(embed=self.pages[self.page])

            if self.page == 0:
                button.style = discord.ButtonStyle.gray
                button.disabled = True

        # if self.page < self.max_page:
        self.next.style = discord.ButtonStyle.blurple
        self.next.disabled = False

        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='>', style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer()
            return

        if self.page + 1 <= self.max_page:
            self.page += 1
            await interaction.message.edit(embed=self.pages[self.page])

            if self.page == self.max_page:
                button.style = discord.ButtonStyle.gray
                button.disabled = True

        self.previous.style = discord.ButtonStyle.blurple
        self.previous.disabled = False

        await interaction.response.edit_message(view=self)
    
    @discord.ui.button(label='🗑️', style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer()
            return

        await interaction.message.delete()


async def create_leaderboard(interaction: discord.Interaction, timeframe: str = "alltime", page: int = 1):
    logger.info("file: cogs/leaderboards.py ~ create_leaderboard ~ run ~ guild id: %s", interaction.guild.id)

    users_per_page = 10

    if not os.path.exists(f"data/{interaction.guild.id}_leetcode_stats.json"):
        embed = discord.Embed(
            title=f"{TIMEFRAME_TITLE[timeframe]['title']} Leaderboard",
            description="No one has added their LeetCode username yet.",
            color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    with open(f"data/{interaction.guild.id}_leetcode_stats.json", "r", encoding="UTF-8") as file:
        data = json.load(file)

    last_updated = data["last_updated"]

    sorted_data = sorted(data["users"].items(),
                         key=lambda x: x[1][TIMEFRAME_TITLE[timeframe]['field']],
                         reverse=True)

    pages = []
    page_count = -(-len(sorted_data)//users_per_page)

    for i in range(page_count):
        leaderboard = []

        for j, (
            username,
            stats,
        ) in enumerate(sorted_data[i * users_per_page: i * users_per_page + users_per_page], start=i * users_per_page + 1):
            profile_link = f"https://leetcode.com/{username}"
            # Get the discord_username from the stats data in the JSON file
            discord_username = stats["discord_username"]
            # Get the link_yes_no from the stats data in the JSON file
            link_yes_no = stats["link_yes_no"] == "yes"

            if discord_username:
                number_rank = f"{j}\."
                discord_username_with_link = f"[{discord_username}]({profile_link})"
                if timeframe == "weekly":
                    weeklies_won = sum(
                        rank == 1 for rank in stats['weeklies_ranking'].values())
                    weeklies_won_text = f"    ({weeklies_won} weeklies won)"
                leaderboard.append(
                    f"**{RANK_EMOJI[j] if j in RANK_EMOJI else number_rank} {discord_username_with_link if link_yes_no else discord_username}**  {stats[TIMEFRAME_TITLE[timeframe]['field']]} points{weeklies_won_text if timeframe == 'weekly' and weeklies_won > 0 else ''}"
                )

        embed = discord.Embed(title=f"{TIMEFRAME_TITLE[timeframe]['title']} Leaderboard",
                              color=discord.Color.yellow())
        embed.description = "\n".join(leaderboard)
        # Score Methodology: Easy: 1, Medium: 3, Hard: 7
        embed.set_footer(
            text=f"Score Methodology: Easy: {DIFFICULTY_SCORE['easy']} point, Medium: {DIFFICULTY_SCORE['medium']} points, Hard: {DIFFICULTY_SCORE['hard']} points\nUpdated on {last_updated}\nPage {i + 1}/{page_count}")
        # Score Equation: Easy * 1 + Medium * 3 + Hard * 7 = Total Score
        pages.append(embed)

    page = page - 1 if page > 0 else 0
    await interaction.response.send_message(embed=pages[page], view=Pagination(interaction.user.id, pages, page))


class Leaderboards(commands.Cog):
    def __init__(self, client):
        self.client = client

    @discord.app_commands.command(name="leaderboard", description="View the All-Time leaderboard")
    async def leaderboard(self, interaction: discord.Interaction, timeframe: str = "alltime", page: int = 1):
        logger.info("file: cogs/leaderboards.py ~ leaderboard ~ run")

        timeframe = timeframe.lower()

        if timeframe not in TIMEFRAME_TITLE:
            await interaction.response.defer()
            return

        await create_leaderboard(interaction, timeframe, page)

    @discord.app_commands.command(name="weekly", description="View the Weekly leaderboard")
    async def weekly(self, interaction: discord.Interaction, page: int = 1):
        logger.info("file: cogs/leaderboards.py ~ weekly ~ run")
        
        await create_leaderboard(interaction, "weekly", page)


async def setup(client):
    await client.add_cog(Leaderboards(client))