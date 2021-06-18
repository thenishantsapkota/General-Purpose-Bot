-- upgrade --
CREATE TABLE IF NOT EXISTS "prefix" (
    "guild_id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "prefix_bot" TEXT NOT NULL
) /* Stores prefixes of the bot */;
-- downgrade --
DROP TABLE IF EXISTS "prefix";
