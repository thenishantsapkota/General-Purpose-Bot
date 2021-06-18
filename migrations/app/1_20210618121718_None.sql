-- upgrade --
CREATE TABLE IF NOT EXISTS "overrides" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "command_name" TEXT NOT NULL,
    "enable" INT NOT NULL  DEFAULT 0,
    "channel_id" BIGINT NOT NULL,
    "guild_id" BIGINT NOT NULL
) /* Stores Overrides */;
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSON NOT NULL
);
