# Script that runs weekly/biweekly
# Updates the age field in donors table by calculating it from DOB

from datetime import date, datetime
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def calculate_age(dob_str):
    dob = datetime.strptime(dob_str, "%y-%m-%d").date()
    today= date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def update_all_donor_ages():
    donors = supabase.table("donors").select("Donor_ID", "DOB").execute().data

    for donor in donors:
        dob = donor.get("DOB")
        if not dob:
            continue
        new_age = calculate_age(dob)
        supabase.table("donors").update({"Age": new_age}).eq("Donor_ID", donor["Donor_ID"]).execute()
        print(f"Updated age for Donor_ID {donor['Donor_ID']} to {new_age}")

if __name__ == "__main__":
    update_all_donor_ages()