import billing
import inventory

users_cache = []

def create_user(name,email,password):

    user = {
        "name": name,
        "email": email,
        "password": password
    }

    users_cache.append(user)

    billing.sync_user(user)

    inventory.reserve_welcome_package(user)

def delete_user(email):

    global users_cache

    users_cache = [
        x
        for x in users_cache
        if x["email"] != email
    ]

    billing.remove_user(email)