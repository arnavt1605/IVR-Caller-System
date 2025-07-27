from dotenv import load_dotenv
from supabase import create_client
from flask import Flask, request, jsonify, Response, render_template, redirect, session
from twilio.rest import Client as TwilioClient
from concurrent.futures import ThreadPoolExecutor
from math import ceil
from datetime import date, datetime
import pytz
import os

load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_ANON_KEY= os.getenv('SUPABASE_ANON_KEY')
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


# Home page
@app.route('/')
def home():
    return render_template('home.html')

# New donor registration form
@app.route('/register', methods=['GET'])
def show_register_form():
    return render_template('register.html')

# Donor registration form 
@app.route('/register_donor', methods=['POST'])
def register_donor():
    name = request.form.get('name')
    age = request.form.get('age')
    blood_group = request.form.get('blood_group')
    phone = request.form.get('phone')
    dob = request.form.get('dob')
    location = request.form.get('location')
    gender = request.form.get('gender')

    # Check all the required fields
    if not all([name, age, blood_group, phone, dob, location]):
        return "Missing fields", 400

    try:
        response = supabase.table('donors').insert({
            "Name": name,
            "Age": int(age),
            "Blood_Group": blood_group,
            "Phone_Number": phone,
            "DOB": dob,
            "Location": location,
            "Gender" : gender
        }).execute()

        print(f"[REGISTERED] {name} added to donors.")
        return redirect('/thanks')  # Redirect to thank you page after registration

    except Exception as e:
        print(f"[ERROR] Failed to register donor: {e}")
        return "Something went wrong", 500
    
# Thank you page
@app.route('/thanks')
def thanks():
    user_agent = request.user_agent.string.lower()

    if "mobile" in user_agent or "android" in user_agent or "iphone" in user_agent:
        return render_template("thanks_mobile.html")
    else:
        return render_template("thanks_desktop.html")

# Update: auth logic integrated
@app.route('/login')
def login():
    return render_template('login.html', supabase_url=SUPABASE_URL, supabase_anon_key=SUPABASE_ANON_KEY)


# Set password logic for new users - Invite sent through mail
@app.route('/set-password')
def set_password():
    return render_template('set_password.html', supabase_url=SUPABASE_URL, supabase_anon_key=SUPABASE_ANON_KEY)

# Reset Password logic for existing users
@app.route('/reset-password')
def reset_password():
    return render_template('reset_password.html', supabase_url=SUPABASE_URL, supabase_anon_key=SUPABASE_ANON_KEY)

#View the admin dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


#To allow admin to view list of all donors in the database
@app.route('/donors')
def view_donors():
    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page

    # Get all donors (paginated)
    all_donors = supabase.table("donors").select("*").order("Donor_ID").range(offset, offset + per_page - 1).execute().data

    for donor in all_donors:
        last_called_utc = donor.get("last_called_at")
        if last_called_utc:
            try:
                utc_dt = datetime.fromisoformat(last_called_utc.replace('Z', '+00:00'))  # Convert from UTC
                ist_dt = utc_dt.astimezone(pytz.timezone('Asia/Kolkata'))
                donor["last_called_at_ist"] = ist_dt.strftime("%d-%m-%Y %I:%M %p")
            except Exception:
                donor["last_called_at_ist"] = "Invalid"
        else:
            donor["last_called_at_ist"] = "Never"

    # Get total count of donors
    total = supabase.table("donors").select("Donor_ID", count='exact').execute().count or 0
    total_pages = ceil(total / per_page)

    # Get blood group counts
    blood_group_counts = {}
    all_data = supabase.table("donors").select("Blood_Group").execute().data
    for d in all_data:
        bg = d["Blood_Group"]
        blood_group_counts[bg] = blood_group_counts.get(bg, 0) + 1

    return render_template("donors.html", donors=all_donors, page=page, total_pages=total_pages, total_donors=total, blood_group_counts=blood_group_counts)

#View previous history of blood group requested
@app.route('/history')
def view_history():
    result = supabase.table("history").select("*").order("id", desc=True).execute()
    history_data = result.data

    return render_template("history.html", history=history_data)

