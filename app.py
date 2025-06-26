from dotenv import load_dotenv
from supabase import create_client
from flask import Flask, request, jsonify, Response
from twilio.rest import Client as TwilioClient
import os

load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Twilio setup
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_FROM_NUMBER')
CALLBACK_URL = os.getenv('CALLBACK_URL')

twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key')

@app.route('/call_bplus_donors', methods=['POST'])
def call_bplus_donors():
    response = supabase.table('donors').select('*').eq('Blood_Group', 'B+').execute()
    donors = response.data
    if not donors:
        return jsonify({"status": "no B+ donors found"}), 404

    for donor in donors:
        phone = str(donor['Phone_Number'])
        
        if not phone.startswith('+'):
            phone = '+' + phone
        try:
            call = twilio_client.calls.create(
                url=f"{CALLBACK_URL}/voice",
                to=phone,
                from_=TWILIO_PHONE_NUMBER
            )
            print(f"Call started for {donor['Name']} at {phone}: {call.sid}")
        except Exception as e:
            print(f"Failed to call {phone}: {e}")

    return jsonify({"status": "calls initiated", "count": len(donors)}), 200

@app.route('/voice', methods=['POST', 'GET'])
def voice():
    response = """<?xml version='1.0' encoding='UTF-8'?>
    <Response>
        <Say>This is an urgent request for blood donation. If you are available to donate, press 1. Otherwise, you may hang up.</Say>
        <Gather action="/process" method="POST" numDigits="1">
            <Say>Please press 1 to confirm your availability.</Say>
        </Gather>
        <Say>No input received. Goodbye!</Say>
    </Response>"""
    return Response(response, mimetype='text/xml')

@app.route('/process', methods=['POST', 'GET'])
def process():
    digit = request.values.get('Digits', '')
    from_number = request.values.get('From', '')

    # Remove '+' if your DB stores numbers without '+'
    phone_number = from_number.lstrip('+')

    if digit == '1':
        donor_resp = supabase.table('donors').select('*').eq('Phone_Number', phone_number).execute()
        donor = donor_resp.data[0] if donor_resp.data else None

        if donor:
            insert_resp = supabase.table('confirmed_donors').insert({
                'Name': donor['Name'],
                'Age': donor['Age'],
                'Blood_Group': donor['Blood_Group'],
                'Phone_Number': donor['Phone_Number'],
                'DOB': donor['DOB'],
                'Location': donor['Location']
            }).execute()
            if hasattr(insert_resp, 'error') and insert_resp.error:
                print(f"Insert error: {insert_resp.error}")
            supabase.table('donors').delete().eq('Donor_ID', donor['Donor_ID']).execute()
            response = """<?xml version='1.0' encoding='UTF-8'?>
            <Response>
                <Say>Thank you for confirming. We appreciate your help. Goodbye!</Say>
            </Response>"""
        else:
            response = """<?xml version='1.0' encoding='UTF-8'?>
            <Response>
                <Say>Could not find your record. Goodbye!</Say>
            </Response>"""
    else:
        response = """<?xml version='1.0' encoding='UTF-8'?>
        <Response>
            <Say>No confirmation received. Goodbye!</Say>
        </Response>"""
    return Response(response, mimetype='text/xml')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
