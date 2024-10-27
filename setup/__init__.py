"""Package for Setup cog."""

import json
from pathlib import Path

from redbot.core.bot import Red

from .setup import Setup2

with Path(__file__).parent.joinpath("info.json").open() as fp:
    __red_end_user_data_statement__ = json.load(fp)["end_user_data_statement"]


async def setup(bot):
    await bot.add_cog(Setup2(bot))
