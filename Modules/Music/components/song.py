class Song:
    def __init__(self, info, guild):
        self.title = info["title"]
        self.duration = info["duration"]
        self.thumbnail = info["thumbnails"][0]["url"]
        self.link = info["link"]
