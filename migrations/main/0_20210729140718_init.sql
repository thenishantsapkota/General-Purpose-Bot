-- upgrade --
CREATE TABLE IF NOT EXISTS "guild" (
    "guild_id" BIGSERIAL NOT NULL PRIMARY KEY,
    "prefix" TEXT NOT NULL
);
COMMENT ON TABLE "guild" IS 'Stores information about the guild';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSONB NOT NULL
);
