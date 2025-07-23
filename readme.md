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
1. Get all donors of the selected blood group.
2. Prioritize never-called donors first
3. Avoid recently called donors, but only if there are enough others available
4. Log the reason for selection (call_priority) in call_logs
5. Shuffle the eligible donors list to avoid repeat patterns
6. Track how many times each donor has been called and limit if needed

### Removed:
1. Removed cron job script temporarily.


