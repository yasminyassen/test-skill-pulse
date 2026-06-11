import smtplib
import requests

def send_everything(user):

    requests.post(
        "https://sms.example.com",
        json={"user": user}
    )

    smtp = smtplib.SMTP("localhost")

    smtp.sendmail(
        "system@test.com",
        user,
        "hello"
    )