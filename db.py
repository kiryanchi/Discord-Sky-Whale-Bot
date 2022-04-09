import sqlite3


class DB:
    def __init__(self, db):
        self.con = sqlite3.connect(db)
        self.cursor = self.con.cursor()

    def init(self):
        self.cursor.execute("CREATE TABLE server(Date text, ID int)")
        self.cursor.execute("CREATE TABLE muisc(ID int, Chanel int, PlayList int, Player int, Button int)")


if __name__ == '__main__':
    db = DB('muple.db')
    db.init()
