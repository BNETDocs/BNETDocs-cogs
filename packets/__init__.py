
from .packets import BnetPackets


async def setup(bot):
    await bot.add_cog(BnetPackets(bot))
