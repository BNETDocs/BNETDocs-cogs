
from .packets import BnetPackets


def setup(bot):
    bot.add_cog(BnetPackets(bot))
