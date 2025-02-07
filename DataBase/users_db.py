import sqlite3 as sq


async def db_conect() -> None:
    global cur
    global db

    db = sq.connect("tg_GOST.db")
    cur = db.cursor()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, status TEXT, requ INTEGER)")
    db.commit()


async def cheker_user(user_id) -> bool:
    cur.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (user_id,))
    if cur.fetchone()[0] == 0:
        return False
    else:
        return True


async def get_new_user(user_id, name, status, requ) -> None:
    cur.execute("INSERT INTO 'users' ('user_id', 'name', 'status', 'requ') VALUES (?, ?, ?, ?)",
                (user_id, name, status, requ,))
    db.commit()


async def get_status(user_id) -> str:
    cur.execute("SELECT status FROM users WHERE user_id = ?", (user_id,))
    return cur.fetchone()[0]


async def set_status(status, user_id) -> None:
    cur.execute("UPDATE users SET status = ? WHERE user_id = ?", (status, user_id,))
    db.commit()


async def get_requ_count(user_id) -> str:
    cur.execute("SELECT requ FROM users WHERE user_id = ?", (user_id,))
    return cur.fetchone()[0]


async def set_requ_count(requ, user_id) -> None:
    cur.execute("UPDATE users SET requ = ? WHERE user_id = ?", (requ, user_id,))
    db.commit()


async def reset_password(user_id, requ) -> None:
    cur.execute("UPDATE users SET requ = ? WHERE user_id = ?", (requ, user_id,))
    db.commit()


async def close() -> None:
    db.close()
