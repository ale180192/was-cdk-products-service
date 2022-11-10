
class Redis:
    pass

class PublisherRedis:

    def __init__(self) -> None:
        self.redis = Redis()

    def publish_event(self, event: str) -> None:
        self.redis.publish(message=event, topic="products")