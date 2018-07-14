from datetime import datetime
from time import sleep


def generate_unique_id():
    return _id_generator.next()


class _IdGenerator:
    def __init__(self):
        self.previous = self._generate_present_timestamp()

    def next(self):
        id = self._generate_present_timestamp()
        if id == self.previous:
            sleep(0.001)
            id += 1
        self.previous = id
        return id

    def _generate_present_timestamp(self):
        return int(datetime.now().timestamp() * 1000)


_id_generator = _IdGenerator()
