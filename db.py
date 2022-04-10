import sqlite3


class DB:
    def __init__(self, db):
        self.con = sqlite3.connect(db)
        self.cursor = self.con.cursor()

    def init(self):
        self.cursor.execute("CREATE TABLE server(ID int)")
        self.cursor.execute(
            "CREATE TABLE muisc(ID int, Chanel int, \
                PlayList int, Player int, Button int)"
        )

    def close(self):
        self.con.close()

    def insert(self, table, *values):
        try:
            assert len(values) > 0, "VALUES 값이 필요합니다."

            if table == "music":
                assert (
                    len(values) == 5
                ), "music 테이블은 id, channel, playlist, player, button이 필요합니다."
            elif table == "server":
                assert len(values) == 1, "server 테이블은 id이 필요합니다."
            else:
                assert table == "music" or table == "server", f"{table}은 존재하지 않습니다."
        except AssertionError as e:
            print(e)
        else:
            items = " ".join(values)
            query_string = f"INSERT INTO {table} VALUES ({items})"
            self.cursor.execute(query_string)
            self.con.commit()

    def fetch(self, table, *values):
        try:
            assert len(values) > 0, "VALUES 값이 필요합니다."
            assert table == "music" or table == "server", f"{table}은 존재하지 않습니다."
        except AssertionError as e:
            print(e)
        else:
            self.cursor.execute(f"SELECT {values} FROM {table}")

    def insert_server(self, id):
        self.cursor.execute(f"INSERT INTO server VALUES({id})")

    def disconnect(self):
        self.con.close()
