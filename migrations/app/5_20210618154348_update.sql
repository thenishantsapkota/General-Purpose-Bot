-- upgrade --
CREATE TABLE IF NOT EXISTS "welcomechannel" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "channel_id" BIGINT NOT NULL,
    "guild_id" BIGINT NOT NULL,
    "welcome_message" TEXT NOT NULL
) /* Stores the Welcome channel and Welcome Message of the bot. */;
-- downgrade --
DROP TABLE IF EXISTS "welcomechannel";
