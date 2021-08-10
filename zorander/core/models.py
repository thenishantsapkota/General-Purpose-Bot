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


class ModerationRoles(Model):
    """Defining a moderation roles model"""

    id = fields.IntField(pk=True)
    admin_role = fields.BigIntField()
    mod_role = fields.BigIntField()
    staff_role = fields.BigIntField()
    guild_id = fields.BigIntField()

    class Meta:
        table = "staffroles"
        table_description = "Stores StaffRoles of the server"
