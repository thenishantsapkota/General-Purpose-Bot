from modules.imports import *
import aiohttp


class Compiler(Cog):
    def __init__(self, client):
        self.client = client

    async def _run_code(self, *, lang: str, code: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://emkc.org/api/v1/piston/execute",
                json={"language": lang, "source": code},
            ) as resp:
                return await resp.json()

    @command(name="compile",brief="Returns output of the code provided.")
    async def compile_command(self, ctx, *, codeblock: str):
        regex = re.compile(r"(\w*)\s*(?:```)(\w*)?([\s\S]*)(?:```$)")
        matches = regex.findall(codeblock)
        if not matches:
            embed = Embed(color=Color.blurple())
            embed.set_author(
                name=f"Could not find codeblock.", icon_url=self.client.user.avatar_url
            )
            await ctx.send(embed=embed)
        lang = matches[0][0] or matches[0][1]
        if not lang:
            embed = Embed(color=Color.blurple())
            embed.set_author(
                name=f"Could not find language hinted in the codeblock.",
                icon_url=self.client.user.avatar_url,
            )
        code = matches[0][2]
        result = await self._run_code(lang=lang, code=code)
        await self._send_result(ctx, result)

    async def _send_result(self, ctx, result: dict):
        if "message" in result:
            return await ctx.send(
                embed=Embed(
                    title="Error", description=result["message"], color=Color.red()
                )
            )
        output = result["output"]
        embed = Embed(timestamp=datetime.utcnow(), color=Color.green())
        output = output[:500]
        shortened = len(output) > 500
        lines = output.splitlines()
        shortened = shortened or (len(lines) > 15)
        output = "\n".join(lines[:15])
        output += shortened * "\n\n**Output shortened**"
        embed.set_author(
            name=f"Your code was in  {str(result['language']).capitalize()}.",
            icon_url=ctx.author.avatar_url,
        )
        embed.add_field(name="Output", value=f"`{output}`" or "**<No output>**")
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.message.add_reaction("<a:loading:856179279292006430>")
        await asyncio.sleep(2)
        await ctx.message.clear_reaction("<a:loading:856179279292006430>")

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Compiler(client))
