from dotenv import load_dotenv
from supabase import create_client
from flask import Flask, request, jsonify, Response
from twilio.rest import Client as TwilioClient
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

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


# Track request summary in memory
recent_request = {
    "blood_group": None,
    "total_calls": 0,
    "answered": set(),
    "confirmed": []
}


# Function to call one donor
def call_donor(donor, blood_group):
    phone = str(donor['Phone_Number'])
    if not phone.startswith('+'):
        phone = '+' + phone
    try:
        call = twilio_client.calls.create(
            url=f"{CALLBACK_URL}/voice",
            to=phone,
            from_=TWILIO_PHONE_NUMBER,
            status_callback=f"{CALLBACK_URL}/status",
            status_callback_event=["completed"],
            status_callback_method="POST"
        )
        print(f"[CALL] {donor['Name']} ({blood_group}) at {phone}: {call.sid}")
    except Exception as e:
        print(f"[ERROR] Failed to call {phone}: {e}")


@app.route('/call_donors', methods=['POST'])
def call_donors():
    data = request.get_json()
    blood_group = data.get('blood_group')

    if not blood_group:
        return jsonify({'error': 'Blood group is required'}), 400

    response = supabase.table('donors').select('*').eq('Blood_Group', blood_group).execute()
    donors = response.data

    if not donors:
        return jsonify({"status": f"No donors found for blood group {blood_group}"}), 404

    # Initialize tracker
    recent_request["blood_group"] = blood_group
    recent_request["total_calls"] = len(donors)
    recent_request["answered"] = set()
    recent_request["confirmed"] = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        for donor in donors:
            executor.submit(call_donor, donor, blood_group)

    return jsonify({"status": f"Calls initiated to {len(donors)} donors with blood group {blood_group}"}), 200


@app.route('/voice', methods=['POST', 'GET'])
def voice():
    print("[VOICE] /voice triggered")
    gather_url = f"{CALLBACK_URL}/process"
    response = f"""<?xml version='1.0' encoding='UTF-8'?>
    <Response>
        <Say>This is an urgent request for blood donation. If you are available to donate, press 1. Otherwise, you may hang up.</Say>
        <Gather action="{gather_url}" method="POST" numDigits="1">
            <Say>Please press 1 to confirm your availability.</Say>
        </Gather>
        <Say>No input received. Goodbye!</Say>
    </Response>"""
    return Response(response, mimetype='text/xml')


@app.route('/process', methods=['POST'])
def process():
    digit = request.values.get('Digits', '')
    to_number = request.values.get('To', '')  # Donor's number

    print(f"[PROCESS] Digit: {digit}, To: {to_number}")

    if digit != '1':
        return Response("""<?xml version='1.0' encoding='UTF-8'?>
            <Response>
                <Say>No confirmation received. Goodbye!</Say>
            </Response>""", mimetype='text/xml')

    donor_resp = supabase.table('donors').select('*').eq('Phone_Number', to_number).execute()
    donor_data = donor_resp.data

    if not donor_data:
        print("[ERROR] Donor not found:", to_number)
        return Response("""<?xml version='1.0' encoding='UTF-8'?>
            <Response>
                <Say>Could not find your record. Goodbye!</Say>
            </Response>""", mimetype='text/xml')

    donor = donor_data[0]

    # Insert into confirmed_donors
    supabase.table('confirmed_donors').insert({
        'Name': donor['Name'],
        'Age': donor['Age'],
        'Blood_Group': donor['Blood_Group'],
        'Phone_Number': int(str(donor['Phone_Number']).replace('+', '')),
        'DOB': donor['DOB'],
        'Location': donor['Location']
    }).execute()


    recent_request["confirmed"].append(donor)

    print(f"[CONFIRMED] {donor['Name']} moved to confirmed_donors.")

    return Response("""<?xml version='1.0' encoding='UTF-8'?>
        <Response>
            <Say>Thank you for confirming. We appreciate your help. Goodbye!</Say>
        </Response>""", mimetype='text/xml')


@app.route('/status', methods=['POST'])
def status_callback():
    call_status = request.form.get('CallStatus', '')
    call_sid = request.form.get('CallSid', '')
    to_number = request.form.get('To', '')

    print(f"[STATUS] Call to {to_number} ended with status: {call_status}")

    donor_resp = supabase.table('donors').select('Name').eq('Phone_Number', to_number).execute()
    name = donor_resp.data[0]['Name'] if donor_resp.data else None

    supabase.table('call_logs').insert({
        'phone_number': to_number,
        'donor_name': name,
        'call_status': call_status,
        'call_sid': call_sid
    }).execute()

    if call_status == 'completed':
        recent_request["answered"].add(to_number)

    return ('', 204)


@app.route('/finalize_request', methods=['POST'])
def finalize_request():
    confirmed_list = [{
        "name": d["Name"],
        "phone": d["Phone_Number"],
        "location": d["Location"]
    } for d in recent_request["confirmed"]]

    supabase.table("history").insert({
        "blood_group": recent_request["blood_group"],
        "total_calls": recent_request["total_calls"],
        "answered_calls": len(recent_request["answered"]),
        "confirmed_count": len(confirmed_list),
        "confirmed_donors": confirmed_list
    }).execute()


    # Clear confirmed_donors after saving
    supabase.table("confirmed_donors").delete().neq("Donor_ID", -1).execute()
    print("[FINALIZED] History saved and confirmed_donors table cleared.")

    return jsonify({"status": "Request history saved."}), 200


if __name__ == '__main__':
    app.run(port=5000, debug=True)
