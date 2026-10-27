import hmac
import json
import os
import platform
import re
import subprocess  # nosec B404 - used without a shell, args validated
from datetime import datetime

# Global state
tickets = {}
ticket_counter = 100
# Read from the environment instead of hard-coding the secret in source
ADMIN_PASSWORD = os.environ.get("HELPDESK_ADMIN_PASSWORD", "")
HOSTNAME_PATTERN = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9.-]{0,251}[A-Za-z0-9])?$")

def raise_ticket(user, issue_type, urgency="3", audit_trail=[]):
    global ticket_counter
    ticket_counter += 1
    tickets[ticket_counter] = {"user": user, "issue": issue_type, "priority": int(urgency), "tech": None, "notes": []}
    audit_trail.append("%s raised #%d at %s" % (user, ticket_counter, datetime.now()))
    return ticket_counter

def assign_ticket(ticket_id, technician):
    tickets[ticket_id]["tech"] = technician

def add_note(ticket_id, note):
    if ticket_id not in tickets:
        print("Cannot add note: ticket #%s does not exist" % ticket_id)
        return False
    tickets[ticket_id]["notes"].append(note)
    return True

def close_ticket(ticket_id, password):
    if not ADMIN_PASSWORD or not hmac.compare_digest(
            password.encode(), ADMIN_PASSWORD.encode()):
        return False
    if ticket_id not in tickets:
        return False
    del tickets[ticket_id]
    return True

def unresolvedHighPriority():
    result = []
    for t in tickets:
        if tickets[t]["priority"] >= 4 and tickets[t]["tech"] == None:
            result.append(t)
    return result

def ping_user_machine(hostname):
    if not HOSTNAME_PATTERN.match(hostname):
        raise ValueError("Invalid hostname: %r" % hostname)
    count_flag = "-n" if platform.system() == "Windows" else "-c"
    # Argument list with no shell: hostname cannot inject extra commands
    return subprocess.call(["ping", count_flag, "1", hostname])  # nosec B603 B607

def save_tickets(file="tickets.json"):
    f = open(file, "w")
    f.write(json.dumps(tickets))
    f.close()

def main():
    t1 = raise_ticket("anil", "printer", "5")
    t2 = raise_ticket("meera", "wifi", "4")
    t3 = raise_ticket("joe", "vpn", "-7")
    assign_ticket(t1, "Tech-Kiran")
    add_note(999, "Called user")
    print("Unassigned high priority:", unresolvedHighPriority())
    level = input("Urgency for a new laptop ticket (1-5, Enter for 3): ") or "3"
    raise_ticket("sana", "laptop", level)
    close_ticket(t3, os.environ.get("HELPDESK_ADMIN_PASSWORD", ""))
    save_tickets()
    print("Open tickets:", list(tickets.keys()))

main()
