from flask import Flask, request, jsonify, render_template, url_for, redirect
import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request 
from flask import Flask, render_template, send_from_directory
from flask_bootstrap import Bootstrap
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

CLIENT_SECRET = 'credentials.json'
SCOPE = ['https://www.googleapis.com/auth/gmail.send',
     'https://www.googleapis.com/auth/userinfo.email',
     'https://www.googleapis.com/auth/userinfo.profile',]
STORAGE = Storage('credentials.storage')

app = Flask(__name__, static_folder='static')
bootstrap = Bootstrap(app)


# Define the scopes for Gmail API access
# SCOPES = ['https://www.googleapis.com/auth/gmail.send',
  #   'https://www.googleapis.com/auth/userinfo.email',
    # 'https://www.googleapis.com/auth/userinfo.profile',]

# Start the OAuth flow to retrieve credentials
def authorize_credentials():
# Fetch credentials from storage
    credentials = STORAGE.get()
# If the credentials doesn't exist in the storage location then run the flow
    if credentials is None or credentials.invalid:
        flow = flow_from_clientsecrets(CLIENT_SECRET, scope=SCOPE)
        http = httplib2.Http()
        credentials = run_flow(flow, STORAGE, http=http)
    return credentials

def get_user_info(credentials):
  """Send a request to the UserInfo API to retrieve the user's information.

  Args:
    credentials: oauth2client.client.OAuth2Credentials instance to authorize the
                 request.
  Returns:
    User information as a dict.
  """
  user_info_service = build(
      serviceName='oauth2', version='v2',
      http=credentials.authorize(httplib2.Http()))
  user_info = None
  try:
    user_info = user_info_service.userinfo().get().execute()
  except Exception as e:
        return "Error during get_user_info: " + str(e)



def generate_right_to_forget_letter(name, company):
    letter = f"Dear {company},\n\nI am writing to exercise my right to be forgotten under applicable data protection laws. As a data subject, I request the deletion of all my personal information held by your company. This includes any data related to my name, contact information, and any other identifiable information.\n\nPlease confirm in writing that mypersonal information has been deleted from your records within the legally required timeframe.\n\nThank you for your prompt attention to this matter.\n\nSincerely,\n{name}"
    return letter

@app.route('/', methods=['GET', 'POST'])
def form():
    return render_template('index.html', script_url=url_for('static', filename='script.js'))

@app.route('/favicon.ico')
def favicon():
    return '', 204


@app.route('/forget', methods=['POST'])
def forget():
    if request.method == 'POST':
        company = request.form['company']
        email = request.form['email']
        sender_name = request.form['sender_name']
        sender_email= request.form['sender_email']

    try:
       # Get the ID token sent by the Google Sign-In callback
         # id_token = request.form['id_token']
        #  creds = Credentials.from_authorized_user_info(id_token=id_token, scopes=SCOPES)
        print("5")
        #service = get_gmail_service()
        creds=authorize_credentials()
         #user_info = get_user_info(creds)
         #sender_email = user_info.get('email')
        
        service=build('gmail', 'v1', credentials=creds)

        
        print("35")
          #Get the authenticated user's email address
       
        #sender_name='Dale Poulter'
        print("37")
        #letter = generate_right_to_forget_letter(sender_name, company)
        letter=generate_right_to_forget_letter(sender_name,company)

        print("40")
        message = (service.users().messages().send(
            userId='me',
            body={
                'raw': base64.urlsafe_b64encode(
                    f"From: {sender_email}\n"
                    f"To: {email}\n"
                    f"Subject: Right to Forget Request\n\n"
                    f"{letter}"
                    .encode("utf-8")
                ).decode("utf-8")
            }
        ).execute())

        # Display a popup with "Email sent successfully" message
        return render_template('popup.html', message='Email sent successfully!')

    except Exception as e:
        # Display a popup with "Error sending email" message
        return render_template('popup.html', message=f'Error sending email: {str(e)}')


if __name__ == '__main__':
    app.run()
