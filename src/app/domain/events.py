class Event:
    
    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

class ProductCreateEvent(Event):
        event = "products.create"
