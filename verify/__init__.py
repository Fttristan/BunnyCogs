from .verify import VerificationCog


async def setup(bot):
    cog = Verify(bot)
    await bot.add_cog(cog)