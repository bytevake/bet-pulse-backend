import africastalking
import requests

class SendMail:
    africastalking_url = "https://api.africastalking.com/version1/messaging"

    # Request.POST()

    def __init__(self, username, api_key, sender):
        africastalking.initialize(username, api_key)
        self.sms = africastalking.SMS
        self.sender = sender
        self.username = username

    def send(self, message, recipients):
        """
        Will Be Used to send messages to users
        """
        # Set the numbers in international format
        # Set your message
        # Set your shortCode or senderId
        try:
            response = self.sms.send(message, recipients, self.sender)
            print (response)
        except Exception as e:
            print (f'Houston, we have a problem: {e}')
    
    def live_send(self, message, recipients):
        """
        Will be used to send messages to users
        """
        data = {
            "username": self.username,
            "to": recipients,
            "message": message,
            "from": self.sender,
        }

        try:
            send_message = requests.post(url=self.africastalking_url, data=data)
            print(send_message.status_code, send_message.text)
        except Exception as e:
            raise e
            print(e)
