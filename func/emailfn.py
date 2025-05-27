import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from func.emailconfig import email, password

def mass_email(sender, location, desc, emails, trip_id):
    emails = emails.split(',')
    for email in emails:
        email = email.strip() 
        if email: 
            send_email(sender, location, desc, email, trip_id)

def send_email(sender, location, desc, recipient_email, trip_id, smtp_server='smtp.gmail.com', smtp_port=587):
    link = f"https://eztrip-vbi5.onrender.com/join/{trip_id}"  # test
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = recipient_email
    msg['Subject'] = f"Trip Invitation from {sender}!"
    body = f"\nYou have been invited to join a trip to {location}.\
        \n\nTrip Description: {desc}\n\
        \n\nJoin the trip now!: {link}!\
        \n\nIf you have any questions, please contact {sender} directly.\n\nBest regards,\nEZtrip Team"

    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email, password)
        server.send_message(msg)
        server.quit()

if __name__ == "__main__":
    send_email('<put ur email>@gmail.com', 1) # not working anymore, change accordingly
