
from .ktbpa import Ktbpa


async def setup(bot):
    await bot.add_cog(Ktbpa(bot))
