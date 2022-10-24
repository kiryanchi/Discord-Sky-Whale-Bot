class Song:
    def __init__(self, info):
        self.title = info["title"]
        self.channel = info["channel"]
        self.webpage_url = info["webpage_url"]
        self.duration = info["duration"]
        self.thumbnail = info["thumbnail"]
        self.url = info["url"]

    def __repr__(self):
        return self.title
