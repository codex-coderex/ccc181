import os
import re
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_migrate import Migrate
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from models import Service, Ticket, User, db

load_dotenv()

app = Flask(__name__)
app.secret_key = "dev-only-change-me"  # Week 11 moves this into an environment variable
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_ECHO"] = os.environ.get("SQLALCHEMY_ECHO") == "1"

db.init_app(app)
migrate = Migrate(app, db)

# Timezones and Time calculations
PH_TIME = timezone(timedelta(hours=8))

@app.template_filter("local")
def local_time(value):
    """Display a database timestamp in Philippine time."""
    return value.astimezone(PH_TIME).strftime("%b %d, %I:%M %p") if value else ""

@app.template_filter("waiting_time")
def waiting_time(created_at):
    total_seconds = max(0, int(
        (datetime.now(timezone.utc) - created_at).total_seconds()
    ))

    minutes, seconds = divmod(total_seconds, 60)

    if minutes == 0:
        return f"{seconds} seconds"

    return f"{minutes} min {seconds} sec"

# Seeding starting services into database.
@app.cli.command("seed")
def seed():
    """Add the starting services if they are not there yet."""
    starting_services = [
        "SIM & eSIM Registration",
        "SIM Card Replacement",
        "Line Activation",
        "Postpaid Mobile Applications",
        "Home Fiber Broadband Applications",
        "Bill Payment & Inquiry",
        "Technical Support & Diagnostics",
    ]
    for name in starting_services:
        exists = db.session.scalar(db.select(Service).filter_by(name=name))
        if exists is None:
            db.session.add(Service(name=name))
    db.session.commit()
    print("Services are ready.")


@app.route("/")
def index():
    # render_template looks inside the templates/ folder and passes
    # keyword arguments to the template as variables.
    return render_template("index.html")


# All services helper
def all_services():
    return db.session.scalars(db.select(Service).order_by(Service.name)).all()

# Join form routes
@app.get("/join")
def join_form():
    return render_template("join.html", services=all_services(), form={})


@app.post("/join")
def join():
    form = request.form
    name = form.get("name", "").strip()
    email = form.get("email", "").strip().lower()
    service_id = form.get("service_id", type=int)
    service = db.session.get(Service, service_id) if service_id else None

    errors = {}
    if not name or len(name) > 80:
        errors["name"] = "Enter your name (up to 80 characters)."

    phone = None
    digits = re.sub(r"[\s-]", "", form.get("mobile_num", "").strip())
    if not digits:
        errors["mobile_num"] = "Enter your mobile number."
    else:
        match = re.fullmatch(r"(?:\+?63|0)(9[0-9]{9})", digits)
        if match is None:
            errors["mobile_num"] = "Enter a valid mobile number, like 09171234567."
        else:
            phone = "0" + match.group(1)  # always 09XXXXXXXXX

    if email and (len(email) > 120 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)):
        errors["email"] = "Enter a valid email address, or leave it blank."
    if service is None:
        errors["service_id"] = "Choose a service."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return render_template("join.html", services=all_services(),
                               form=form, errors=errors), 400

    user = db.session.scalar(db.select(User).filter_by(phone=phone))
    if user is not None:
        active = db.session.scalar(
            db.select(Ticket).filter(Ticket.user_id == user.id,
                                     Ticket.status.in_(["waiting", "called"])))
        if active is not None:
            flash(f"You already have an active ticket (#{active.id}). "         
                  "You cannot create a new ticket until your current ticket is completed.",
                  "warning")
            return redirect(url_for("ticket", ticket_id=active.id))
    else:
        user = User(name=name, phone=phone, email=email or None)

    ticket_row = Ticket(user=user, service=service)
    db.session.add(ticket_row)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Something went wrong saving your ticket. Please try again.", "danger")
        return render_template("join.html", services=all_services(),
                               form=form, errors={}), 409

    flash(f"You joined the queue. Your ticket is #{ticket_row.id}.", "success")
    return redirect(url_for("ticket", ticket_id=ticket_row.id))


# Queue and ticket status routes (My place)
def people_ahead(t):
    """Count tickets still waiting for the same service that joined before t."""
    stmt = (db.select(func.count())
            .select_from(Ticket)
            .where(
                Ticket.service_id == t.service_id,
                Ticket.status == "waiting",
                (Ticket.created_at < t.created_at) |
                    (
                        (Ticket.created_at == t.created_at) &
                        (Ticket.id < t.id)
                    )
                )
            )
    return db.session.scalar(stmt)

@app.get("/queue/<int:ticket_id>")
def ticket(ticket_id):
    t = db.get_or_404(Ticket, ticket_id)

    return render_template(
        "ticket.html",
        ticket=t,
        service=t.service,
        ahead=people_ahead(t),
        now=datetime.now(PH_TIME)
    )

@app.post("/queue/<int:ticket_id>/leave")
def leave(ticket_id):
    t = db.get_or_404(Ticket, ticket_id)

    if t.status != "waiting":
        flash("This ticket can no longer leave the queue.", "warning")
        return redirect(url_for("ticket", ticket_id=t.id))

    t.status = "left"
    db.session.commit()

    flash("You left the queue.", "info")
    return redirect(url_for("index"))


@app.get("/queue/<int:ticket_id>/status.json")
def ticket_status(ticket_id):
    t = db.get_or_404(Ticket, ticket_id)
    return {"status": t.status, 
            "ahead": people_ahead(t),
            "assigned_counter": t.assigned_counter,
        }


# Staff dashboard and actions
@app.get("/staff")
def staff_dashboard():
    service_id = request.args.get("service_id", type=int)
    q = request.args.get("q", "").strip().lower()

    services = all_services()

    # All waiting tickets
    waiting = db.session.scalars(
        db.select(Ticket)
        .where(Ticket.status == "waiting")
        .order_by(Ticket.created_at, Ticket.id)
    ).all()

    # Overall waiting count
    total_waiting = len(waiting)

    # Waiting tickets per service
    counts = {
        s.id: sum(1 for t in waiting if t.service_id == s.id)
        for s in services
    }

    # Filter by service
    if service_id:
        waiting = [t for t in waiting if t.service_id == service_id]

    # Search by name or ticket number
    if q:
        waiting = [
            t for t in waiting
            if q in t.user.name.lower() or q in str(t.id)
        ]

    # Currently called ticket
    serving = db.session.scalar(
        db.select(Ticket)
        .where(Ticket.status == "called")
        .order_by(Ticket.created_at)
    )

    # Service names
    names = {s.id: s.name for s in services}

    # Recently completed ticket
    done_id = request.args.get("done", type=int)
    done = db.session.get(Ticket, done_id) if done_id else None

    return render_template(
        "staff.html",
        serving=serving,
        done=done,
        waiting=waiting,
        total_waiting=total_waiting,
        services=services,
        names=names,
        counts=counts,
        selected=service_id,
        q=q
    )


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


@app.route("/hello")
def hello():
    # The plain-string version from the Routes slide.
    return "Hello, CCC181!"


if __name__ == "__main__":
    # Lets you also start the app with: python app.py
    app.run(debug=True)
