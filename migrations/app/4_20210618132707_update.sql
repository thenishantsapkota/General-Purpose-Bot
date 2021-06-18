-- upgrade --
CREATE TABLE IF NOT EXISTS "bot_prefix" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "guild_id" BIGINT NOT NULL,
    "prefix" TEXT NOT NULL
) /* Stores Prefix of the bot. */;
-- downgrade --
DROP TABLE IF EXISTS "bot_prefix";
