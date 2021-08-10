"""file to generate models for tortoise-orm"""
from tortoise import fields
from tortoise.models import Model


class GuildModel(Model):
    """Defining a guild model"""

    guild_id = fields.BigIntField(pk=True)
    prefix = fields.TextField(default=">")

    class Meta:
        """Meta class to set table name and description"""

        table = "guild"
        table_description = "Stores information about the guild"


class MusicModel(Model):
    """Defining a Music Model"""

    guild_id = fields.BigIntField(pk=True)
    channel_id = fields.BigIntField()

    class Meta:
        table = "music"
        table_description = "Stores information about Music Cog"
