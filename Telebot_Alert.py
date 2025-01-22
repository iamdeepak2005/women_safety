import telebot
import cv2
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from twilio.rest import Client


# add emails  and phone numbers here
emails=["dkag709@gmail.com"]
phoneno=["9047253765"]
# Initialize the Telegram bot
bot = telebot.TeleBot("6843529361:AAEEPwP36laT-Hc8nO3CQHcuwg80tIqQOH8")
CHAT_ID = "1484998700"


TWILIO_ACCOUNT_SID = "your_account_sid"
TWILIO_AUTH_TOKEN = "your_auth_token"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+your_sandbox_number"  # Replace with your Twilio WhatsApp number
TWILIO_MESSAGE_NUMBER = "+your_message_number"  # Replace with your Twilio WhatsApp number
from_email = "your-registered_email"
password = "your_smtp_password"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_sms_twilio(scenario):
    
    base_message = '''
🚨 **ALERT!** 🚨

We have detected a potentially dangerous situation. Please take immediate action:

'''

    # Depending on the scenario, we will format the message differently
    if scenario == "female_surrounded":
        message_content = '''
👩‍🦰 **Female Surrounded by Men** 👨‍🦰

It appears a female is surrounded by multiple men. This could be a dangerous situation. 

‼️ **Immediate action is required**:
1. Call **112** or your local emergency number.
2. Stay in a safe place, do not try to confront the individuals.
3. Keep your phone on, and try to stay discreet to avoid escalating the situation.
        
🔴 **Be alert and stay safe!**
        '''
    elif scenario == "stressed":
                message = f'''
        ⚠️ **ALERT: Woman in Distress** ⚠️

        A woman is showing signs of **distress or fear**. This is a possible emergency situation. 🚨

        Please contact the authorities immediately:
        📞 **Police Station**: +1 (800) 123-4567
        📞 **Emergency Number**: 112

        **Steps to take**:
        1️⃣ Ensure the safety of the woman and approach carefully.
        2️⃣ Observe the situation for any further signs of distress.
        3️⃣ Offer support if needed while waiting for help.
        4️⃣ Do not escalate the situation unless absolutely necessary.
        '''
    else:
        message_content = '''
👩‍🦰 **Female Alone** 🌙

A female is detected in an isolated area . This could pose a safety risk. 

‼️ **Immediate action is required**:
1. Call **112** or your local emergency number for help.
2. If possible, try to move to a well-lit area with people nearby.
3. Keep your phone charged and available for communication.

🔴 **Stay alert, your safety is important!**
        '''
    # Combine the base message with the scenario-specific content
    full_message = base_message + message_content

    for i in phoneno:
        message = client.messages.create(
        body=full_message,
        from_=TWILIO_MESSAGE_NUMBER,
        to=f"+91{i}"
        )
    # Your Twilio credentials

    # Send the SMS



def send_whatsapp_message( scenario: str):
    # Default message structure
    base_message = '''
🚨 **ALERT!** 🚨

We have detected a potentially dangerous situation. Please take immediate action:

'''

    # Depending on the scenario, we will format the message differently
    if scenario == "female_surrounded":
        message_content = '''
👩‍🦰 **Female Surrounded by Men** 👨‍🦰

It appears a female is surrounded by multiple men. This could be a dangerous situation. 

‼️ **Immediate action is required**:
1. Call **112** or your local emergency number.
2. Stay in a safe place, do not try to confront the individuals.
3. Keep your phone on, and try to stay discreet to avoid escalating the situation.
        
🔴 **Be alert and stay safe!**
        '''
    elif scenario == "stressed":
                message = f'''
        ⚠️ **ALERT: Woman in Distress** ⚠️

        A woman is showing signs of **distress or fear**. This is a possible emergency situation. 🚨

        Please contact the authorities immediately:
        📞 **Police Station**: +1 (800) 123-4567
        📞 **Emergency Number**: 112

        **Steps to take**:
        1️⃣ Ensure the safety of the woman and approach carefully.
        2️⃣ Observe the situation for any further signs of distress.
        3️⃣ Offer support if needed while waiting for help.
        4️⃣ Do not escalate the situation unless absolutely necessary.
        '''
    else:
        message_content = '''
👩‍🦰 **Female Alone** 🌙

A female is detected in an isolated area . This could pose a safety risk. 

‼️ **Immediate action is required**:
1. Call **112** or your local emergency number for help.
2. If possible, try to move to a well-lit area with people nearby.
3. Keep your phone charged and available for communication.

🔴 **Stay alert, your safety is important!**
        '''
    # Combine the base message with the scenario-specific content
    full_message = base_message + message_content

    try:
        # Send the WhatsApp message via Twilio API
        for i in phoneno:
            message = client.messages.create(
            body=full_message,
            from_=TWILIO_WHATSAPP_NUMBER,  # Twilio sandbox number
            to=f'whatsapp:+91{i}'  # Format: whatsapp:<recipient_number> for India
                )

        # Return the message SID (unique identifier for the message)
        # return f"Message sent successfully! SID: {message.sid}"

    except Exception as e:
        return f"Error sending message: {str(e)}"



