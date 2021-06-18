from tortoise.models import Model
from tortoise import fields

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
