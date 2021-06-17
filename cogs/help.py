from modules.imports import *

def syntax(command):
	cmd_and_aliases = "|".join([str(command), *command.aliases])
	params = []

	for key, value in command.params.items():
		if key not in ("self", "ctx"):
			params.append(f"[{key}]" if "NoneType" in str(value) else f"<{key}>")

	params = " ".join(params)

	return f"```{cmd_and_aliases} {params}```"


class HelpMenu(ListPageSource):
	def __init__(self, ctx, data):
		self.ctx = ctx

		super().__init__(data, per_page=3)

	async def write_page(self, menu, fields=[]):
		offset = (menu.current_page*self.per_page) + 1
		len_data = len(self.entries)

		embed = Embed(title="Help",
					  description="List of commands available in the bot.",
					  colour=Color.blurple())
		embed.set_thumbnail(url=self.ctx.guild.me.avatar_url)
		embed.set_footer(text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} commands.")

		for name, value in fields:
			embed.add_field(name=name, value=value, inline=False)

		return embed

	async def format_page(self, menu, entries):
		fields = []

		for entry in entries:
			fields.append((entry.brief or "No description", syntax(entry)))

		return await self.write_page(menu, fields)


class Help(Cog):
	def __init__(self, client):
		self.client = client
		self.client.remove_command("help")

	async def cmd_help(self, ctx, command):
		embed = Embed(title=f"Help with `{command}`",
					  description=syntax(command),
					  colour=Color.blurple())
		embed.add_field(name="Command description", value=command.help)
		await ctx.send(embed=embed)

	@command(name="help", brief="Shows this menu!")
	async def show_help(self, ctx, cmd: Optional[str]):
		"""Shows this message."""
		if cmd is None:
			menu = MenuPages(source=HelpMenu(ctx, list(self.client.commands)),
							 clear_reactions_after=True,
							 timeout=60.0)
			await menu.start(ctx)

		else:
			if (command := get(self.client.commands, name=cmd)):
				await self.cmd_help(ctx, command)

			else:
				await ctx.send("That command does not exist.")


def setup(client):
    client.add_cog(Help(client))