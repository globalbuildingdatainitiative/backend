from aiocache import caches

# You can use either classes or strings for referencing classes
caches.set_config(
    {
        "default": {
            "cache": "aiocache.SimpleMemoryCache",
            "serializer": {"class": "aiocache.serializers.StringSerializer"},
        },
    }
)
