"""Models file to generate models for tortoise-orm"""
from tortoise import fields
from tortoise.models import Model


class GuildModel(Model):
    """Defining a guild model to store prefix of the guild"""

    guild_id = fields.BigIntField(pk=True)
    prefix = fields.TextField(default=">")

    class Meta:
        """Meta class to set table name and description"""

        table = "guild"
        table_description = "Stores information about the guild"


class ModerationRoles(Model):
    """Defining a moderation roles model to store moderation roles for the server"""

    id = fields.IntField(pk=True)
    admin_role = fields.BigIntField(null=True)
    mod_role = fields.BigIntField(null=True)
    staff_role = fields.BigIntField(null=True)
    guild_id = fields.BigIntField()

    class Meta:
        """Meta class to set table name and description"""

        table = "staffroles"
        table_description = "Stores StaffRoles of the server"


class MuteModel(Model):
    """Defining a Mute model to store mutes"""

    id = fields.IntField(pk=True)
    member_id = fields.BigIntField()
    guild_id = fields.BigIntField()
    time = fields.DatetimeField()
    role_id = fields.TextField()

    class Meta:
        """Meta class to set table name and description"""

        table = "mutes"
        table_description = "Stores Per Guild Mute Data"


class WarningsModel(Model):
    "Defining a warn model to store warns"
    id = fields.IntField(pk=True)
    member_id = fields.BigIntField()
    guild_id = fields.BigIntField()
    reason = fields.TextField()
    author_name = fields.TextField()
    date = fields.TextField()

    class Meta:
        """Meta class to set table name and description"""

        table = "warnings"
        table_description = "Stores Per Guild Warnings"
