from modules.imports import *
from models import ReputationPoints


class Reputation(Cog):
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 86400, commands.BucketType.user)
    @command(name="rep", brief="Give a reputation point to the user")
    async def reputation_command(self, ctx, member: Member):
        await self.reputation_handler(ctx, member)

    async def reputation_handler(self, ctx, member):
        if member is ctx.author:
            await ctx.send("you cannot give reputation points to yourself.")
            return
        model, _ = await ReputationPoints.get_or_create(
            member_name=member.name, guild_id=ctx.guild.id
        )
        model.points = model.points + 1
        await model.save()
        embed = Embed(color=Color.green())  # timestamp=datetime.utcnow())
        embed.set_author(
            name=f"{ctx.author.name} gave a reputation point to {member.name}",
            icon_url=ctx.author.avatar_url,
        )
        await ctx.send(embed=embed)

    @command(name="replist", brief="View the leaderboard of reputation for the server.")
    async def replist_command(self, ctx):
        rep_model = (
            await ReputationPoints.filter(guild_id=ctx.guild.id)
            .order_by("-points")
            .limit(10)
        )
        leaderboard = "\n".join(
            [
                f"**{i+1}.** {model.member_name} - {model.points}"
                for (i, model) in enumerate(rep_model)
            ]
        )
        # print(leaderboard)
        embed = Embed(
            description=leaderboard if len(rep_model) else "No data found",
            color=Color.blurple(),
            timestamp=datetime.utcnow(),
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        embed.set_author(
            name=f"{ctx.guild.name} Reputation Leaderboard", icon_url=ctx.guild.icon_url
        )
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Reputation(client))
