from tortoise import fields
from tortoise.models import Model

# Use this when adding new tables
# aerich migrate
# aerich upgrade


class OverrideModel(Model):

    id = fields.IntField(pk=True)
    command_name = fields.TextField()
    enable = fields.BooleanField(default=False)
    channel_id = fields.BigIntField()
    guild_id = fields.BigIntField()

    class Meta:
        table = "overrides"
        table_description = "Stores Overrides"


class PrefixModel(Model):

    id = fields.IntField(pk=True)
    guild_id = fields.BigIntField()
    prefix = fields.TextField()

    class Meta:
        table = "bot_prefix"
        table_description = "Stores Prefix of the bot."


class OnMemberJoinModel(Model):

    id = fields.IntField(pk=True)
    channel_id = fields.BigIntField()
    guild_id = fields.BigIntField()
    welcome_message = fields.TextField()
    base_role_id = fields.BigIntField()

    class Meta:
        table = "onMemberJoin"
        table_description = "Stores the Welcome channel and Welcome Message of the bot."


class ReputationPoints(Model):

    id = fields.IntField(pk=True)
    member_name = fields.TextField()
    points = fields.IntField(default=0)
    guild_id = fields.BigIntField()  # before migrating comment this

    class Meta:
        table = "reputation_points"
        table_description = "Stores Global Member Reputation."


class MuteModel(Model):
    id = fields.IntField(pk=True)
    member_id = fields.BigIntField()
    guild_id = fields.BigIntField()
    time = fields.DatetimeField()  # before migrating comment this
    role_id = fields.TextField()  # before migrating comment this

    class Meta:
        table = "mutes"
        table_description = "Stores Per Guild Mute Data"


class WarnModel(Model):
    id = fields.IntField(pk=True)
    member_id = fields.BigIntField()
    guild_id = fields.BigIntField()
    reason = fields.TextField()

    class Meta:
        table = "warnings"
        table_description = "Stores Per Guild Warnings"


class ModerationRoles(Model):
    id = fields.IntField(pk=True)
    admin_role = fields.BigIntField()
    mod_role = fields.BigIntField()
    staff_role = fields.BigIntField()
    guild_id = fields.BigIntField()

    class Meta:
        table = "staffroles"
        table_description = "Stores StaffRoles of the server"


class TicketModel(Model):
    id = fields.IntField(pk=True)
    category_id = fields.BigIntField()
    message_id = fields.BigIntField()
    message_channel_id = fields.BigIntField()
    guild_id = fields.BigIntField()

    class Meta:
        table = "tickets"
        table_description = "Stores info about tickets"


class JoinToCreate(Model):
    id = fields.IntField(pk=True)
    member_id = fields.BigIntField(null=True)
    channel_id = fields.BigIntField(null=True)

    class Meta:
        table = "voice_channels"
        table_description = "Stores info about voice channels created."
