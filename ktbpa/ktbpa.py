
from redbot.core import commands


class Ktbpa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_listener(self.on_message, 'on_message')
        super().__init__()

    async def on_message(self, message):
        if message.content[0] != "?":
            return

        text = message.content
        if text.lower() == "?trigger":
            prefixes = await self.bot.get_prefix(message)
            return await message.channel.send("The bot's current trigger is: %s" % prefixes)

    @commands.command()
    @commands.guild_only()
    async def whoami(self, ctx):
        """Gives the requesting user's highest role."""
        who = ctx.message.author
        role = who.top_role

        if who == ctx.guild.owner:
            return await ctx.send("Our glorious leader, %s." % who.display_name)
        elif role == ctx.guild.default_role:
            return await ctx.send("You are nobody special.")
        else:
            return await ctx.send("%s. Role: %s." % (who.display_name, role.name))

    def cog_unload(self):
        self.bot.remove_listener(self.on_message, 'on_message')
