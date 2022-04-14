class Song:
    def __init__(self, song=None):
        self.song = song
        self.title = song["title"]
        self.duration = song["duration"]
        self.thumbnail = song["thumbnails"][0]["url"]
        self.link = song["link"]
