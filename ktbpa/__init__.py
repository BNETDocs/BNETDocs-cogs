
from .ktbpa import Ktbpa


def setup(bot):
    bot.add_cog(Ktbpa(bot))
