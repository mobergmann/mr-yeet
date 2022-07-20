import sqlite3


class Database:
    db_connection: sqlite3.Connection = sqlite3.connect("database.sqlite3")
    db_cursor: sqlite3.Cursor = db_connection.cursor()

    def __init__(self):
        # Create table if not existent
        self.db_cursor.execute("""CREATE TABLE IF NOT EXISTS "users" (
            "user_id" INTEGER NOT NULL PRIMARY KEY UNIQUE,
            "has_yeeted" INTEGER NOT NULL,
            "been_yeeted" INTEGER NOT NULL);""")

    def get_user(self, user_id: int):
        self.db_cursor.execute(f"SELECT * FROM yeet WHERE user_id = ?", (user_id, ))
        return self.db_cursor.fetchone()

    def been_yeeted(self, user_id: int):
        user = self.get_user(user_id)

        if not user:
            # insert default value, because user is not in database
            self.db_cursor.execute("INSERT INTO yeet VALUES(?, 0, 1)", (user_id,))
        else:
            # update users been_yeet to +1
            increased_score = user.been_yeeted + 1
            self.db_cursor.execute("UPDATE yeet SET been_yeeted = ? WHERE user_id = ?", (increased_score, user_id))

        self.db_connection.commit()

    def has_yeeted(self, user_id: int):
        user = self.get_user(user_id)

        if not user:
            # insert default value, because user is not in database
            self.db_cursor.execute("INSERT INTO yeet VALUES(?, 1, 0)", (user_id,))
        else:
            # update users has_yeet to +1
            increased_score = user.has_yeeted + 1
            self.db_cursor.execute("UPDATE yeet SET has_yeeted = ? WHERE user_id = ?", (increased_score, user_id))

        self.db_connection.commit()
