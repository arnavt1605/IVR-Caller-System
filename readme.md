
# Interactive Voice Response Calling System




## Table of Contents

1. [Abstract](#abstract)
2. [Objective](#objective)
3. [Literature Review](#literature-review)
4. [System Design and Architecture](#system-design-and-architecture)
5. [Results and Future Work](#results-and-future-work)
6. [Disclaimer](#disclaimer)

## Abstract
During emergency medical situations, especially in rural and urban hospitals, finding blood donors of a specific blood group can be time-critical.
This project automates the donor calling process using an IVR (Interactive Voice Response) system powered by Twilio and integrates a confirmation mechanism for donors via keypad input.
The system also stores donor details and call history using Supabase, enabling quick and reliable communication during emergencies.
## Objective
1. Automate donor notification to reduce response time.

2. Allow donors to confirm availability by pressing a digit on their phone.

3. Provide hospitals with a dashboard to track call status, confirmations, and donor history.

4. Maintain a centralized donor database for quick access.
## Literature Review
Example references:
- **Asterisk Open Source PBX**: Widely used for automated call handling and IVR in both corporate and healthcare sectors.  
  [Read more](https://www.asterisk.org/)
- **Twilio IVR for Nonprofits**: Used by NGOs to coordinate volunteers and blood donors during crises.  
  [Read more](https://www.twilio.org/)
- **NHS Blood and Transplant UK**: Utilizes automated calling & SMS to reach registered donors quickly.  
  [Read more](https://www.blood.co.uk/)
## System Design and Architecture

| Component       | Technology Used | Reason |
|-----------------|-----------------|--------|
| Backend         | Flask (Python)  | Lightweight, easy to integrate with APIs |
| Database        | Supabase        | Serverless, real-time updates |
| IVR & Calls     | Twilio          | Reliable and easy to integrate with Python|
| Frontend UI     | Bootstrap       | Quick UI development, responsive |
| Hosting         | Railway| Simple deployment for Flask apps |


## Results and Future Work
### 1. Current state: 
Prototype implementation present. No production testing done yet.

### 2. Future Work (non-exhaustive):

a) Add retries & backoff logic for failed calls.

b) Add multilingual IVR messages.

c) Add robust logging, monitoring, and unit/integration tests.

d) Build an official deploy pipeline and secrets management.
## Disclaimer

> A working version of this product is ready and is currently in the process of being deployed as an integrated package alongside other systems.  
> No claims are being made at this stage, as the system has not yet been tested in real-world scenarios and may still have certain issues.  
> The final product will not be a standalone solution but will be incorporated as part of a larger website with additional features.
