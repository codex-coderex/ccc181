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
        "assigned_to": "Counter 1",
        "status": "called",
        "joined_at": datetime(2026, 10, 26, 2, 5),
    },
    {
        "number": 102,
        "name": "May Abbott",
        "email": "may.abbott@example.com",
        "mobile_num": "01234567890",
        "service_id": 1,
        "assigned_to": "pending",
        "status": "waiting",
        "joined_at": datetime(2026, 10, 26, 2, 12),
    },
    {
        "number": 103,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "mobile_num": "01234567890",
        "service_id": 5,
        "assigned_to": "pending",
        "status": "waiting",
        "joined_at": datetime(2026, 10, 26, 2, 15),
    },
    {
        "number": 104,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "mobile_num": "01234567890",
        "service_id": 6,
        "assigned_to": "pending",
        "status": "waiting",
        "joined_at": datetime(2026, 10, 26, 2, 15),
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

# queue join form submission 

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
             if x["status"] == "waiting"
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


# staff dashboard and actions

@app.template_filter("minutes_since")
def minutes_since(dt):
    return int((datetime.now() - dt).total_seconds() // 60)


@app.get("/staff")
def staff_dashboard():
    service_id = request.args.get("service_id", type=int)
    q = request.args.get("q", "").strip().lower()

    waiting = [t for t in TICKETS if t["status"] == "waiting"]
    total_waiting = len(waiting)
    counts = {s["id"]: len([t for t in waiting if t["service_id"] == s["id"]])
              for s in SERVICES}

    if service_id:
        waiting = [t for t in waiting if t["service_id"] == service_id]
    if q:
        waiting = [t for t in waiting
                   if q in t["name"].lower() or q in str(t["number"])]

    serving = next((t for t in TICKETS if t["status"] == "called"), None)
    names = {s["id"]: s["name"] for s in SERVICES}
    done = next((t for t in TICKETS if t["number"] == request.args.get("done", type=int)), None)
    return render_template("staff.html", serving=serving, done=done, waiting=waiting,
                       total_waiting=total_waiting, services=SERVICES,
                       names=names, counts=counts, selected=service_id, q=q)


@app.post("/staff/call-next")
def call_next():
    service_id = request.form.get("service_id", type=int)
    if any(t["status"] == "called" for t in TICKETS):
        flash("Finish serving the current ticket first.", "warning")
        return redirect(url_for("staff_dashboard"))

    nxt = next((t for t in TICKETS
                if t["status"] == "waiting"
                and (not service_id or t["service_id"] == service_id)), None)
    if nxt is None:
        flash("Nobody is waiting.", "info")
    else:
        nxt["status"] = "called"
        nxt["assigned_to"] = "Counter 1"
        flash(f"Ticket #{nxt['number']} called.", "info")
    return redirect(url_for("staff_dashboard", service_id=service_id))


@app.post("/staff/tickets/<int:ticket_id>/<action>")
def staff_action(ticket_id, action):
    new_status = {"call": "called", "serve": "served", "no-show": "no-show"}.get(action)
    t = next((t for t in TICKETS if t["number"] == ticket_id), None)
    if action == "call" and any(x["status"] == "called" for x in TICKETS):
        flash("Finish serving the current ticket first.", "warning")
        return redirect(url_for("staff_dashboard"))
    
    if t is None or new_status is None:
        abort(404)
    t["status"] = new_status
    if new_status == "called":
        t["assigned_to"] = "Counter 1"
    flash(f"Ticket #{ticket_id} marked {new_status}.", "info")
    done = None if new_status == "called" else ticket_id
    return redirect(url_for("staff_dashboard", done=done))


@app.get("/queue/<int:ticket_id>/status.json")
def ticket_status(ticket_id):
    t = next((t for t in TICKETS if t["number"] == ticket_id), None)
    if t is None:
        abort(404)
    ahead = sum(1 for x in TICKETS
                if x["status"] == "waiting"
                and x["number"] < t["number"])
    return {"status": t["status"], "ahead": ahead,
            "assigned_to": t["assigned_to"]}


@app.route("/hello")
def hello():
    # The plain-string version from the Routes slide.
    return "Hello, CCC181!"


if __name__ == "__main__":
    # Lets you also start the app with: python app.py
    app.run(debug=True)
