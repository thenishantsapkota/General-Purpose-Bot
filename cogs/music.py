import asyncio
import datetime as dt
import random
import re
import typing as t
from enum import Enum
import aiohttp

import discord
import wavelink
from discord import Color
from discord.ext import commands

URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
LYRICS_URL = "https://some-random-api.ml/lyrics?title="
HZ_BANDS = (
    20,
    40,
    63,
    100,
    150,
    250,
    400,
    450,
    630,
    1000,
    1600,
    2500,
    4000,
    10000,
    16000,
)
TIME_REGEX = r"([0-9]{1,2})[:ms](([0-9]{1,2})s?)?"
OPTIONS = {
    "1️⃣": 0,
    "2️⃣": 1,
    "3️⃣": 2,
    "4️⃣": 3,
    "5️⃣": 4,
}


class AlreadyConnectedToChannel(commands.CommandError):
    pass


class NoVoiceChannel(commands.CommandError):
    pass


class QueueIsEmpty(commands.CommandError):
    pass


class NoTracksFound(commands.CommandError):
    pass


class PlayerIsAlreadyPaused(commands.CommandError):
    pass


class NoMoreTracks(commands.CommandError):
    pass


class NoPreviousTracks(commands.CommandError):
    pass


class InvalidRepeatMode(commands.CommandError):
    pass


class VolumeTooLow(commands.CommandError):
    pass


class VolumeTooHigh(commands.CommandError):
    pass


class MaxVolume(commands.CommandError):
    pass


class MinVolume(commands.CommandError):
    pass


class NoLyricsFound(commands.CommandError):
    pass


class InvalidEQPreset(commands.CommandError):
    pass


class NonExistentEQBand(commands.CommandError):
    pass


class EQGainOutOfBounds(commands.CommandError):
    pass


class InvalidTimeString(commands.CommandError):
    pass


class RepeatMode(Enum):
    NONE = 0
    ONE = 1
    ALL = 2


class Queue:
    def __init__(self):
        self._queue = []
        self.position = 0
        self.repeat_mode = RepeatMode.NONE

    @property
    def is_empty(self):
        return not self._queue

    @property
    def current_track(self):
        if not self._queue:
            raise QueueIsEmpty

        if self.position <= len(self._queue) - 1:
            return self._queue[self.position]

    @property
    def upcoming(self):
        if not self._queue:
            raise QueueIsEmpty

        return self._queue[self.position + 1 :]

    @property
    def history(self):
        if not self._queue:
            raise QueueIsEmpty

        return self._queue[: self.position]

    @property
    def length(self):
        return len(self._queue)

    def add(self, *args):
        self._queue.extend(args)

    def get_next_track(self):
        if not self._queue:
            raise QueueIsEmpty

        self.position += 1

        if self.position < 0:
            return None
        elif self.position > len(self._queue) - 1:
            if self.repeat_mode == RepeatMode.ALL:
                self.position = 0
            else:
                return None

        return self._queue[self.position]

    def shuffle(self):
        if not self._queue:
            raise QueueIsEmpty

        upcoming = self.upcoming
        random.shuffle(upcoming)
        self._queue = self._queue[: self.position + 1]
        self._queue.extend(upcoming)

    def set_repeat_mode(self, mode):
        if mode == "none":
            self.repeat_mode = RepeatMode.NONE
        elif mode == "1":
            self.repeat_mode = RepeatMode.ONE
        elif mode == "all":
            self.repeat_mode = RepeatMode.ALL

    def empty(self):
        self._queue.clear()
        self.position = 0


