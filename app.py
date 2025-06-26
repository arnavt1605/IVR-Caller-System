from dotenv import load_dotenv
from supabase import create_client, Client
from flask import Flask, render_template, request, redirect, session, url_for
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app= Flask(__name__)
app.secret_key = SECRET_KEY

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            return redirect(url_for('login'))
        else:
            return "Registration failed", 400
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.session:
            session['user'] = response.user.id
            return redirect(url_for('dashboard'))
        else:
            return "Login failed", 400
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Login required decorator
from functools import wraps
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Protected dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    # Example: fetch all confirmed donors
    confirmed_donors = supabase.table('confirmed_donors').select('*').execute().data
    return render_template('dashboard.html', donors=confirmed_donors)

# Example: fetch donors by blood group (API endpoint)
@app.route('/donors')
@login_required
def get_donors():
    blood_group = request.args.get('blood_group')
    if not blood_group:
        return {"error": "blood_group is required"}, 400
    response = supabase.table("donors").select("*").eq("blood group", blood_group).execute()
    return response.data

if __name__ == '__main__':
    app.run(debug=True)