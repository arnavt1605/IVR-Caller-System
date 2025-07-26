### Updated Features
1. Added Gender and Registered_At columns to donors table.
2. Updated frontend `register.html` with the new columns.
3. Updated backend for the registration route to handle new column values.
4. Added Gender row in confirmed_donors table.
5. Updated `history.html` with the new columns.
6. Updated app.py routes (all).
7. Updated `donors.html` and `request.html`.
8. Added "I don't know" option in blood group selection in `register.html`.
9. Save Contact button added in `thanks.html`.
10. Play human voice when called instead of automated voice.
11. Added reset password code in `reset_password.html`.
12. Reset password logic working successfully.
13. Added last_called_at in donors table.
14. Added the last_called_at columns in `donors.html` as well.

### Files needing updates:
1. `donors.html`
2. `register.html`
3. `history.html`
4. `request.html`
5. `app.py` -> `/register_donor` , `/process` , `/finalize_request`

### Make Changes:
1. Calling logic needs to be changed (WIP).
2. Integrate whatsapp messaging system along with confirmation.
3. Upload the cron job file on render.
4. Add deployment URL to the `/voice` route.

5. Let admin see info about donor from call_logs


### New Calling Logic Idea:
1. Get all donors of the selected blood group from the donors table.
2. Prioritize never-called donors first, whose last called date is NULL then go over the remaining entries in ascending order of last called date
3. Update the last called date to the current called date after calling
4. Track how many times each donor has been called and limit if needed

### Calling logic implemented:
1. Prioritize never-called donors first, then by oldest last_called.
2. Update last_called after calling.
3. Insert into call_logs table correctly.
4. Limit to top 10 eligible donors (you can change this if needed).

### Removed:
1. Removed cron job script temporarily.


