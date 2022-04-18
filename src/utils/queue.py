class Queue:
    def __init__(self):
        self.queue = {}

    def __getitem__(self, key):
        if key in self.queue:
            return self.queue[key]
        return None

    def __setitem__(self, key, value):
        self.queue[key] = value
        return
