import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from io import BytesIO
from config import email, password
import qrcode

def mass_email(sender, location, desc, emails, trip_id):
    emails = emails.split(',')
    for email_addr in emails:
        email_addr = email_addr.strip() 
        if email_addr: 
            send_email(sender, location, desc, email_addr, trip_id)

def send_email(sender, location, desc, recipient_email, trip_id, smtp_server='smtp.gmail.com', smtp_port=587):
    link = f"https://eztrip-vbi5.onrender.com/join/{trip_id}"  # test
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(link)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = BytesIO()
    qr_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    msg = MIMEMultipart('related')
    msg['From'] = email
    msg['To'] = recipient_email
    msg['Subject'] = f"Trip Invitation to {location} from {sender}!"
    
    main_mess = f"""
        <html>
            <body>
                <p>You have been invited to join a trip to <strong>{location}</strong>.</p>
                
                <p><strong>Trip Description:</strong> {desc}</p>
                
                <p>Join the trip now: <a href="{link}">{link}</a></p>
                
                <p>Or scan this QR code:</p>
                <img src="cid:qr_code" alt="QR Code" style="width:200px;height:200px;">
                
                <p>If you have any questions, please contact {sender} directly.</p>
                
                <p>Best regards,<br>EZtrip Team</p>
            </body>
        </html>
    """
    
    msg.attach(MIMEText(main_mess, 'html'))
    img_attachment = MIMEImage(img_buffer.getvalue())
    img_attachment.add_header('Content-ID', '<qr_code>')
    img_attachment.add_header('Content-Disposition', 'inline', filename='qr_code.png')
    msg.attach(img_attachment)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email, password)
        server.send_message(msg)
        server.quit()
