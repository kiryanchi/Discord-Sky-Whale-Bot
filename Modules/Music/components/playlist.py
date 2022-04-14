from Modules.Music.components.song import Song


class Playlist:
    def __init__(self, channel, playlist_msg, vc=None):
        self.channel = channel
        self.playlist_msg = playlist_msg
        self.vc = vc
        self.queue = {"prev_song": None, "current_song": None, "next_songs": []}

    def get_channel_id(self) -> int:
        return self.channel.id

    def get_current_song(self) -> Song:
        return self.queue["current_song"]

    def get_next_songs(self) -> list:
        return self.queue["next_songs"]
