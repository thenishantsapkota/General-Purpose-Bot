-- upgrade --
CREATE TABLE IF NOT EXISTS "onMemberJoin" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "channel_id" BIGINT NOT NULL,
    "guild_id" BIGINT NOT NULL,
    "welcome_message" TEXT NOT NULL,
    "base_role_id" BIGINT NOT NULL
) /* Stores the Welcome channel and Welcome Message of the bot. */;;
DROP TABLE IF EXISTS "welcomechannel";
-- downgrade --
DROP TABLE IF EXISTS "onMemberJoin";
