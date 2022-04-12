import sqlite3


class DB:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.con = sqlite3.connect("muple.db")
        self.cursor = self.con.cursor()

    def save(self, query_string, param=None):
        if param:
            self.cursor.execute(query_string, param)
        else:
            self.cursor.execute(query_string)
        self.con.commit()

    def close(self):
        self.con.close()
        print("DB 성공적으로 해제 됨")

    def insert_music_channel(self, guild_id, channel_id, playlist_id, button_id):
        query_string = f"INSERT INTO music_channel VALUES ({guild_id}, {channel_id}, {playlist_id}, {button_id})"
        self.save(query_string)

    def select_music_channel(self, guild_id):
        query_string = "SELECT * FROM music_channel WHERE guild_id='%s'" % guild_id
        self.cursor.execute(query_string)

        return self.cursor.fetchall()

    def delete_music_channel(self, guild_id):
        query_string = "DELETE FROM music_channel WHERE guild_id='%s'" % guild_id
        self.save(query_string)
