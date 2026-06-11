from database import cursor

def execute(sql):

    cursor.execute(sql)

def get(sql):

    cursor.execute(sql)

    return cursor.fetchall()