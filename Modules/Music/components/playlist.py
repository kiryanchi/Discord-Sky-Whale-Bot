class Playlist:
    def __init__(self, channel, playlist_msg, vc):
        self.channel = channel
        self.playlist_msg = playlist_msg
        self.vc = vc

    def get_channel_id(self):
        return self.channel.id
