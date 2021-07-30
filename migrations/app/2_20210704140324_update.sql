-- upgrade --
CREATE TABLE IF NOT EXISTS "tickets" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "category_id" BIGINT NOT NULL,
    "message_id" BIGINT NOT NULL,
    "message_channel_id" BIGINT NOT NULL,
    "guild_id" BIGINT NOT NULL
) /* Stores info about tickets */;
-- downgrade --
DROP TABLE IF EXISTS "tickets";
