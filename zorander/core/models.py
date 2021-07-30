from tortoise import fields
from tortoise.models import Model


class GuildModel(Model):

    guild_id = fields.BigIntField(pk=True)
    prefix = fields.TextField(default=">")

    class Meta:
        table = "guild"
        table_description = "Stores information about the guild"
