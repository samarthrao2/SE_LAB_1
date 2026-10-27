"""IT helpdesk ticket allocator.

Raises tickets with an urgency level, assigns technicians, records notes,
lists unassigned high-priority tickets and saves everything to a JSON file.
"""
import hmac
import itertools
import json
import os
import platform
import re
import subprocess  # nosec B404
from datetime import datetime

MIN_PRIORITY = 1
MAX_PRIORITY = 5
DEFAULT_PRIORITY = 3
HIGH_PRIORITY = 4

# Read from the environment instead of hard-coding the secret in source
ADMIN_PASSWORD = os.environ.get("HELPDESK_ADMIN_PASSWORD", "")
HOSTNAME_PATTERN = re.compile(
    r"^[A-Za-z0-9]([A-Za-z0-9.-]{0,251}[A-Za-z0-9])?$")


TICKETS = {}
_ticket_ids = itertools.count(101)


def parse_priority(urgency):
    """Convert urgency to an int and make sure it is within 1-5."""
    try:
        priority = int(urgency)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Urgency must be a number, got {urgency!r}") from exc
    if not MIN_PRIORITY <= priority <= MAX_PRIORITY:
        raise ValueError(
            f"Urgency must be between {MIN_PRIORITY} and {MAX_PRIORITY}, "
            f"got {priority}")
    return priority


def raise_ticket(user, issue_type, urgency=str(DEFAULT_PRIORITY),
                 audit_trail=None):
    """Create a ticket and return its id.

    A fresh audit trail is used per call unless one is passed in.
    """
    priority = parse_priority(urgency)
    if audit_trail is None:
        audit_trail = []
    ticket_id = next(_ticket_ids)
    TICKETS[ticket_id] = {
        "user": user,
        "issue": issue_type,
        "priority": priority,
        "tech": None,
        "notes": [],
    }
    audit_trail.append(
        f"{user} raised #{ticket_id} at {datetime.now()}")
    return ticket_id


def assign_ticket(ticket_id, technician):
    """Assign a technician; return False if the ticket does not exist."""
    if ticket_id not in TICKETS:
        return False
    TICKETS[ticket_id]["tech"] = technician
    return True


def add_note(ticket_id, note):
    """Append a note; return False if the ticket does not exist."""
    if ticket_id not in TICKETS:
        print(f"Cannot add note: ticket #{ticket_id} does not exist")
        return False
    TICKETS[ticket_id]["notes"].append(note)
    return True


def close_ticket(ticket_id, password):
    """Delete a ticket if the admin password matches."""
    if not ADMIN_PASSWORD or not hmac.compare_digest(
            password.encode(), ADMIN_PASSWORD.encode()):
        return False
    if ticket_id not in TICKETS:
        return False
    del TICKETS[ticket_id]
    return True


def unresolved_high_priority():
    """Return ids of high-priority tickets with no technician assigned."""
    return [
        ticket_id for ticket_id, ticket in TICKETS.items()
        if ticket["priority"] >= HIGH_PRIORITY and ticket["tech"] is None
    ]


def ping_user_machine(hostname):
    """Ping a host once and return the ping exit code."""
    if not HOSTNAME_PATTERN.match(hostname):
        raise ValueError(f"Invalid hostname: {hostname!r}")
    count_flag = "-n" if platform.system() == "Windows" else "-c"
    # Argument list with no shell: hostname cannot inject extra commands
    return subprocess.call(  # nosec B603 B607
        ["ping", count_flag, "1", hostname])


def save_tickets(file="tickets.json"):
    """Write all tickets to a JSON file."""
    with open(file, "w", encoding="utf-8") as handle:
        json.dump(TICKETS, handle)


def main():
    """Demo run of the helpdesk workflow."""
    t1 = raise_ticket("anil", "printer", "5")
    raise_ticket("meera", "wifi", "4")
    t3 = raise_ticket("joe", "vpn", "3")
    assign_ticket(t1, "Tech-Kiran")
    add_note(999, "Called user")
    print("Unassigned high priority:", unresolved_high_priority())
    level = input(
        "Urgency for a new laptop ticket (1-5, Enter for 3): ") or "3"
    try:
        raise_ticket("sana", "laptop", level)
    except ValueError as err:
        print("Ticket not created:", err)
    close_ticket(t3, ADMIN_PASSWORD)
    save_tickets()
    print("Open tickets:", list(TICKETS))


if __name__ == "__main__":
    main()
