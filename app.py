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


# Services helpers
def all_services():
    return db.session.scalars(db.select(Service).order_by(Service.id)).all()

def active_services():
    return db.session.scalars(
        db.select(Service)
        .filter_by(is_active=True)
        .order_by(Service.id)
    ).all()

# Join form routes
@app.get("/join")
def join_form():
    return render_template("join.html", services=active_services(), form={})


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
    if service is None or not service.is_active:
        errors["service_id"] = "Choose a service."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return render_template("join.html", services=active_services(),
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
        return render_template("join.html", services=active_services(),
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

    waiting = db.session.scalars(
        db.select(Ticket)
        .where(Ticket.status == "waiting")
        .order_by(Ticket.created_at, Ticket.id)
    ).all()

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

    serving = db.session.scalar(
        db.select(Ticket)
        .where(Ticket.status == "called")
        .order_by(Ticket.created_at)
    )

    names = {s.id: s.name for s in services}

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

# Listens to queue state in db
@app.get("/staff/queue-state.json")
def staff_queue_state():
    service_id = request.args.get("service_id", type=int)
    q = request.args.get("q", "").strip().lower()

    stmt = (
        db.select(Ticket)
        .where(Ticket.status == "waiting")
        .order_by(Ticket.created_at, Ticket.id)
    )

    if service_id:
        stmt = stmt.where(Ticket.service_id == service_id)

    waiting = db.session.scalars(stmt).all()

    if q:
        waiting = [
            t for t in waiting
            if q in t.user.name.lower() or q in str(t.id)
        ]

    serving = db.session.scalar(
        db.select(Ticket)
        .where(Ticket.status == "called")
        .order_by(Ticket.created_at, Ticket.id)
    )

    return {
        "waiting_ids": [t.id for t in waiting],
        "serving_id": serving.id if serving else None,
    }


@app.post("/staff/call-next")
def call_next():
    service_id = request.form.get("service_id", type=int)

    serving = db.session.scalar(
        db.select(Ticket).filter_by(status="called")
    )

    if serving is not None:
        flash("Finish serving the current ticket first.", "warning")
        return redirect(url_for("staff_dashboard"))

    # Find the first waiting ticket
    stmt = (
        db.select(Ticket)
        .filter_by(status="waiting")
        .order_by(Ticket.created_at, Ticket.id)
        .limit(1)
    )

    # Apply service filter if one was selected
    if service_id:
        stmt = stmt.where(Ticket.service_id == service_id)

    nxt = db.session.scalar(stmt)

    if nxt is None:
        flash("Nobody is waiting.", "info")
    else:
        nxt.status = "called"
        nxt.called_at = func.now()
        nxt.assigned_counter = 1

        db.session.commit()

        flash(f"Ticket #{nxt.id} called.", "info")

    return redirect(url_for("staff_dashboard", service_id=service_id))


@app.post("/staff/tickets/<int:ticket_id>/<action>")
def staff_action(ticket_id, action):
    # Same implementation as using a separate STAFF_ACTIONS dictionary
    new_status = {"call": "called", "serve": "served", "no-show": "no-show"}.get(action)

    if new_status is None:
        abort(404)

    t = db.get_or_404(Ticket, ticket_id)

    # Prevent calling another ticket while one is being served
    if action == "call":
        serving = db.session.scalar(
            db.select(Ticket).filter_by(status="called")
        )

        if serving is not None:
            flash("Finish serving the current ticket first.", "warning")
            return redirect(url_for("staff_dashboard"))

        if t.status != "waiting":
            flash("Only waiting tickets can be called.", "warning")
            return redirect(url_for("staff_dashboard"))

    # Prevent changing completed or inactive tickets
    if action == "serve" and t.status != "called":
        flash("Only called tickets can be marked served.", "warning")
        return redirect(url_for("staff_dashboard"))

    if action == "no-show" and t.status not in ("waiting", "called"):
        flash("This ticket is no longer active.", "warning")
        return redirect(url_for("staff_dashboard"))

    t.status = new_status

    if new_status == "called":
        t.called_at = func.now()
        t.assigned_counter = 1

    db.session.commit()

    flash(f"Ticket #{ticket_id} marked {new_status}.", "info")

    done = None if new_status == "called" else ticket_id
    return redirect(url_for("staff_dashboard", done=done))


@app.post("/staff/tickets/<int:ticket_id>/delete")
def delete_ticket(ticket_id):
    t = db.get_or_404(Ticket, ticket_id)
    db.session.delete(t)  # hard delete: the row is gone for good
    db.session.commit()
    flash(f"Ticket #{ticket_id} was deleted.", "warning")
    return redirect(url_for("staff_dashboard"))


# Staff services management routes
@app.get("/staff/services")
def services_list():
    return render_template("services.html", services=all_services())


@app.post("/staff/services")
def service_create():
    name = request.form.get("name", "").strip()

    if not name or len(name) > 60:
        flash("Enter a name (up to 60 characters).", "danger")
        return redirect(url_for("services_list"))

    existing = db.session.scalar(
        db.select(Service).where(func.lower(Service.name) == name.lower())
    )

    if existing:
        flash("A service with this name already exists.", "danger")
        return redirect(url_for("services_list"))

    db.session.add(Service(name=name))

    try:
        db.session.commit()
        flash(f"Service “{name}” added.", "success")
    except IntegrityError:
        db.session.rollback()
        flash(f"A service named “{name}” already exists.", "danger")
    return redirect(url_for("services_list"))


@app.post("/staff/services/<int:service_id>/edit")
def service_edit(service_id):
    s = db.get_or_404(Service, service_id)

    name = request.form.get("name", "").strip()

    if not name or len(name) > 60:
        flash("Enter a service name (up to 60 characters).", "danger")
        return redirect(url_for("services_list"))

    s.name = name
    s.is_active = request.form.get("is_active") == "on"

    try:
        db.session.commit()
        flash(f"Service “{name}” updated.", "success")
    except IntegrityError:
        db.session.rollback()
        flash(f"A service named “{name}” already exists.", "danger")

    return redirect(url_for("services_list"))


@app.post("/staff/services/<int:service_id>/delete")
def service_delete(service_id):
    s = db.get_or_404(Service, service_id)

    if s.tickets:
        flash(f"“{s.name}” has tickets, so it cannot be deleted. Turn it off instead.", "danger")
        return redirect(url_for("services_list"))
    
    db.session.delete(s)
    db.session.commit()
    flash(f"Service “{s.name}” deleted.", "warning")
    return redirect(url_for("services_list"))


@app.route("/hello")
def hello():
    # The plain-string version from the Routes slide.
    return "Hello, CCC181!"


if __name__ == "__main__":
    # Lets you also start the app with: python app.py
    app.run(debug=True)
