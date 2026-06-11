import users
import inventory
import billing

history = []

def audit(message):

    history.append(message)

def generate_report():

    report = {

        "users": len(users.users_cache),
        "items": len(inventory.items),
        "payments": len(billing.payments)

    }

    print(report)

    return report