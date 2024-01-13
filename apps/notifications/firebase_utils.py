
import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate('eventicnut-firebase-adminsdk-np3oy-6a5e0c7489.json')
firebase_admin.initialize_app(cred)
