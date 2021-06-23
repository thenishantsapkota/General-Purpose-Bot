from tortoise.models import Model
from tortoise import fields

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


class TokenModel(Model):

    bot_token = fields.TextField(pk=True)

    class Meta:
        table = "bot_token"
        table_description = "Stores the bot token."


class ReputationPoints(Model):

    id = fields.IntField(pk=True)
    member_name = fields.TextField()
    points = fields.IntField(default=0)
    guild_id = fields.BigIntField()

    class Meta:
        table = "reputation_points"
        table_description = "Stores Global Member Reputation"


class MuteModel(Model):
    id = fields.IntField(pk=True)
    member_id = fields.BigIntField()
    guild_id = fields.BigIntField()
    time = fields.IntField()
    role_id = fields.TextField()

    class Meta:
        table = "mutes"
        table_description = "Stores Per Guild Mute Data"


class WarnModel(Model):
    id = fields.IntField(pk=True)
    member_id =fields.BigIntField()
    guild_id = fields.BigIntField()
    reason = fields.TextField()

    class Meta:
        table = "warnings"
        table_description = "Stores Per Guild Warnings"
