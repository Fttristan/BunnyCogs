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
        await ctx.send("Do you want to enable gban in your server? (yes/no)")
        try:
            msg = await self.bot.wait_for(
                "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=60
            )
        except asyncio.TimeoutError:
            return await ctx.send("Setup timed out. Please try again.")

        if msg.content.lower() == "yes":
            await ctx.send("Enabling gban service...")
            await ctx.invoke(self.bot.get_command("bancheckset service enable antiraid"))
        else:
            return await ctx.send("Setup aborted.")

        await ctx.send("Which channel do you want for auto-check notifications? Please mention the channel.")
        try:
            msg = await self.bot.wait_for(
                "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel and m.channel_mentions, timeout=60
            )
        except asyncio.TimeoutError:
            return await ctx.send("Setup timed out. Please try again.")

        channel = msg.channel_mentions[0]
        await ctx.send(f"Setting auto-check notifications to {channel.mention}...")
        await ctx.invoke(self.bot.get_command(f"bancheckset autocheck set {channel.id}"))

        await ctx.send("Do you want to automatically ban users on the ban list when they join? (yes/no)")
        try:
            msg = await self.bot.wait_for(
                "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=60
            )
        except asyncio.TimeoutError:
            return await ctx.send("Setup timed out. Please try again.")

        if msg.content.lower() == "yes":
            await ctx.send("Enabling automatic bans for users on the ban list...")
            await ctx.invoke(self.bot.get_command("bancheckset autoban enable antiraid"))
        else:
            await ctx.send("Automatic bans not enabled.")

        await ctx.send("Ban check setup completed!")

def setup(bot):
    bot.add_cog(BanCheckSetup(bot))
