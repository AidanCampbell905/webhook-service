### 02/18\2026

## 1.5 Hours

- Created the base files and folders in beginning my project, as well as my app.py file.'

### 02/20/2026

## 1 hour

- Created my database.py using sqlite

### 02/24/2026

## 1 hour

- Made the dashboard.html file to view webhook events.

### 02/24/2026

## 1.5 hour

- Made changes to app.py and tested the project using : curl.exe -X POST http://127.0.0.1:5000/webhook ^
  -H "Content-Type: application/json" ^
  -d "{\"event_name\": \"push\", \"user\": \"aidan\"}"

  - Viewed the stored event on 127.0.0.1:5000/dashboard

  ### 02/26/2026

  ## 2.5 hours

  - Set up ngrok and succesfully tested my webhooks service. I had to set up ngrok to avoid the security restrictions in the lab enviornment/GitLab enviornment. I Created new tables so that I am able to use and view the service on multiple GitLab projects with ease.

  ### 02/27/2026

  ## 4 hours

  - Added a secret token that GitLab can accept. Added paging to the dashboard as well as a way to order the events from oldest to newest and vice-versa

  - Connected my GitHub to Render.com, so that I don't need to run the app locally. (Had to push to GitHub to bypass GitLab parameters.)