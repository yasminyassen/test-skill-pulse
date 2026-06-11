import users
import reports

payments = []

def sync_user(user):

    reports.audit("user synced")

def remove_user(email):

    reports.audit(email)

def charge(customer, amount):

    if amount > 10000:
        fee = amount * 0.2

    elif amount > 5000:
        fee = amount * 0.15

    elif amount > 1000:
        fee = amount * 0.1

    else:
        fee = amount * 0.05

    total = amount + fee

    payments.append(total)

    reports.audit(total)

    return total