from twilio.rest import Client
import os
from dotenv import load_dotenv
load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

client.messages.create(
    from_='whatsapp:+14155238886',  
    to='whatsapp:+919284834031',    
    body='Hello Hello 1 2 3 1 2 3 testing testing'
)
