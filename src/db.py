import sqlite3
import os


class DB:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            print(f"[INFO] {args[0]} DB 연결 됨")  # log
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db):
        self.con = sqlite3.connect(db)
        self.cursor = self.con.cursor()
        if not os.path.isfile(db):
            self.make_db_file()

    def make_db_file(self):
        query_string = "CREATE TABLE music_channel(guild_id int, channel_id int)"
        self.update_query(query_string)

    def update_query(self, query_string, param=None):
        if param:
            self.cursor.execute(query_string, param)
        else:
            self.cursor.execute(query_string)
        self.con.commit()

    def close(self):
        self.con.close()
        print("DB 성공적으로 해제 됨")

    def insert_music_channel(self, guild_id, channel_id):
        query_string = f"INSERT INTO music_channel VALUES ({guild_id}, {channel_id})"
        self.update_query(query_string)

    def select_all_music_channel(self):
        try:
            query_string = "SELECT * FROM music_channel"
            self.update_query(query_string)
        except sqlite3.OperationalError:
            self.make_db_file()
            self.select_all_music_channel()
            return
        return self.cursor.fetchall()

    def select_music_channel(self, guild_id):
        query_string = (
            "SELECT channel_id FROM music_channel WHERE guild_id='%s'" % guild_id
        )
        self.update_query(query_string)

        return self.cursor.fetchall()

    def delete_music_channel(self, guild_id):
        query_string = "DELETE FROM music_channel WHERE guild_id='%s'" % guild_id
        self.update_query(query_string)