class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = Queue()

    async def connect(self, ctx, channel=None):
        if self.is_connected:
            raise AlreadyConnectedToChannel

        if (channel := getattr(ctx.author.voice, "channel", channel)) is None:
            raise NoVoiceChannel

        await super().connect(channel.id)
        return channel

    async def teardown(self):
        try:
            await self.destroy()
        except KeyError:
            pass

    async def add_tracks(self, ctx, tracks):
        if not tracks:
            raise NoTracksFound

        if isinstance(tracks, wavelink.TrackPlaylist):
            self.queue.add(*tracks.tracks)
            embed = discord.Embed(
                title="Add Tracks",
                description=f"Added tracks from playlist to the queue!",
                timestamp=dt.datetime.utcnow(),
                color=ctx.author.color,
            )
            embed.set_footer(
                text=f"Requested by {ctx.author.display_name}",
                icon_url=ctx.author.avatar_url,
            )
            await ctx.send(embed=embed)
        elif len(tracks) == 1:
            self.queue.add(tracks[0])
            # await ctx.send(f"Added {tracks[0].title} to the queue.")
            embed = discord.Embed(
                title="Add Tracks",
                description=f"Added {tracks[0].title} to the queue!",
                timestamp=dt.datetime.utcnow(),
                color=ctx.author.color,
            )
            embed.set_footer(
                text=f"Requested by {ctx.author.display_name}",
                icon_url=ctx.author.avatar_url,
            )
            await ctx.send(embed=embed)
        else:
            if (track := await self.choose_track(ctx, tracks)) is not None:
                self.queue.add(track)
                # await ctx.send(f"Added {track.title} to the queue.")
                embed = discord.Embed(
                    title="Add Tracks",
                    description=f"Added {track.title} to the queue!",
                    timestamp=dt.datetime.utcnow(),
                    color=ctx.author.color,
                )
                embed.set_footer(
                    text=f"Requested by {ctx.author.display_name}",
                    icon_url=ctx.author.avatar_url,
                )
                await ctx.send(embed=embed)

        if not self.is_playing and not self.queue.is_empty:
            await self.start_playback()

    async def choose_track(self, ctx, tracks):
        def _check(r, u):
            return (
                r.emoji in OPTIONS.keys() and u == ctx.author and r.message.id == msg.id
            )

        embed = discord.Embed(
            title="Choose a song",
            description=(
                "\n".join(
                    f"**{i+1}.** {t.title} ({t.length//60000}:{str(t.length%60).zfill(2)})"
                    for i, t in enumerate(tracks[:5])
                )
            ),
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow(),
        )
        embed.set_author(name="Query Results")
        embed.set_footer(
            text=f"Invoked by {ctx.author.display_name}", icon_url=ctx.author.avatar_url
        )

        msg = await ctx.send(embed=embed)
        for emoji in list(OPTIONS.keys())[: min(len(tracks), len(OPTIONS))]:
            await msg.add_reaction(emoji)

        try:
            reaction, _ = await self.bot.wait_for(
                "reaction_add", timeout=60.0, check=_check
            )
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.message.delete()
        else:
            await msg.delete()
            return tracks[OPTIONS[reaction.emoji]]

    async def start_playback(self):
        await self.play(self.queue.current_track)

    async def advance(self):  # remove ctx if breaks
        try:
            if (track := self.queue.get_next_track()) is not None:
                await self.play(track)
                # music = self.bot.get_channel(834792408659001344)

        except QueueIsEmpty:
            pass

    async def repeat_track(self, ctx):
        await self.play(self.queue.current_track)
        # music = self.bot.get_channel(834792408659001344)
        embed = discord.Embed(
            title="Repeat",
            description=f"Looping the current track!",
            timestamp=dt.datetime.utcnow(),
        )
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}",
            icon_url=ctx.author.avatar_url,
        )
        await ctx.send(embed=embed)


