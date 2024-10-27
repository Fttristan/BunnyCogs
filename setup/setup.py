from redbot.core import commands, Config
import discord

class Setup2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {
            "gban_enabled": False,
            "autocheck_channel": None,
            "autoban_enabled": False,
        }
        self.config.register_guild(**default_guild)

    @commands.guild_only()
    @commands.admin_or_permissions(administrator=True)
    @commands.command()
    async def setup(self, ctx):
        await ctx.send("setup cog is broken")
