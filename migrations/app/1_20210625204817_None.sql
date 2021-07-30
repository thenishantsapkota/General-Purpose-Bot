-- upgrade --
CREATE TABLE IF NOT EXISTS "staffroles" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "admin_role" BIGINT NOT NULL,
    "mod_role" BIGINT NOT NULL,
    "staff_role" BIGINT NOT NULL,
    "guild_id" BIGINT NOT NULL
) /* Stores StaffRoles of the server */;
CREATE TABLE IF NOT EXISTS "mutes" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "member_id" BIGINT NOT NULL,
    "guild_id" BIGINT NOT NULL,
    "time" TIMESTAMP NOT NULL,
    "role_id" TEXT NOT NULL
) /* Stores Per Guild Mute Data */;
CREATE TABLE IF NOT EXISTS "onMemberJoin" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "channel_id" BIGINT NOT NULL,
    "guild_id" BIGINT NOT NULL,
    "welcome_message" TEXT NOT NULL,
    "base_role_id" BIGINT NOT NULL
) /* Stores the Welcome channel and Welcome Message of the bot. */;
CREATE TABLE IF NOT EXISTS "overrides" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "command_name" TEXT NOT NULL,
    "enable" INT NOT NULL  DEFAULT 0,
    "channel_id" BIGINT NOT NULL,
    "guild_id" BIGINT NOT NULL
) /* Stores Overrides */;
CREATE TABLE IF NOT EXISTS "bot_prefix" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "guild_id" BIGINT NOT NULL,
    "prefix" TEXT NOT NULL
) /* Stores Prefix of the bot. */;
CREATE TABLE IF NOT EXISTS "reputation_points" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "member_name" TEXT NOT NULL,
    "points" INT NOT NULL  DEFAULT 0,
    "guild_id" BIGINT NOT NULL
) /* Stores Global Member Reputation. */;
CREATE TABLE IF NOT EXISTS "warnings" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "member_id" BIGINT NOT NULL,
    "guild_id" BIGINT NOT NULL,
    "reason" TEXT NOT NULL
) /* Stores Per Guild Warnings */;
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSON NOT NULL
);
