from http.client import HTTPSConnection
from credentials.creds import TEXTME_USERNAME, TEXTME_PASSWORD


username = TEXTME_USERNAME
password = TEXTME_PASSWORD


def send_sms(username, password, source, recipient, message):
    """
    Function sends message from source phone number to recipient phone number\n
    username - Required element. The username of the account by which you are recognized in the system.\n
    password - Required element.The password to your user account.\n
    source - Required element. The phone number from which you wish to send the SMS message.\n
    recipient - Required element. phone number to which the SMS, must be formatted : 5xxxxxxx or 05xxxxxxx\n
    message - Required element. Contains the message to be sent to the destinations.
    """

    conn = HTTPSConnection('my.textme.co.il')
    payload = f"""\
<?xml version='1.0' encoding='UTF-8'?>
    <sms>
        <user>
            <username>{username}</username>
            <password>{password}</password>
        </user>
        <source>{source}</source>
        <destinations>
            <phone>{recipient}</phone>
        </destinations>
        <message>{message}</message>
    </sms>\
"""

    headers = {
        'Content-Type': "application/xml",
    }

    conn.request("POST", "/api", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")


def balance(username, password):
    conn = HTTPSConnection("my.textme.co.il")

    payload = f"""\
<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<balance>
    <user>
        <username>{username}</username>
        <password>{password}</password>
    </user>
</balance>\
"""

    headers = {
        'Content-Type': "application/xml",
    }

    # print(payload)
    conn.request("POST", "/api", payload, headers)

    res = conn.getresponse()
    data = res.read()

    return data.decode("utf-8")


if __name__ == "__main__":
    print(balance(username, password))
    # print(send_sms(username, password, '0520000000', '0521111111', 'Test message'))
