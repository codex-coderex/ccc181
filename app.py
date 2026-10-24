"""CCC181 Week 2: a "Hello, Flask" starter app.

Run it with:
    flask --app app run --debug
then open http://127.0.0.1:5000
"""
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from datetime import datetime
import re


app = Flask(__name__)
app.secret_key = "dev-only-change-me"

# Telecom services
SERVICES = [
    {"id": 1, "name": "SIM & eSIM Registration"},
    {"id": 2, "name": "SIM Card Replacement"},
    {"id": 3, "name": "Line Activation"},
    {"id": 4, "name": "Postpaid Mobile Applications"},
    {"id": 5, "name": "Home Fiber Broadband Applications"},
    {"id": 6, "name": "Bill Payment & Inquiry"},
    {"id": 7, "name": "Technical Support & Diagnostics"},
]

# Sample data for the demo. A real app would load this from a database later.
TICKETS = [
    {
        "number": 101,
        "name": "Jason Santos",
        "email": "jason.santos@example.com",
        "mobile_num": "01234567890",
        "service_id": 1,
        "assigned_to": "Counter 4",
        "status": "called",
        "joined_at": datetime(2026, 10, 26, 9, 5),
    },
    {
        "number": 102,
        "name": "May Abbott",
        "email": "may.abbott@example.com",
        "mobile_num": "01234567890",
        "service_id": 1,
        "assigned_to": "Counter 1",
        "status": "called",
        "joined_at": datetime(2026, 10, 26, 9, 12),
    },
    {
        "number": 103,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "mobile_num": "01234567890",
        "service_id": 5,
        "assigned_to": "pending",
        "status": "waiting",
        "joined_at": datetime(2026, 10, 26, 9, 15),
    },
]

@app.route("/")
def index():
    # render_template looks inside the templates/ folder and passes
    # keyword arguments to the template as variables.
    return render_template("index.html", name="Jason", tickets=TICKETS)


@app.get("/join")
def join_form():
    return render_template("join.html", services=SERVICES, form={})


@app.post("/join")
def join():
    form = request.form
    name = form.get("name", "").strip()
    mobile_num = form.get("mobile_num", "").strip()
    email = form.get("email", "").strip().lower()
    service_id = form.get("service_id", type=int)

    errors = {}
    if not name:
        errors["name"] = "Enter your name."

    digits = re.sub(r"[\s-]", "", mobile_num)  # allow spaces and dashes
    if not mobile_num:
        errors["mobile_num"] = "Enter your mobile number."
    elif not re.fullmatch(r"\+?\d{10,13}", digits):
        errors["mobile_num"] = "Enter a valid mobile number, like 09171234567."

    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        errors["email"] = "Enter a valid email address, or leave it blank."

    if service_id not in [s["id"] for s in SERVICES]:
        errors["service_id"] = "Choose a service."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return render_template("join.html", services=SERVICES, form=form, errors=errors), 400

    number = TICKETS[-1]["number"] + 1 if TICKETS else 1
    TICKETS.append({
        "number": number,
        "name": name,
        "email": email,
        "mobile_num": digits,
        "service_id": service_id,
        "assigned_to": "pending",
        "status": "waiting",
        "joined_at": datetime.now(),
    })
    flash(f"You joined the queue. Your ticket is #{number}.", "success")
    return redirect(url_for("ticket", ticket_id=number))


@app.get("/queue/<int:ticket_id>")
def ticket(ticket_id):
    t = next((t for t in TICKETS if t["number"] == ticket_id), None)
    if t is None:
        abort(404)
    ahead = [x for x in TICKETS
             if x["service_id"] == t["service_id"]
             and x["status"] == "waiting"
             and x["number"] < t["number"]]
    service = next(s for s in SERVICES if s["id"] == t["service_id"])
    return render_template("ticket.html", ticket=t, service=service,ahead=len(ahead), now=datetime.now())


@app.post("/queue/<int:ticket_id>/leave")
def leave(ticket_id):
    t = next((t for t in TICKETS if t["number"] == ticket_id), None)
    if t is None:
        abort(404)
    t["status"] = "left"
    flash("You left the queue.", "info")
    return redirect(url_for("index"))


@app.route("/staff")
def staff_dashboard():
    return "Staff dashboard coming soon"


@app.route("/hello")
def hello():
    # The plain-string version from the Routes slide.
    return "Hello, CCC181!"


if __name__ == "__main__":
    # Lets you also start the app with: python app.py
    app.run(debug=True)
