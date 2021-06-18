from modules.imports import *
from models import OverrideModel


class CmdOverrides(Cog):
    def __init__(self, client):
        self.client = client

    @commands.group()
    @commands.has_permissions(administrator=True)
    async def toggle(
        self, ctx, command: str, channels: Greedy[TextChannel], toggle: bool
    ):
        await self.toggle_handler(ctx, command, channels, toggle)

    async def toggle_handler(
        self, ctx, command, channels: List[TextChannel], toggle: bool
    ):
        # channel = channel or ctx.channel
        # toggle = str(toggle).lower()
        command = self.client.get_command(command)
        if command == ctx.command:
            await ctx.send(f"You cannot disable this command.")

        else:
            for channel in channels:
                model, _ = await OverrideModel.get_or_create(
                    guild_id=ctx.guild.id,
                    command_name=command.name,
                    channel_id=channel.id,
                )
                model.enable = toggle
                await model.save()
            toggle_string = "enabled" if toggle else "disabled"
            channel_mention = "".join([channel.mention for channel in channels])
            await ctx.send(f"`{command.name}` {toggle_string} in {channel_mention}")

    @command()
    async def check(self, ctx, command: str, channel: Optional[TextChannel]):
        command = self.client.get_command(command)
        channel = channel or ctx.channel
        check = await OverrideModel.get_or_none(
            guild_id=ctx.guild.id, command_name=command.name, channel_id=channel.id
        )
        try:
            toggle_str = "enabled" if check.enable else "disabled"
            await ctx.send(
                f"`{command.name}` has been {toggle_str} in {channel.mention}"
            )
        except AttributeError:
            await ctx.send(f"No data of the command in the database.")


def setup(client):
    client.add_cog(CmdOverrides(client))
