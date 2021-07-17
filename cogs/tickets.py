from models import ModerationRoles, PrefixModel, TicketModel
from modules.imports import *


class NotEnoughPermissions(commands.CommandError):
    pass


class Tickets(Cog):
    def __init__(self, client):
        self.client = client

    async def has_permissions(self, member: Member, permission: str):
        if getattr(member.guild_permissions, permission, False):
            return True
        return False

    async def rolecheck(self, member: Member, role: Role):
        if role in member.roles:
            return True
        return False

    async def fetchRoleData(self, guild: discord.Guild):
        model = await ModerationRoles.get_or_none(guild_id=guild.id)
        if model is None:
            return False
        adminrole = discord.utils.get(guild.roles, id=model.admin_role)
        modrole = discord.utils.get(guild.roles, id=model.mod_role)
        staffrole = discord.utils.get(guild.roles, id=model.staff_role)
        roles = {
            "adminrole": adminrole,
            "modrole": modrole,
            "staffrole": staffrole,
        }
        return roles

    @command(name="configure_ticket")
    async def config_ticket_command(
        self, ctx, message: discord.Message, category: discord.CategoryChannel = None
    ):
        author = ctx.author
        guild = ctx.guild
        adminrole = (await self.fetchRoleData(guild)).get("adminrole")
        if not (
            await self.has_permissions(author, "manage_messages")
            or await self.rolecheck(author, adminrole)
        ):
            raise NotEnoughPermissions(
                "You don't have either the roles required or the permissions."
            )
        if message is None or category is None:
            await ctx.send(
                "Ticket configuration failed because required arguments were missing."
            )
            return
        model, _ = await TicketModel.get_or_create(
            guild_id=guild.id,
            message_channel_id=message.channel.id,
            message_id=message.id,
            category_id=category.id,
        )
        await model.save()
        await message.add_reaction("\U0001F3AB")
        await ctx.send(
            "Ticket system has been configured successfully.", delete_after=10
        )

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if (
            payload.member.id != self.client.user.id
            and str(payload.emoji) == "\U0001F3AB"
        ):
            model = await TicketModel.get_or_none(guild_id=payload.guild_id)
            if model is None:
                return

            if payload.message_id == model.message_id:
                guild = self.client.get_guild(payload.guild_id)

                for category in guild.categories:
                    if category.id == model.category_id:
                        break
                channel = guild.get_channel(model.message_channel_id)

                ticket_num = (
                    1
                    if len(category.channels) == 0
                    else int(category.channels[-1].name.split("-")[1]) + 1
                )

                ticket_channel = await category.create_text_channel(
                    f"ticket {ticket_num}",
                    topic=f"Ticket Channel for {ticket_num}",
                    permission_synced=True,
                )

                await ticket_channel.set_permissions(
                    payload.member, read_messages=True, send_messages=True
                )

                message = await channel.fetch_message(model.message_id)
                await message.remove_reaction(payload.emoji, payload.member)

                record = await PrefixModel.get_or_none(guild_id=payload.guild_id)
                prefix = ">" if not record else record.prefix

                embed = Embed(
                    color=Color.blurple(),
                    timestamp=datetime.utcnow(),
                    description=f"Thank you for creating the ticket.\n Use {prefix}closeticket to close the ticket.\nMention your issue here.",
                )
                embed.set_author(name=f"Ticket Created by {payload.member}")
                await ticket_channel.send(payload.member.mention, embed=embed)

                try:
                    await self.client.wait_for(
                        "message",
                        check=lambda m: m.channel == ticket_channel
                        and m.author == payload.member
                        and m.content == f"{prefix}closeticket",
                        timeout=3600,
                    )

                except asyncio.TimeoutError:
                    await ticket_channel.delete()

                else:
                    await ticket_channel.delete()

    @command(name="delticketconfig")
    async def delticketconfig_command(self, ctx):
        model = await TicketModel.get_or_none(guild_id=ctx.guild.id)
        if model is None:
            await ctx.send("No data found in the database.")
            return
        await model.delete()
        await ctx.send(
            "Configuration for ticket deleted successfully for this server.",
            delete_after=10,
        )


def setup(client):
    client.add_cog(Tickets(client))
