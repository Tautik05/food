import os
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv

load_dotenv()  # Loads environment variables from .env


# Path to your Firebase service account key file
cred = credentials.Certificate(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'firebase_credentials.json'))

firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv('FIREBASE_DATABASE_URL')
})




from firebase_admin import db


def update_firebase_order(partner_id, order_details):
    try:
        order_ref = db.reference(f"orders/{partner_id}")
        order_ref.set(order_details)  # Use .set to write the order details
        print(f"Order updated in Firebase for partner ID {partner_id}.")
    except Exception as e:
        print(f"Error updating Firebase: {e}")



def send_location_to_firebase(partner_id, latitude, longitude):
    try:
        print(f"Sending location to Firebase: {partner_id}, {latitude}, {longitude}")  # Debugging line
        location_ref = db.reference(f"locations/{partner_id}")
        location_data = {
            "latitude": latitude,
            "longitude": longitude,
        }
        location_ref.set(location_data)
        print(f"Location updated in Firebase for partner ID {partner_id}.")
    except Exception as e:
        print(f"Error updating Firebase location: {e}")

