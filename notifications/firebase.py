import os
import firebase_admin
from firebase_admin import credentials, messaging

def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH', 'smartagrialert-firebase-adminsdk-fbsvc-ad796387ac.json'))
        firebase_admin.initialize_app(cred)