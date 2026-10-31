# SignalQ — Week 4 Schema Self-Review

I reviewed [schema.md](schema.md) using the six questions in Part 3 of the activity.

## Entry 1: Queue position and waiting time are computed

**Works well:** The schema stores `tickets.created_at` and `tickets.called_at` and calculates from them instead of storing queue position and waiting duration. Position is calculated from waiting tickets ordered by their joining time, while waiting duration is calculated from `created_at`. This avoids updating multiple ticket records whenever someone joins or leaves the queue. (Question 3: Facts, not results)

**Problem:** None found. Storing position or waiting duration separately would duplicate values that can already be calculated.

**Change:** Kept the schema as it is. No additional columns are needed.

## Entry 2: Ticket history is protected

**Works well:** Both foreign keys in `tickets` use `ON DELETE RESTRICT`. This prevents deleting users or services that still have tickets associated to them. Services can instead be deactivated through `services.is_active`, preserving their existing tickets. (Question 5: Deletes)

**Problem:** None found. Using `ON DELETE CASCADE` would risk removing historical tickets needed for reporting.

**Change:** Kept `ON DELETE RESTRICT` for both foreign keys to keep ticket relationships and support NFR-03 and NFR-04.

## Entry 3: Blank names and invalid email addresses

**Works well:** `users.name` has a `NOT NULL` constraint, and `users.email` is optional under FR-01.

**Problem:** `NOT NULL` does not prevent empty strings or names containing only spaces. Also, without an email format constraint, the database could accept an invalid email like `joanna.example.com` if Flask validation were bypassed. Found through Question 4 (Bad data).

**Change:** Added `CHECK (btrim(name) <> '')` to reject blank names. I also added `CHECK (email IS NULL OR email ~ '^[^@[:space:]]+@[^@[:space:]]+$')` to reject obviously malformed email addresses while still allowing NULL because email is optional. Flask will continue validating and cleaning the inputs before saving them.

## Entry 4: Waiting tickets could contain counter information

**Works well:** `tickets.status` has a CHECK constraint limiting values to `waiting`, `called`, `served`, `no-show`, and `left`. The `called_at` and `assigned_counter` columns are nullable because tickets do not have a counter assignment when first created.

**Problem:** The original schema allows a ticket with `status = 'waiting'` to have a counter number or call timestamp. This could cause the My place page to show counter information before the ticket has been actually called. Found through Question 4 (Bad data).

**Change:** Added the following constraint:

```sql
CHECK (
    status <> 'waiting'
    OR (called_at IS NULL AND assigned_counter IS NULL)
)
```

This prevents waiting tickets from containing call information. Other ticket status transitions will still be validated in Flask.

## Entry 5: Counter numbers are not linked to a separate table

**Works well:** The `tickets.assigned_counter` column records which counter a customer should approach after being called. This supports FR-02 and FR-05 without introducing another table.

**Problem:** The database cannot verify whether an assigned counter actually exists because `assigned_counter` is an integer rather than a foreign key. Found through Question 1 (Coverage).

**Change:** Kept `assigned_counter` as an integer with a positive-value CHECK constraint. SignalQ does not currently require staff to create or manage counters. A separate `counters` table can be introduced through a future migration if counter management becomes necessary.

## Entry 6: Duplicate active tickets

**Works well:** `users.phone` has a UNIQUE constraint to prevent duplicate customer records, and the backend saves every accepted number in the same `09XXXXXXXXX` form, so the same number typed in different ways still matches one row. The frontend also disables (greys out) the **Get Ticket** button after submission to prevent accidental double taps.

**Problem:** Disabling the button only prevents repeated submissions from the same page. A customer could still submit from another tab or retry a request, potentially creating multiple active tickets and making the queue count inaccurate. Found through Question 4 (Bad data).

**Change:** Added a partial unique index on `tickets.user_id` that applies only when `status IN ('waiting', 'called')`. This prevents the same user record from having multiple active tickets simultaneously while still allowing new tickets after previous ones are served, marked no-show, or left. The trade-off is that one customer cannot hold two active tickets at the same time, for example for two different services. I accepted this because my persona comes in with one problem per visit, and it keeps the position count accurate. If this becomes a problem, the index can be changed to `(user_id, service_id)` in a later migration.

## Review Summary

| Question | Result |
| --- | --- |
| 1. Coverage | Every data-storing functional requirement has a corresponding table, column, or planned field. The schema supports the personas' main tasks. `users.role` separates customers and staff. |
| 2. One fact in one place | Customer information is stored in `users`, service information in `services`, and ticket-specific information in `tickets`. Service names and customer details are not duplicated across tickets. |
| 3. Facts, not results | Queue position and waiting duration are calculated instead of stored (Entry 1). |
| 4. Bad data | Added checks for blank names and malformed emails (Entry 3), waiting tickets with call information (Entry 4), and duplicate active tickets (Entry 6). Existing constraints also reject invalid ticket statuses. |
| 5. Deletes | Both foreign keys use `ON DELETE RESTRICT` to preserve ticket relationships and historical records (Entry 2). |
| 6. Types | Timestamps use `timestamptz`, `is_active` uses `boolean`, and phone numbers use `varchar` to preserve their leading zero. |

