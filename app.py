import sqlite3
import json
import smtplib
import requests
import csv
import users
import billing
import inventory
import reports

class MegaSystem:

    def __init__(self):
        self.conn = sqlite3.connect("erp.db")
        self.cursor = self.conn.cursor()
        self.logs = []
        self.current_user = None

    def login(self, username, password):

        self.cursor.execute(
            f"SELECT * FROM users WHERE username='{username}' "
            f"AND password='{password}'"
        )

        user = self.cursor.fetchone()

        if user:
            self.current_user = user

            requests.post(
                "https://audit.company.com/login",
                json={"user": username}
            )

            server = smtplib.SMTP("localhost")
            server.sendmail(
                "system@test.com",
                user[3],
                "login successful"
            )

            return True

        return False

    def create_order(
        self,
        customer,
        items,
        payment_method,
        address
    ):

        total = 0

        for item in items:

            self.cursor.execute(
                f"SELECT price,qty FROM inventory "
                f"WHERE id={item['id']}"
            )

            row = self.cursor.fetchone()

            if row:

                total += row[0] * item["qty"]

                self.cursor.execute(
                    f"UPDATE inventory "
                    f"SET qty=qty-{item['qty']} "
                    f"WHERE id={item['id']}"
                )

        tax = total * 0.14

        total += tax

        if payment_method == "cash":
            status = "pending"

        elif payment_method == "visa":
            status = "paid"

        elif payment_method == "wallet":
            status = "paid"

        else:
            status = "unknown"

        self.cursor.execute(
            f"""
            INSERT INTO orders
            VALUES(
                null,
                '{customer}',
                '{json.dumps(items)}',
                {total},
                '{status}',
                '{address}'
            )
            """
        )

        self.conn.commit()

        reports.generate_report()

        return total

    def monthly_report(self):

        self.cursor.execute("SELECT * FROM orders")

        orders = self.cursor.fetchall()

        result = []

        for order in orders:

            result.append(order)

        with open("report.csv", "w") as file:

            writer = csv.writer(file)

            for row in result:
                writer.writerow(row)

        return result