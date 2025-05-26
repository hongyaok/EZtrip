import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from func.emailconfig import email, password

def mass_email(emails, trip_id):
    emails = emails.split(',')
    for email in emails:
        email = email.strip() 
        if email: 
            send_email(email, trip_id)

def send_email(recipient_email, trip_id, smtp_server='smtp.gmail.com', smtp_port=587):
    link = f"https://eztrip-vbi5.com/join/{trip_id}"  # test
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = recipient_email
    msg['Subject'] = f"Trip Invitation - Trip ID: {trip_id}"
    body = f"You have been invited to join a trip with ID: {trip_id}.\
        \nJoin the trip now!: {link}!"

    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email, password)
        server.send_message(msg)
        server.quit()

if __name__ == "__main__":
    send_email('<put ur email>@gmail.com', 1)