from dotenv import load_dotenv
from supabase import create_client
from flask import Flask, request, jsonify, Response
from twilio.rest import Client as TwilioClient
from concurrent.futures import ThreadPoolExecutor
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

# Global to track current request
recent_request = {}

@app.route('/call_donors', methods=['POST'])
def call_donors():
    global recent_request
    data = request.get_json()
    blood_group = data.get('blood_group')

    if not blood_group:
        return jsonify({"error": "blood_group is required"}), 400

    response = supabase.table('donors').select('*').eq('Blood_Group', blood_group).execute()
    donors = response.data

    if not donors:
        return jsonify({"status": f"No {blood_group} donors found"}), 404

    recent_request = {
        "blood_group": blood_group,
        "total_calls": len(donors),
        "answered": [],
    }

    def make_call(donor):
        phone = str(donor["Phone_Number"])
        if not phone.startswith("+"):
            phone = "+" + phone

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
            supabase.table("call_logs").insert({
                "phone_number": phone,
                "donor_name": donor["Name"],
                "call_sid": call.sid,
                "call_status": "initiated"
            }).execute()
        except Exception as e:
            print(f"[ERROR] Call failed for {phone}: {e}")

    with ThreadPoolExecutor(max_workers=5) as executor:
        for donor in donors:
            executor.submit(make_call, donor)

    return jsonify({"status": "Calls initiated", "count": len(donors)}), 200


@app.route('/voice', methods=['POST'])
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
    to_number = request.values.get('To', '')
    print(f"[PROCESS] Digit: {digit}, To: {to_number}")

    if digit == '1':
        donor_resp = supabase.table('donors').select('*').eq('Phone_Number', to_number).execute()
        donor_data = donor_resp.data

        if donor_data:
            donor = donor_data[0]
            supabase.table('confirmed_donors').insert({
                "Name": donor["Name"],
                "Age": donor["Age"],
                "Blood_Group": donor["Blood_Group"],
                "Phone_Number": int(donor["Phone_Number"]),
                "DOB": donor.get("DOB"),
                "Location": donor.get("Location")
            }).execute()
            print(f"[CONFIRMED] {donor['Name']} moved to confirmed_donors.")
        else:
            print(f"[WARNING] Donor not found for number: {to_number}")

    return Response("""<?xml version='1.0' encoding='UTF-8'?><Response><Say>Thank you for your response. Goodbye!</Say></Response>""", mimetype='text/xml')


@app.route('/status', methods=['POST'])
def status():
    from_number = request.values.get('To', '')
    call_status = request.values.get('CallStatus')
    print(f"[STATUS] Call to {from_number} ended with status: {call_status}")

    if call_status == 'completed':
        global recent_request
        if "answered" in recent_request and from_number not in recent_request["answered"]:
            recent_request["answered"].append(from_number)

    return '', 204


@app.route('/finalize_request', methods=['POST'])
def finalize_request():
    global recent_request

    confirmed = supabase.table("confirmed_donors").select("*").execute().data
    confirmed_list = [
        {
            "Name": d["Name"],
            "Age": d["Age"],
            "Blood_Group": d["Blood_Group"],
            "Phone_Number": d["Phone_Number"],
            "Location": d.get("Location"),
            "DOB": str(d.get("DOB"))
        }
        for d in confirmed
    ]

    supabase.table("history").insert({
        "blood_group": recent_request.get("blood_group"),
        "total_calls": recent_request.get("total_calls", 0),
        "answered_calls": len(recent_request.get("answered", [])),
        "confirmed_count": len(confirmed_list),
        "confirmed_donors": confirmed_list
    }).execute()

    supabase.table("confirmed_donors").delete().neq("Donor_ID", -1).execute()
    print("[FINALIZED] History saved and confirmed_donors table cleared.")
    return '', 204


if __name__ == '__main__':
    app.run(port=5000, debug=True)
