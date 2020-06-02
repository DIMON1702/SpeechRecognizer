from twilio.rest import Client
import json
from credentials.creds import TWILIO_AUTH_TOKEN, TWILIO_SID, TWILIO_WHATSAPP_FROM_NUMBER

account_sid = TWILIO_SID
auth_token = TWILIO_AUTH_TOKEN
from_ = TWILIO_WHATSAPP_FROM_NUMBER

client = Client(account_sid, auth_token)

def send_whatsapp_message(to, body):
    message = client.messages.create(
                              body=body,
                              from_=f'whatsapp:{from_}',
                              to=f'whatsapp:{to}'
                          )
    return message

# send_whatsapp_message('+1234567890', 'Test whatsapp message')