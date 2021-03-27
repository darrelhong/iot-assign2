import sqlite3

def get_db():
    db = sqlite3.connect('instance/edge_db.sqlite')
    db.row_factory = sqlite3.Row

    return db
