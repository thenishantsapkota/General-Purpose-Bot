-- upgrade --
CREATE TABLE IF NOT EXISTS "bot_token" (
    "bot_token" TEXT NOT NULL  PRIMARY KEY
) /* Stores the bot token. */;
-- downgrade --
DROP TABLE IF EXISTS "bot_token";
