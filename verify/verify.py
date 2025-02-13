import aiohttp
import discord
from redbot.core import commands, Config, checks
from redbot.core.bot import Red

class VerificationCog(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {
            "verification_role": None,
            "verification_channel": None,
            "data_channel": None
        }
        self.config.register_guild(**default_guild)
        self.config.register_global(api_key="")

    @commands.command()
    @checks.is_owner()
    async def setapikey(self, ctx: commands.Context, api_key: str):
        """Set the API key for the verification cog."""
        await self.config.api_key.set(api_key)
        await ctx.send("API key has been set.")

    @commands.command()
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    async def setverifrole(self, ctx: commands.Context, role: discord.Role):
        """Set the verification role for the guild."""
        await self.config.guild(ctx.guild).verification_role.set(role.id)
        await ctx.send(f"Verification role has been set to {role.name}.")

    @commands.command()
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    async def setverifchannel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the verification channel for the guild."""
        await self.config.guild(ctx.guild).verification_channel.set(channel.id)
        await ctx.send(f"Verification channel has been set to {channel.mention}.")

    @commands.command()
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    async def setdatachannel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the verification data channel for the guild."""
        await self.config.guild(ctx.guild).data_channel.set(channel.id)
        await ctx.send(f"Verification data channel has been set to {channel.mention}.")

    @commands.command()
    @commands.guild_only()
    async def verify(self, ctx: commands.Context):
        """Verify the user."""
        api_key = await self.config.api_key()
        user_id = ctx.author.id
        redbot_version = "3.5"
        user_agent = f"Red-DiscordBot/{redbot_version} BanCheck (https://github.com/PhasecoreX/PCXCogs)"

        async with aiohttp.ClientSession() as client_session:
            try:
                async with client_session.get(
                    f"https://verify.vrcband.com/api/v1/discord/cog/data/{api_key}/{user_id}",
                    headers={
                        "user-agent": user_agent,
                        "auth": "bunnybot2.0"
                    },
                ) as resp:
                    raw_data = await resp.json()  # Get raw response text
                    print(f"Raw response: {raw_data}")
                    try:
                        data = await resp.json()
                    except Exception as e:
                        print(f"Error parsing JSON: {e}")
                        await ctx.send(f"Verification failed. Error parsing JSON: {e}")
                        return
                    print(data)
                    if 'items' in data and len(data['items']) > 0:
                        if data['items'][0]['api_key'] == api_key:
                            if data['items'][0]['discord_id'] == str(user_id):
                                role_id = await self.config.guild(ctx.guild).verification_role()
                                role = ctx.guild.get_role(role_id)
                                if role:
                                    await ctx.author.add_roles(role)
                                    await ctx.send(f"Verification successful. {ctx.author.mention} has been given the {role.name} role.")
                                    # Send verification data
                                    data_channel_id = await self.config.guild(ctx.guild).data_channel()
                                    data_channel = ctx.guild.get_channel(data_channel_id)
                                    if data_channel:
                                        embed = discord.Embed(
                                            title="User Verified",
                                            description=f"User {ctx.author.mention} has been verified.",
                                            color=discord.Color.green()
                                        )
                                        embed.add_field(name="Discord User ID", value=ctx.author.id)
                                        embed.add_field(name="Discord User Name", value=str(ctx.author))
                                        embed.add_field(name="VRChat ID", value=data['items'][0]['vrchat_id'])
                                        await data_channel.send(embed=embed)
                                else:
                                    await ctx.send(f"{ctx.author.mention}, please verify yourself at https://verify.vrcband.com/api/v1/lantern/consent/{api_key}")
                            else:
                                await ctx.send(f"{ctx.author.mention}, please verify yourself at https://verify.vrcband.com/api/v1/lantern/consent/{api_key}")
                        else:
                            await ctx.send(f"{ctx.author.mention}, please verify yourself at https://verify.vrcband.com/api/v1/lantern/consent/{api_key}")
                    else:
                        await ctx.send(f"{ctx.author.mention}, please verify yourself at https://verify.vrcband.com/api/v1/lantern/consent/{api_key}")
            except aiohttp.ClientConnectionError:
                await ctx.send("Verification failed. Could not connect to host.")
            except aiohttp.ClientError as e:
                await ctx.send(f"Verification failed. Client error occurred: {e}")
            except TypeError as e:
                await ctx.send(f"Verification failed. Type error occurred: {e}")
            except KeyError as e:
                await ctx.send(f"Verification failed. Key error occurred: {e}")
            await ctx.send("Verification failed. Response data malformed.")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Verify user when they join the server."""
        guild = member.guild
        api_key = await self.config.api_key()
        user_id = member.id
        redbot_version = "3.5"
        user_agent = f"Red-DiscordBot/{redbot_version} BanCheck (https://github.com/PhasecoreX/PCXCogs)"
        verification_channel_id = await self.config.guild(guild).verification_channel()
        verification_channel = guild.get_channel(verification_channel_id)

        async with aiohttp.ClientSession() as client_session:
            try:
                async with client_session.get(
                    f"https://verify.vrcband.com/api/v1/discord/cog/data/{api_key}/{user_id}",
                    headers={
                        "user-agent": user_agent,
                        "auth": "bunnybot2.0"
                    },
                ) as resp:
                    raw_data = await resp.json()  # Get raw response text
                    print(f"Raw response: {raw_data}")
                    try:
                        data = await resp.json()
                    except Exception as e:
                        print(f"Error parsing JSON: {e}")
                        if verification_channel:
                            await verification_channel.send(f"Verification failed. Error parsing JSON: {e}")
                        return
                    print(data)
                    if 'items' in data and len(data['items']) > 0:
                        if data['items'][0]['api_key'] == api_key:
                            if data['items'][0]['discord_id'] == str(user_id):
                                role_id = await self.config.guild(guild).verification_role()
                                role = guild.get_role(role_id)
                                if role:
                                    await member.add_roles(role)
                                    if verification_channel:
                                        await verification_channel.send(f"Welcome {member.mention}! You have been automatically verified and given the {role.name} role.")
                                    # Send verification data
                                    data_channel_id = await self.config.guild(guild).data_channel()
                                    data_channel = guild.get_channel(data_channel_id)
                                    if data_channel:
                                        embed = discord.Embed(
                                            title="User Verified",
                                            description=f"User {member.mention} has been verified.",
                                            color=discord.Color.green()
                                        )
                                        embed.add_field(name="Discord User ID", value=member.id)
                                        embed.add_field(name="Discord User Name", value=str(member))
                                        embed.add_field(name="VRChat ID", value=data['items'][0]['vrchat_id'])
                                        await data_channel.send(embed=embed)
                                else:
                                    if verification_channel:
                                        await verification_channel.send("Verification role not found.")
                            else:
                                if verification_channel:
                                    await verification_channel.send(f"{member.mention}, please verify yourself at https://verify.vrcband.com/api/v1/lantern/consent/{api_key}")
                        else:
                            if verification_channel:
                                await verification_channel.send(f"{member.mention}, please verify yourself at https://verify.vrcband.com/api/v1/lantern/consent/{api_key}")
                    else:
                        if verification_channel:
                            await verification_channel.send(f"{member.mention}, please verify yourself at https://verify.vrcband.com/api/v1/lantern/consent/{api_key}")
            except aiohttp.ClientConnectionError:
                if verification_channel:
                    await verification_channel.send("Verification failed. Could not connect to host.")
            except aiohttp.ClientError as e:
                if verification_channel:
                    await verification_channel.send(f"Verification failed. Client error occurred: {e}")
            except TypeError as e:
                if verification_channel:
                    await verification_channel.send(f"Verification failed. Type error occurred: {e}")
            except KeyError as e:
                if verification_channel:
                    await verification_channel.send(f"Verification failed. Key error occurred: {e}")
            if verification_channel:
                await verification_channel.send("Verification failed. Response data malformed.")

def setup(bot: Red):
    bot.add_cog(VerificationCog(bot))

