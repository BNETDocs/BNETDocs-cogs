
from redbot.core import commands

import aiohttp


APPLICATION_LAYERS = {
    1: "SID",
    2: "PKT",
    3: "MCP",
    4: "D2GS",
    5: "W3GS",
    6: "PACKET",
    7: "BNLS",
    8: "SCGP",
    9: "SID2"
}

TRANSPORT_LAYERS = {
    1: "TCP",
    2: "UDP",
    3: "ICMP"
}

PACKET_DIRECTIONS = {
    "CS": 1,
    "SC": 2,
    "P2P": 3
}

APP_ALIASES = {
    "SID": ["BNCS", "BNET"],
    "PKT": ["UDP"],
    "MCP": ["REALM"],
    "PACKET": ["BOTNET"],
    "SID2": ["BNET2"]
}


def _rdict(d):
    return {v: k for k, v in d.items()}


class BnetPackets(commands.Cog):
    """Provides information about documented Battle.net packets."""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.packets = {}
        self.session = aiohttp.ClientSession()
        bot.loop.create_task(self.update_packet_index())

    async def update_packet_index(self):
        url = "https://bnetdocs.org/packet/index.json"
        headers = {"user-agent": "Red-cog/3.0"}
        async with self.session.get(url, headers=headers) as r:
            data = await r.json()

        self.packets = {}
        for pak in data["packets"]:
            app = pak["packet_application_layer_id"]

            if app not in self.packets:
                self.packets[app] = {}
            self.packets[app][pak["id"]] = {
                "packet_name": pak["packet_name"],
                "packet_id": pak["packet_id"],
                "packet_direction_id": pak["packet_direction_id"]
            }

        return len(self.packets) > 0

    @commands.command()
    async def packet(self, ctx, ident, app="SID", direction=None):
        """Links the documentation for a packet from BNETDocs.org."""
        async with ctx.channel.typing():
            async for url in self.find_packet(ctx, ident, app, direction):
                await ctx.send(url)

    async def find_packet(self, ctx, ident, app, direction):
        # Check that we have packet data available
        if len(self.packets) == 0:
            await ctx.send("Packet data is not available at this time.")
            return

        app = app.upper()

        # Determine what kind of identity was provided (name or packet ID)
        if ident[:2] == "0x":
            id_type = "packet_id"
            id_value = int(ident[2:], 16)
        else:
            id_type = "packet_name"
            id_value = ident.upper()

            # Packet name includes the app prefix. Try to use app as direction, or overwrite.
            if not direction and app in PACKET_DIRECTIONS:
                direction = PACKET_DIRECTIONS.get(app)
            app = id_value.split('_')[0]

        # Convert specified direction to database ID value
        if direction and isinstance(direction, str):
            direction = PACKET_DIRECTIONS.get(direction.upper())

        # Find which application this packet belongs to
        if app not in APPLICATION_LAYERS.values():
            if not direction and app in PACKET_DIRECTIONS:
                direction = PACKET_DIRECTIONS.get(app)
                app = "SID"
            else:
                for app_id, aliases in APP_ALIASES.items():
                    if app in aliases:
                        app = app_id
                        break

                if app not in APPLICATION_LAYERS.values():
                    await ctx.send("Unknown app layer: %s. Available: %s" %
                                   (app, ', '.join(APPLICATION_LAYERS.values())))
                    return

        # Search all the packets in this application for the one we want
        found = False
        layer = self.packets.get(_rdict(APPLICATION_LAYERS).get(app), [])
        for obj_id, packet_data in layer.items():
            if packet_data.get(id_type) == id_value:

                # If a direction is specified, only show that packet.
                packet_direction = packet_data.get("packet_direction_id")
                if direction and packet_direction != direction:
                    continue

                found = True
                packet_name = packet_data.get("packet_name")
                yield "https://bnetdocs.org/packet/%i/%s" % (obj_id, packet_name.lower())

        if not found:
            await ctx.send("Sorry, a packet with that identifier was not found.")

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())
