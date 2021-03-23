import sqlite3

def get_db():
    db = sqlite3.connect('local.db')
    db.row_factory = sqlite3.Row

    return db


def init_db():
    db = get_db()

    with open('local_schema.sql', 'r') as sql_file:
        sql_script = sql_file.read()
    
    cur = db.cursor()
    cur.executescript(sql_script)
    db.commit()
    db.close()