# View the donor info of any registered donor
@app.route('/donor_info', methods=['GET', 'POST'])
def donor_info():
    donor = None
    total_calls = 0
    searched = False

    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        searched = True

        # Step 1: Find donor by phone number
        donor_response = supabase.table("donors").select("*").eq("Phone_Number", phone_number).execute()
        if donor_response.data:
            donor = donor_response.data[0]
            call_log_response = supabase.table("call_logs").select("id").eq("donor_id", donor["Donor_ID"]).execute()
            total_calls = len(call_log_response.data)

    return render_template("donor_info.html", donor=donor, total_calls=total_calls, searched=searched)

#Main logic that will initiate the calls 
@app.route('/call_donors', methods=['POST'])
def call_donors():
    data = request.get_json()
    blood_group = data.get('blood_group')
    if not blood_group:
        return jsonify({"error": "blood_group is required"}), 400

    response = supabase.table('donors').select('*').eq('Blood_Group', blood_group).execute()
    all_donors = response.data
    if not all_donors:
        return jsonify({"status": f"No donors with blood group {blood_group} found"}), 404

    # Sorting donors here: never-called first, then by oldest last_called date
    def donor_sort_key(donor):
        if donor['last_called'] is None:
            return (False, datetime.min.isoformat())  # Top priority
        else:
            return (True, donor['last_called'])  # Later calls

    eligible_donors = sorted(all_donors, key=donor_sort_key)

    eligible_donors = eligible_donors[:10]  #Can be changed later as per our needs

    if not eligible_donors:
        return jsonify({"status": f"No eligible {blood_group} donors to call"}), 200

    global recent_request
    recent_request = {
        "blood_group": blood_group,
        "total_calls": len(eligible_donors),
        "answered": [],
    }

    
    def make_call(donor):
        phone = donor['Phone_Number']  
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
            supabase.table("donors").update({
                "last_called": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat()
            }).eq("Phone_Number", phone).execute()

            # Insert call log into the call_logs table
            supabase.table("call_logs").insert({
                "donor_id": donor["id"],
                "phone_number": phone,
                "call_sid": call.sid,
                "call_status": "initiated",
                "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat()
            }).execute()

        except Exception as e:
            print(f"[ERROR] Call failed for {phone}: {e}")

    with ThreadPoolExecutor(max_workers=5) as executor:
        for donor in eligible_donors:
            executor.submit(make_call, donor)

    return jsonify({"status": "Calls initiated", "count": len(eligible_donors)}), 200



# Message that will play when call is received  # NEED TO UPDATE THE URL HERE !!
@app.route('/voice', methods=['POST'])
def voice():
    print("[VOICE] /voice triggered")
    gather_url = f"{CALLBACK_URL}/process"
    response = f"""<?xml version='1.0' encoding='UTF-8'?>
    <Response>  
        <Gather numDigits="1" action="/process" method="POST">
            <Play>https://ivr-caller-system.onrender.com//static/audio/recording.mp3</Play>
        </Gather>
    </Response>
"""
    return Response(response, mimetype='text/xml')

#View donor logs/info needs to be inserted here



#Logic for handling the input by the user
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
                "Gender": donor.get("Gender"),
                "Blood_Group": donor["Blood_Group"],
                "Phone_Number": int(donor["Phone_Number"]),
                "DOB": donor.get("DOB"),
                "Location": donor.get("Location")
            }).execute()
            print(f"[CONFIRMED] {donor['Name']} moved to confirmed_donors.")
        else:
            print(f"[WARNING] Donor not found for number: {to_number}")

    return Response("""<?xml version='1.0' encoding='UTF-8'?><Response><Say>Thank you for your response. Goodbye!</Say></Response>""", mimetype='text/xml')


#Updating status of the call
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


#Logic for requesting sepcific blood groups and processing all of it

@app.route('/request')
def request_page():
    return render_template("request.html")

@app.route('/supabase-config')
def supabase_config():
    return jsonify({
        "url": os.getenv("SUPABASE_URL"),
        "anon": os.getenv("SUPABASE_ANON_KEY")  
    })

@app.route('/finalize_request', methods=['POST'])
def finalize_request():
    global recent_request

    confirmed = supabase.table("confirmed_donors").select("*").execute().data
    confirmed_list = [
        {
            "Name": d["Name"],
            "Age": d["Age"],
            "Gender": d.get("Gender"),
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
