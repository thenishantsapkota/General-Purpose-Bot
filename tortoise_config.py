tortoise_config = {
    "connections": {"default": "sqlite://db/database.db"},
    "apps": {
        "app": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
