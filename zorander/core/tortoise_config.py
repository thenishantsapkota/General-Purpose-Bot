tortoise_config = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "database": "zorander_v2",
                "host": "localhost",
                "password": "test123",
                "port": 5432,
                "user": "nishant",
            },
        }
    },
    "apps": {
        "main": {
            "models": ["zorander.core.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}
