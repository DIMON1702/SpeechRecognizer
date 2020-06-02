from twilio.rest import Client
from credentials.creds import TWILIO_AUTH_TOKEN, TWILIO_SID, TWILIO_SMS_FROM_NUMBER

account_sid = TWILIO_SID
auth_token = TWILIO_AUTH_TOKEN
from_ = TWILIO_SMS_FROM_NUMBER

client = Client(account_sid, auth_token)

def send_sms(to, body):
    message = client.messages.create(
                              body=body,
                              from_=from_,
                              to=to
                          )
    return message

# send_sms('+1234567890', 'Test sms')