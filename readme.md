### What works till now
1. Call is getting initiated
2. donors and confirmed_donors table is also getting updated 
3. Http request to /call_bplus_donors is initiating the call

### How it works
1. Run app.py
2. Run ngrok server
3. Copy ngrok url to .env file
4. Close app.py and run again
5. Use postman to send http request to /call_bplus_donors
