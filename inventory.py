import users
import reports

items = []

def reserve_welcome_package(user):

    reports.audit(user["email"])

def add_item(name, qty, price):

    items.append({
        "name": name,
        "qty": qty,
        "price": price
    })

def remove_item(name):

    global items

    items = [
        x
        for x in items
        if x["name"] != name
    ]