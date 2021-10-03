
from datetime import datetime, timedelta

from redbot.core import checks, commands


class Ktbpa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_listener(self.on_message, 'on_message')
        super().__init__()

    async def on_message(self, message):
        if not message.content:
            return

        if message.channel.id == 648966495476383772:
            # auto publish messages in #blue-tracker
            return await message.publish()

        text = message.content
        if text.lower() == "?trigger":
            prefix = await self.bot.get_prefix(message)[-1]
            return await message.channel.send("The bot's current trigger is: `%s`" % prefix)

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

    @commands.command()
    @commands.guild_only()
    @checks.mod_or_permissions(ban_members=True)
    @checks.bot_has_permissions(ban_members=True)
    async def loadban(self, ctx, period: commands.converter.TimedeltaConverter):
        """Bans everyone who joined the guild in the given time before now."""
        limiter = timedelta(hours=12)
        if period > limiter:
            await ctx.send(f"Error: Loadban can only be used for up to {limiter.seconds / 3600} hours.")
        else:
            banned = []
            async for member in ctx.guild.fetch_members(after=(datetime.now() - period)):
                if len([role for role in member.roles if role != ctx.guild.default_role]) == 0:
                    banned.append(str(member.id))
                    await member.ban(reason="Loadban", delete_message_days=1)

            await ctx.send(f"Banned {len(banned)} users: {', '.join(banned)}")

    def cog_unload(self):
        self.bot.remove_listener(self.on_message, 'on_message')
