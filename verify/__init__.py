from .verify import VerificationCog


async def setup(bot):
    cog = VerificationCog(bot)
    await bot.add_cog(cog)