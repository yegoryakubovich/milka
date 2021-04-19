import sqlite3

conn = sqlite3.connect("db.db")
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS accounts
                  (
                  account_id        INT
                  )
               """)

cursor.execute("""CREATE TABLE IF NOT EXISTS videos
                  (
                  video_id          INTEGER PRIMARY KEY AUTOINCREMENT,
                  account_id        INT,
                  message_id        INT,
                  score             INT,
                  adm_id            INT
                  )
               """)

cursor.execute("""CREATE TABLE IF NOT EXISTS admins
                  (
                  account_id        INT UNIQUE
                  )
               """)


def query(sql):
    cursor.execute(sql)
    conn.commit()
    return cursor.fetchall()


def reconnect():
    sqlite3.connect("db.db")


def account_insert(account_id):
    try:
        query("INSERT INTO accounts VALUES ({})".format(account_id))
        return True
    except:
        print("[DataBase] Произошла ошибка: account_insert")
        sqlite3.connect("db.db")
        return False


def account_select():
    try:
        result = query("SELECT * FROM accounts")
        if result:
            return result
    except:
        print("[DataBase] Произошла ошибка: account_select")
        sqlite3.connect("db.db")
        return 0


def account_select_rating():
    try:
        accounts = account_select()
        rating = []
        for account in accounts:
            account_id = account[0]
            score = video_select_sum(account_id)
            rating.append([score, account_id])
        rating.sort(reverse=True)
        return rating

    except:
        print("[DataBase] Произошла ошибка: account_select_rating")
        sqlite3.connect("db.db")
        return 0


def account_exits(account_id):
    try:
        result = query("SELECT * FROM accounts WHERE account_id = {}".format(account_id))
        if result:
            return True
        else:
            return False
    except:
        print("[DataBase] Произошла ошибка: account_exits")
        sqlite3.connect("db.db")
        return False


def admin_insert(account_id):
    try:
        query("INSERT INTO admins VALUES ({})".format(account_id))
        return True
    except:
        print("[DataBase] Произошла ошибка: admin_insert")
        sqlite3.connect("db.db")
        return False


def admin_exits(account_id):
    try:
        result = query("SELECT * FROM admins WHERE account_id = {}".format(account_id))
        if result:
            return True
        else:
            return False
    except:
        print("[DataBase] Произошла ошибка: admin_exits")
        sqlite3.connect("db.db")
        return False


def video_insert(account_id, message_id):
    try:
        cursor.execute("""INSERT INTO videos(account_id, message_id) VALUES (?, ?)""",
                       (account_id, message_id))
        conn.commit()
        return True
    except:
        print("[DataBase] Произошла ошибка: video_insert")
        sqlite3.connect("db.db")
        return False


def video_select(video_id):
    try:
        result = query("SELECT * FROM videos WHERE video_id = {}".format(video_id))
        if result:
            result = result[0]
            return {
                'video_id': result[0],
                'account_id': result[1],
                'message_id': result[2],
                'score': result[3],
                'adm_id': result[4]
            }
        else:
            return None
    except:
        print("[DataBase] Произошла ошибка: video_select")
        sqlite3.connect("db.db")
        return False


def video_select_sum(account_id):
    try:
        result = query("SELECT SUM(score) FROM videos WHERE account_id = {} AND score NOT NULL".format(account_id))
        if result[0][0] is not None:
            return result[0][0]
        else:
            return 0
    except:
        print("[DataBase] Произошла ошибка: video_select_sum")
        sqlite3.connect("db.db")
        return False


def video_select_adm(adm_id):
    try:
        result = query("SELECT * FROM videos WHERE adm_id = {}".format(adm_id))
        if result:
            result = result[-1]
            return {
                'video_id': result[0],
                'account_id': result[1],
                'message_id': result[2],
                'score': result[3],
                'adm_id': result[4]
            }
        else:
            return None
    except:
        print("[DataBase] Произошла ошибка: video_select_adm")
        sqlite3.connect("db.db")
        return False


def video_select_first():
    try:
        result = query("SELECT * FROM videos WHERE adm_id IS NULL AND score IS NULL")
        if result:
            result = result[0]
            return {
                'video_id': result[0],
                'account_id': result[1],
                'message_id': result[2],
                'score': result[3],
                'adm_id': result[4]
            }
        else:
            return None
    except:
        print("[DataBase] Произошла ошибка: video_select_first")
        sqlite3.connect("db.db")
        return False


def video_update_score(video_id, score):
    try:

        query("UPDATE videos SET score = {} WHERE video_id = {}".format(score, video_id))
        return True
    except:
        print("[DataBase] Произошла ошибка: video_update_score")
        sqlite3.connect("db.db")
        return False


def video_update_adm_id(video_id, adm_id):
    try:
        if adm_id is None:
            query("UPDATE videos SET adm_id = NULL WHERE video_id = {}".format(video_id))
            return True
        else:
            query("UPDATE videos SET adm_id = {} WHERE video_id = {}".format(adm_id, video_id))
            return True
    except:
        print("[DataBase] Произошла ошибка: video_update_adm_id")
        sqlite3.connect("db.db")
        return False
