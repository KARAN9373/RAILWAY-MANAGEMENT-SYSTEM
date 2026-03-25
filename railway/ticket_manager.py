import pickle
import os
import random
from datetime import datetime

TICKET_FILE = "railway2.dat"

def generate_pnr():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=2))
    return f"PNR{timestamp[-4:]}{random_suffix}"

def load_tickets():
    tickets = []
    if os.path.exists(TICKET_FILE):
        with open(TICKET_FILE, "rb") as file:
            while True:
                try:
                    ticket = pickle.load(file)
                    tickets.append(ticket)
                except EOFError:
                    break
    return tickets

def save_tickets(tickets):
    with open(TICKET_FILE, "wb") as file:
        for ticket in tickets:
            pickle.dump(ticket, file)

def add_ticket(ticket):
    tickets = load_tickets()
    tickets.append(ticket)
    save_tickets(tickets)

def find_ticket_by_pnr(pnr):
    tickets = load_tickets()
    for ticket in tickets:
        if ticket["PNR"] == pnr:
            return ticket
    return None

def update_ticket_by_pnr(pnr, new_name, new_age):
    tickets = load_tickets()
    updated = False
    for ticket in tickets:
        if ticket["PNR"] == pnr:
            ticket["PASSENGER NAME"] = new_name
            ticket["AGE"] = new_age
            updated = True
            break
    save_tickets(tickets)
    return updated

def cancel_ticket_by_pnr(pnr):
    tickets = load_tickets()
    initial_len = len(tickets)
    tickets = [ticket for ticket in tickets if ticket["PNR"] != pnr]
    save_tickets(tickets)
    return len(tickets) < initial_len
