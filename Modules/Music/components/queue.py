class Queue:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            print("Queue 생성 완료")
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.queue = {}

    def __getitem__(self, key):
        return self.queue[key]

    def __setitem__(self, key, value):
        self.queue[key] = value
        return
