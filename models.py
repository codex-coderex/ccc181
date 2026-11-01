from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    BigInteger, CheckConstraint, DateTime, ForeignKey, Identity, Index,
    String, func, text, true
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    phone: Mapped[str | None] = mapped_column(String(11), unique=True)
    email: Mapped[str | None] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(
        String(20), default="customer", server_default="customer"
    )

    tickets: Mapped[list["Ticket"]] = relationship(back_populates="user")

    __table_args__ = (
        CheckConstraint("btrim(name) <> ''", name="ck_users_name_not_blank"),
        CheckConstraint(
            "phone IS NULL OR phone ~ '^09[0-9]{9}$'",
            name="ck_users_phone_format",
        ),
        CheckConstraint(
            "role = 'staff' OR phone IS NOT NULL",
            name="ck_users_customer_phone_required",
        ),
        CheckConstraint(
            "email IS NULL OR email ~ '^[^@[:space:]]+@[^@[:space:]]+$'",
            name="ck_users_email_format",
        ),
        CheckConstraint("role IN ('customer', 'staff')", name="ck_users_role"),
    )


class Service(db.Model):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True)
    is_active: Mapped[bool] = mapped_column(default=True, server_default=true())

    tickets: Mapped[list["Ticket"]] = relationship(back_populates="service")

    __table_args__ = (
        Index("unique_service_name_ci", func.lower(name), unique=True),
    )

class Ticket(db.Model):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(
        BigInteger, Identity(always=True), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT")
    )
    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id", ondelete="RESTRICT")
    )
    status: Mapped[str] = mapped_column(
        String(20), default="waiting", server_default="waiting"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    called_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    assigned_counter: Mapped[int | None] = mapped_column()
    account_type: Mapped[str | None] = mapped_column(String(20))
    priority_reason: Mapped[str | None] = mapped_column(String(20))

    user: Mapped["User"] = relationship(back_populates="tickets")
    service: Mapped["Service"] = relationship(back_populates="tickets")

    __table_args__ = (
        CheckConstraint(
            "status IN ('waiting', 'called', 'served', 'no-show', 'left')",
            name="ck_tickets_status",
        ),
        CheckConstraint(
            "status <> 'waiting' OR (called_at IS NULL AND assigned_counter IS NULL)",
            name="ck_tickets_waiting_not_called",
        ),
        CheckConstraint(
            "assigned_counter IS NULL OR assigned_counter > 0",
            name="ck_tickets_assigned_counter_positive",
        ),
        CheckConstraint(
            "account_type IS NULL OR account_type IN ('prepaid', 'postpaid', 'business')",
            name="ck_tickets_account_type",
        ),
        CheckConstraint(
            "priority_reason IS NULL OR priority_reason IN ('senior citizen', 'PWD', 'pregnant')",
            name="ck_tickets_priority_reason",
        ),
        Index(
            "unique_active_ticket_per_user",
            "user_id",
            unique=True,
            postgresql_where=text("status IN ('waiting', 'called')"),
        ),
    )