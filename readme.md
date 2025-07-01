### What works till now
1. Call is getting initiated
2. Added two extra tables, call_logs and history, in addition to donors and confirmed donors
3. Working on the frontend
4. General route created for requesting calls to a specific blood group

### How it works
1. Run app.py
2. Run ngrok server
3. Copy ngrok url to .env file
4. Close app.py and run again
5. Use postman to send http request to /call_bplus_donors (post request)
