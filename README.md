# SignalQ: Stay connected while you wait

SignalQ is a queue management system for a telecom service center. Customers get a ticket for services like SIM registration, SIM replacement, line activation, postpaid and fiber applications, bill payment and technical support. They can check their place in line from any device. Staff see the waiting list, call the next ticket, and mark customers as served or no-show.

## How to run

```bash
# create the environment (once)
python -m venv .venv

# activate it (every new terminal)
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS/Linux

# install the packages
pip install -r requirements.txt

# run the app
flask --app app run --debug
```

Open http://127.0.0.1:5000. Some systems use `python3` or `py` instead of `python`.

To test on a phone on the same Wi-Fi, run `flask --app app run --debug --host 0.0.0.0` and open your laptop's IP address on the phone.

## Screens

| Screen | URL | Who uses it |
| --- | --- | --- |
| Home | `/` | Person waiting |
| Join the queue | `/join` | Person waiting |
| My place | `/queue/<ticket number>` | Person waiting |
| Staff dashboard | `/staff` | Staff member |

**Note:** the staff dashboard is open to anyone for now. Staff login comes in a later week.

## Routes

| URL | Method | What it does |
| --- | --- | --- |
| `/` | GET | Home page |
| `/join` | GET | Shows the join form |
| `/join` | POST | Validates the form and creates a ticket |
| `/queue/<ticket_id>` | GET | My place page for one ticket |
| `/queue/<ticket_id>/leave` | POST | Marks the ticket as left |
| `/queue/<ticket_id>/status.json` | GET | Status and position as JSON, used for the 10-second refresh |
| `/staff` | GET | Staff dashboard, with service filter and search |
| `/staff/call-next` | POST | Calls the first waiting ticket |
| `/staff/tickets/<ticket_id>/<action>` | POST | Call, serve or no-show a ticket |

## Project structure

```
├── app.py              # routes and sample data
├── requirements.txt    # packages
├── templates/
│   ├── base.html       # shared layout and navigation
│   ├── index.html      # home page
│   ├── join.html       # join the queue form
│   ├── ticket.html     # My place
│   └── staff.html      # staff dashboard
├── static/
│   ├── css/style.css
│   └── js/main.js
└── docs/
    ├── week1/
    └── week3/          # personas, wireframes, feedback, accessibility, usability test, report
```

## Notes

- Tickets are stored in a Python list, so they reset when the server restarts. A database comes in Week 4.
- Ticket statuses are `waiting`, `called`, `served`, `left` and `no-show`.