import pickle
import os
import base64
import googleapiclient.discovery
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow


def sendEmail(to, message):
    # # run the following code to get new token
    # # Get the path to the pickle file
    # # Get the user's home directory
    # SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    # home_dir = os.path.expanduser('~')
    # print(home_dir)
    #
    # # Recall that the credentials.json data is saved in your "Downloads" folder
    # json_path = os.path.join('credentials.json')
    # flow = InstalledAppFlow.from_client_secrets_file(json_path, SCOPES)
    # creds = flow.run_local_server(port=8000)
    # pickle_path = os.path.join('gmail.pickle')
    # with open(pickle_path, 'wb') as token:
    #     pickle.dump(creds, token)
    pickle_path = os.path.join('gmail.pickle')

    # Load our pickled credentials
    creds = pickle.load(open(pickle_path, 'rb'))

    # Build the service
    service = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)

    # Create a message
    my_email = 'test@gmail.com'
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Last Will'
    msg['From'] = f'{my_email}'
    msg['To'] = f'{to}'
    msgPlain = message
    # msgHtml = '<b>This is my first email!</b>'
    msg.attach(MIMEText(msgPlain, 'plain'))
    # msg.attach(MIMEText(msgHtml, 'html'))
    raw = base64.urlsafe_b64encode(msg.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}

    message1 = body
    message = (
        service.users().messages().send(
            userId="me", body=message1).execute())
    print('Message Id: %s' % message['id'])
# sendEmail("test@gmail.com", "hi")
