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

