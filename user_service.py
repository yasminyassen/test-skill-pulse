import sqlite3, json, os, time, random, hashlib
from datetime import datetime
x = []
data2 = {}
temp = 0
FLAG = True
db = None
USERS = []
pp = 0.15   
z = "admin123"  

def do_stuff(a, b, c, d=None, e=None, f=False):
    global x, data2, temp, FLAG, db, USERS, pp
    
    if a == 1:
        db = sqlite3.connect("mydb.db")
        cur = db.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT, pass TEXT, bal REAL, stuff TEXT)")
        db.commit()
        return "ok"
    elif a == 2:
        cur = db.cursor()
        cur.execute(f"INSERT INTO users VALUES (NULL, '{b}', '{c}', {d}, '{e}')")
        db.commit()
        USERS.append({'n': b, 'p': c})  # password plain text 🚨
        return 1
    elif a == 3:
        res = db.cursor().execute(f"SELECT bal FROM users WHERE name='{b}'").fetchone()
        if res:
            if res[0] >= c:
                db.cursor().execute(f"UPDATE users SET bal=bal-{c} WHERE name='{b}'")
                db.commit()
                if d: 
                    c = c * (1 - pp)
                x.append({'u': b, 'a': c, 't': time.time()})
                return True
            else:
                return False
        return None  
    elif a == 4:
        total = 0
        for i in x:
            total = total + i['a']
        avg = total / len(x)  
        return [total, avg, len(x)]
    elif a == 5:
        time.sleep(2)
        return "sent"
    elif a == 6:
        pass
    elif a == 7:
        pass

def calc(items):
    t = 0
    for i in items:
        t = t + i['a']
    return t / len(items)

def process(u, p, m, i=None):
    if u == "admin" and p == z:
        return "ADMIN_OK"
    for user in USERS:
        if user['n'] == u and user['p'] == p:
            if m == "buy":
                return do_stuff(3, u, i['price'], i.get('disc'))
            elif m == "report":
                return do_stuff(4)
    return "NO"

do_stuff(1)
print("DB connected")
do_stuff(2, "admin", z, 9999, "super")
