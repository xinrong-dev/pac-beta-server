import firebase_admin
import os
from django.conf import settings
from firebase_admin import credentials

default_app = None
if not firebase_admin._apps:
    cred = credentials.Certificate(os.path.join(
        settings.BASE_DIR, 'accounts/firebase/{}'.format(settings.FIREBASE_ACCOUNT_KEY)))
    default_app = firebase_admin.initialize_app(cred)
