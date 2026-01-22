# notifications/firebase.py
import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("smartagrialert-firebase-adminsdk-fbsvc-ad796387ac.json")
firebase_admin.initialize_app(cred)