class Music(commands.Cog, wavelink.WavelinkMixin):
    def __init__(self, bot):
        self.bot = bot
        self.wavelink = wavelink.Client(bot=bot)
        self.bot.loop.create_task(self.start_nodes())

    # @commands.Cog.listener()
    # async def on_voice_state_update(self, member, before, after):
    #     if not member.bot and after.channel is None:
    #         if not [m for m in before.channel.members if not m.bot]:
    #             await self.get_player(member.guild).teardown()

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node):
        print(f" Wavelink node `{node.identifier}` ready.")

    @wavelink.WavelinkMixin.listener("on_track_stuck")
    @wavelink.WavelinkMixin.listener("on_track_end")
    @wavelink.WavelinkMixin.listener("on_track_exception")
    async def on_player_stop(self, node, payload):
        if payload.player.queue.repeat_mode == RepeatMode.ONE:
            await payload.player.repeat_track()
        else:
            await payload.player.advance()  # remove ctx if breaks

    async def cog_check(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Music commands are not available in DMs.")
            return False

        return True

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        nodes = {
            "MAIN": {
                "host": "127.0.0.1",
                "port": 2333,
                "rest_uri": "http://127.0.0.1:2333",
                "password": "youshallnotpass",
                "identifier": "MAIN",
                "region": "india",
            }
        }

        for node in nodes.values():
            await self.wavelink.initiate_node(**node)

    def get_player(self, obj):
        if isinstance(obj, commands.Context):
            return self.wavelink.get_player(obj.guild.id, cls=Player, context=obj)
        elif isinstance(obj, discord.Guild):
            return self.wavelink.get_player(obj.id, cls=Player)

    @commands.command(name="connect", aliases=["join"])
    # @commands.has_role("DJ")
    async def connect_command(self, ctx, *, channel: t.Optional[discord.VoiceChannel]):
        player = self.get_player(ctx)
        channel = await player.connect(ctx, channel)
        # await ctx.send(f"Connected to {channel.name}.")
        await ctx.message.add_reaction("👍")

    @connect_command.error
    async def connect_command_error(self, ctx, exc):
        if isinstance(exc, AlreadyConnectedToChannel):
            await ctx.send("Already connected to a voice channel.")
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send("No suitable voice channel was provided.")

    @commands.command(name="disconnect", aliases=["leave", "dc", "fuckoff"])
    @commands.has_role("DJ")
    async def disconnect_command(self, ctx):
        player = self.get_player(ctx)
        await player.teardown()
        player.queue.empty()
        # await ctx.send("Disconnected.")
        await ctx.message.add_reaction("👋")

    @commands.command(name="play", aliases=["p"])
    # @commands.has_role("DJ")
    async def play_command(self, ctx, *, query: t.Optional[str]):
        player = self.get_player(ctx)

        if not player.is_connected:
            await player.connect(ctx)

        if query is None:
            if player.queue.is_empty:
                raise QueueIsEmpty

            await ctx.message.add_reaction("▶️")

        else:
            query = query.strip("<>")
            if not re.match(URL_REGEX, query):
                query = f"ytsearch:{query}"

            await player.add_tracks(ctx, await self.wavelink.get_tracks(query))

    @play_command.error
    async def play_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("No songs to play as the queue is empty.")
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send("No suitable voice channel was provided.")

    @commands.command(name="pause")
    @commands.has_role("DJ")
    async def pause_command(self, ctx):
        player = self.get_player(ctx)

        if player.is_paused:
            raise PlayerIsAlreadyPaused

        await player.set_pause(True)
        # await ctx.send("Playback paused.")
        await ctx.message.add_reaction("⏸")

    @pause_command.error
    async def pause_command_error(self, ctx, exc):
        if isinstance(exc, PlayerIsAlreadyPaused):
            await ctx.send("Already paused.")

    @commands.command(name="stop")
    @commands.has_role("DJ")
    async def stop_command(self, ctx):
        player = self.get_player(ctx)
        player.queue.empty()
        await player.stop()
        # await ctx.send("Playback stopped.")
        await ctx.message.add_reaction("🛑")

    @commands.command(name="next", aliases=["skip", "n"])
    @commands.has_role("DJ")
    async def next_command(self, ctx):
        player = self.get_player(ctx)

        if not player.queue.upcoming:
            raise NoMoreTracks

        await player.stop()
        # await ctx.send("Playing next track in queue.")
        embed = discord.Embed(color=ctx.author.color)
        embed.set_author(
            name="Playing next track in the queue!", icon_url=ctx.author.avatar_url
        )
        await ctx.send(embed=embed)

    @next_command.error
    async def next_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send(
                "This could not be executed as the queue is currently empty."
            )
        elif isinstance(exc, NoMoreTracks):
            await ctx.send("There are no more tracks in the queue.")

    @commands.command(name="previous", aliases=["prev"])
    @commands.has_role("DJ")
    async def previous_command(self, ctx):
        player = self.get_player(ctx)

        if not player.queue.history:
            raise NoPreviousTracks

        player.queue.position -= 2
        await player.stop()
        embed = discord.Embed(color=ctx.author.color)
        embed.set_author(
            name="Playing previous track in the queue!", icon_url=ctx.author.avatar_url
        )
        await ctx.send(embed=embed)

    @previous_command.error
    async def previous_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send(
                "This could not be executed as the queue is currently empty."
            )
        elif isinstance(exc, NoPreviousTracks):
            await ctx.send("There are no previous tracks in the queue.")

    @commands.command(name="shuffle")
    @commands.has_role("DJ")
    async def shuffle_command(self, ctx):
        player = self.get_player(ctx)
        player.queue.shuffle()
        embed = discord.Embed(
            color=ctx.author.color,
        )
        embed.set_author(
            name="Queue has been shuffled.", icon_url=ctx.author.avatar_url
        )
        await ctx.send(embed=embed)

    @shuffle_command.error
    async def shuffle_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("The queue could not be shuffled as it is currently empty.")

    @commands.command(name="repeat")
    @commands.has_role("DJ")
    async def repeat_command(self, ctx, mode: str = None):
        player = self.get_player(ctx)
        if mode not in ("none", "1", "all"):
            player.queue.set_repeat_mode(1)
            embed = discord.Embed(
                color=ctx.author.color,
            )
            embed.set_footer(text=f"Invoked by {ctx.author}")
            embed.set_author(name=f"Looping the current song!")
            await ctx.send(embed=embed)

        player.queue.set_repeat_mode(mode)
        # await ctx.send(f"The repeat mode has been set to {mode}.")
        embed = discord.Embed(color=ctx.author.color)
        embed.set_author(name=f"The repeat mode has been set to {mode}")
        embed.set_footer(text=f"Invoked by {ctx.author}")
        await ctx.send(embed=embed)

    @commands.command(name="queue", aliases=["q"])
    async def queue_command(self, ctx, show: t.Optional[int] = 10):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        embed = discord.Embed(
            description=f"Showing up to next {show} tracks",
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow(),
        )
        embed.set_author(name=f"Displaying {ctx.guild.name}'s current queue.")
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}",
            icon_url=ctx.author.avatar_url,
        )
        embed.add_field(
            name="Currently playing",
            value=getattr(
                player.queue.current_track, "title", "No tracks currently playing."
            ),
            inline=False,
        )
        if upcoming := player.queue.upcoming:
            embed.add_field(
                name="Next up",
                value=f"\n".join(
                    f"**{i+1}.** {t.title}" for (i,t) in enumerate(upcoming[:show])
                ),
                inline=False,
            )

        msg = await ctx.send(embed=embed)

    @queue_command.error
    async def queue_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("The queue is currently empty.")

    # @commands.command(name="np")
    # async def now_playing_command(self, ctx):
    #     player = self.get_player(ctx)

    #     if player.queue.is_empty:
    #         raise QueueIsEmpty

    #     embed = discord.Embed(
    #         description=getattr(
    #             player.queue.current_track, "title", "No tracks currently playing."
    #         ),
    #         colour=ctx.author.colour,
    #         timestamp=dt.datetime.utcnow(),
    #     )
    #     embed.set_footer(
    #         text=f"Requested by {ctx.author.display_name}",
    #         icon_url=ctx.author.avatar_url,
    #     )
    #     embed.set_author(name="Now Playing")
    #     await ctx.send(embed=embed)

    @commands.command(name="clear")
    @commands.has_role("DJ")
    async def clear_command(self, ctx):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty
        player.queue.empty()
        await player.stop()
        # await ctx.send("Playback stopped.")
        embed = discord.Embed(color=ctx.author.color)
        embed.set_author(
            name="Queue has been cleared successfully.", icon_url=ctx.author.avatar_url
        )
        await ctx.send(embed=embed)

    @clear_command.error
    async def clear_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("The queue is currently empty.")

    @commands.group(name="volume", invoke_without_command=True)
    async def volume_group(self, ctx, volume: int):
        player = self.get_player(ctx)

        if volume < 0:
            raise VolumeTooLow

        if volume > 150:
            raise VolumeTooHigh

        await player.set_volume(volume)
        #await ctx.send(f"Volume set to {volume:,}%")
        embed = discord.Embed(
            color = discord.Color.green(),
            description = f"🔊| **Volume set to {volume:,}%**"
        )
        await ctx.send(embed=embed)

    @volume_group.error
    async def volume_group_error(self, ctx, exc):
        if isinstance(exc, VolumeTooLow):
            await ctx.send("The volume must be 0% or above.")
        elif isinstance(exc, VolumeTooHigh):
            await ctx.send("The volume must be 150% or below.")

    @volume_group.command(name="up")
    async def volume_up_command(self, ctx):
        player = self.get_player(ctx)

        if player.volume == 150:
            raise MaxVolume

        await player.set_volume(value := min(player.volume + 30, 150))
        #await ctx.send(f"Volume set to {value:,}%")
        embed = discord.Embed(
            color = discord.Color.green(),
            description = f"🔊| **Volume set to {volume:,}%**"
        )
        await ctx.send(embed=embed)

    @volume_up_command.error
    async def volume_up_command_error(self, ctx, exc):
        if isinstance(exc, MaxVolume):
            await ctx.send("The player is already at max volume.")

    @volume_group.command(name="down")
    async def volume_down_command(self, ctx):
        player = self.get_player(ctx)

        if player.volume == 0:
            raise MinVolume

        await player.set_volume(value := max(0, player.volume - 30))
        #await ctx.send(f"Volume set to {value:,}%")
        embed = discord.Embed(
            color = discord.Color.green(),
            description = f"🔉| **Volume set to {volume:,}%**"
        )
        await ctx.send(embed=embed)

    @volume_down_command.error
    async def volume_down_command_error(self, ctx, exc):
        if isinstance(exc, MinVolume):
            await ctx.send("The player is already at min volume.")

    @commands.command(name="lyrics")
    async def lyrics_command(self, ctx, name: t.Optional[str]):
        player = self.get_player(ctx)
        name = name or player.queue.current_track.title

        async with ctx.typing():
            async with aiohttp.request("GET", LYRICS_URL + name, headers={}) as r:
                if not 200 <= r.status <= 299:
                    raise NoLyricsFound

                data = await r.json()

                if len(data["lyrics"]) > 2000:
                    return await ctx.send(f"<{data['links']['genius']}>")

                embed = discord.Embed(
                    title=data["title"],
                    description=data["lyrics"],
                    colour=ctx.author.colour,
                    timestamp=dt.datetime.utcnow(),
                )
                embed.set_thumbnail(url=data["thumbnail"]["genius"])
                embed.set_author(name=data["author"])
                await ctx.send(embed=embed)

    @lyrics_command.error
    async def lyrics_command_error(self, ctx, exc):
        if isinstance(exc, NoLyricsFound):
            await ctx.send("No lyrics could be found.")

    @commands.command(name="eq")
    async def eq_command(self, ctx, preset: str):
        player = self.get_player(ctx)

        eq = getattr(wavelink.eqs.Equalizer, preset, None)
        if not eq:
            raise InvalidEQPreset

        await player.set_eq(eq())
        await ctx.send(f"Equaliser adjusted to the {preset} preset.")

    @eq_command.error
    async def eq_command_error(self, ctx, exc):
        if isinstance(exc, InvalidEQPreset):
            await ctx.send(
                "The EQ preset must be either 'flat', 'boost', 'metal', or 'piano'."
            )

    @commands.command(name="adveq", aliases=["aeq"])
    async def adveq_command(self, ctx, band: int, gain: float):
        player = self.get_player(ctx)

        if not 1 <= band <= 15 and band not in HZ_BANDS:
            raise NonExistentEQBand

        if band > 15:
            band = HZ_BANDS.index(band) + 1

        if abs(gain) > 10:
            raise EQGainOutOfBounds

        player.eq_levels[band - 1] = gain / 10
        eq = wavelink.eqs.Equalizer(
            levels=[(i, gain) for i, gain in enumerate(player.eq_levels)]
        )
        await player.set_eq(eq)
        await ctx.send("Equaliser adjusted.")

    @adveq_command.error
    async def adveq_command_error(self, ctx, exc):
        if isinstance(exc, NonExistentEQBand):
            await ctx.send(
                "This is a 15 band equaliser -- the band number should be between 1 and 15, or one of the following "
                "frequencies: " + ", ".join(str(b) for b in HZ_BANDS)
            )
        elif isinstance(exc, EQGainOutOfBounds):
            await ctx.send(
                "The EQ gain for any band should be between 10 dB and -10 dB."
            )

    @commands.command(name="playing", aliases=["np"])
    async def playing_command(self, ctx):
        player = self.get_player(ctx)

        if not player.is_playing:
            raise PlayerIsAlreadyPaused

        embed = discord.Embed(
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow(),
        )
        embed.set_author(name="Now playing", icon_url=self.bot.user.avatar_url)
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}",
            icon_url=ctx.author.avatar_url,
        )
        embed.add_field(
            name="Track title", value=player.queue.current_track.title, inline=False
        )
        embed.add_field(
            name="Artist", value=player.queue.current_track.author, inline=False
        )

        position = divmod(player.position, 60000)
        length = divmod(player.queue.current_track.length, 60000)
        embed.add_field(
            name="Position",
            value=f"{int(position[0])}:{round(position[1]/1000):02}/{int(length[0])}:{round(length[1]/1000):02}",
            inline=False,
        )

        await ctx.send(embed=embed)

    @playing_command.error
    async def playing_command_error(self, ctx, exc):
        if isinstance(exc, PlayerIsAlreadyPaused):
            await ctx.send("There is no track currently playing.")

    @commands.command(name="skipto", aliases=["playindex"])
    async def skipto_command(self, ctx, index: int):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        if not 0 <= index <= player.queue.length:
            raise NoMoreTracks

        player.queue.position = index - 2
        await player.stop()
        await ctx.send(f"Playing track in position {index}.")

    @skipto_command.error
    async def skipto_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("There are no tracks in the queue.")
        elif isinstance(exc, NoMoreTracks):
            await ctx.send("That index is out of the bounds of the queue.")

    @commands.command(name="restart")
    async def restart_command(self, ctx):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        await player.seek(0)
        await ctx.send("Track restarted.")

    @restart_command.error
    async def restart_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("There are no tracks in the queue.")

    @commands.command(name="seek")
    async def seek_command(self, ctx, position: str):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        if not (match := re.match(TIME_REGEX, position)):
            raise InvalidTimeString

        if match.group(3):
            secs = (int(match.group(1)) * 60) + (int(match.group(3)))
        else:
            secs = int(match.group(1))

        await player.seek(secs * 1000)
        await ctx.send("Seeked.")


def setup(bot):
    bot.add_cog(Music(bot))
