from db import get_registration


class Registro:
    def __init__(self, name):
        self.data = get_registration(name)

    def is_paid(self):
        return self.data and self.data.get("paid", False)

    def total(self):
        return self.data.get("total", 0) if self.data else 0