last_alert_time = 0

def send_telegram_alert(frame, message):
    print("telegram alert started")
    global last_alert_time
    current_time = time.time()
    
    if current_time - last_alert_time >= 60:
        try:
            cv2.imwrite("alert.jpg", frame)
            with open("alert.jpg", 'rb') as photo:
                bot.send_photo(CHAT_ID, photo, caption=f"🚨 ALERT! 🚨\n{message}")
                send_smtp_email(emails,message,"alert.jpg")
                send_whatsapp_message(message)
                send_sms_twilio(message)
            bot.send_message(CHAT_ID, f"{message} Please take necessary precautions immediately!")
            last_alert_time = current_time
            print(f"Telegram alert sent: {message}")
        except Exception as e:
            print(f"Error sending Telegram alert: {e}")
    else:
        print("Waiting to send next alert. Time since last alert:", int(current_time - last_alert_time), "seconds")

def send_smtp_email(emails, msg, img_path):

    
    # Loop over the list of emails
    for i in emails:
        # Create a new email message for each recipient
        message = MIMEMultipart()
        message['From'] = from_email
        message['To'] = i
        message['Subject'] = "ALERT: Potential Danger Detected"
        
        # Conditional message based on the situation (for demo purposes)
        if "female_surrounded" in msg:
            html_content = '''
                <html>
                    <body>
                        <h3 style="color: red;">ALERT: Female Surrounded by Men</h3>
                        <p style="font-size: 20px;">There is a potential danger. A female is surrounded by multiple men. Immediate action is required.</p>
                        <p style="font-size: 18px; color: blue;">Please contact the authorities immediately:</p>
                        <ul style="font-size: 18px;">
                            <li>Police Station: +1 (800) 123-4567</li>
                            <li>Emergency Number: 112</li>
                        </ul>
                        <p style="font-size: 18px; font-weight: bold;">Steps to take:</p>
                        <ol style="font-size: 18px;">
                            <li>Try to stay calm and observe the surroundings.</li>
                            <li>Send this alert to others nearby.</li>
                            <li>If safe, contact the authorities immediately and provide the location.</li>
                        </ol>
                    </body>
                </html>
            '''

        elif "stressed" in msg:
            html_content = '''
        <html>
            <body>
                <h3 style="color: orange;">ALERT: Woman in Distress</h3>
                <p style="font-size: 20px;">A woman has been detected exhibiting signs of distress or fear. This is a possible emergency situation.</p>
                <p style="font-size: 18px; color: blue;">Please contact the authorities immediately:</p>
                <ul style="font-size: 18px;">
                    <li>Police Station: +1 (800) 123-4567</li>
                    <li>Emergency Number: 112</li>
                </ul>
                <p style="font-size: 18px; font-weight: bold;">Steps to take:</p>
                <ol style="font-size: 18px;">
                    <li>Ensure the safety of the woman and approach carefully.</li>
                    <li>Assess the situation for any further signs of danger or distress.</li>
                    <li>If needed, offer support and comfort while waiting for the authorities to arrive.</li>
                    <li>Do not escalate the situation unless absolutely necessary.</li>
                </ol>
            </body>
        </html>
    '''
        else:
            html_content = '''
                <html>
                    <body>
                        <h3 style="color: red;">ALERT: Female Alone at a Location</h3>
                        <p style="font-size: 20px;">A female has been detected alone at a location. Immediate action is required.</p>
                        <p style="font-size: 18px; color: blue;">Please contact the authorities:</p>
                        <ul style="font-size: 18px;">
                            <li>Police Station: +1 (800) 123-4567</li>
                            <li>Emergency Number: 112</li>
                        </ul>
                        <p style="font-size: 18px; font-weight: bold;">Steps to take:</p>
                        <ol style="font-size: 18px;">
                            <li>Ensure the area is safe and avoid confrontation.</li>
                            <li>Send this alert to others nearby.</li>
                            <li>Contact the authorities for assistance and report the situation.</li>
                        </ol>
                    </body>
                </html>
            '''
        
        # Attach the HTML content to the email
        message.attach(MIMEText(html_content, 'html'))
        
        # Attach the image (if provided)
        if img_path:
            with open(img_path, 'rb') as img_file:
                img = MIMEImage(img_file.read())
                img.add_header('Content-ID', '<image1>')  # Set a content ID for the image
                message.attach(img)

        # Send the email through the Gmail SMTP server
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()  # Secure the connection
                server.login(from_email, password)
                server.sendmail(from_email, i, message.as_string())
                print(f"Email sent to {i}")
        except Exception as e:
            print(f"Error sending email to {i}: {e}")