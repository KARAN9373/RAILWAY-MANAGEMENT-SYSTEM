from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
from datetime import datetime
from ticket_manager import (
    load_tickets,
    save_tickets,
    find_ticket_by_pnr,
    update_ticket_by_pnr,
    cancel_ticket_by_pnr
)

app = Flask(__name__)
app.secret_key = "your_secret_key"
serial_number_counter = 1
tickets = load_tickets()
serial_number_counter = max((t.get("S.NO", 0) for t in tickets), default=0) + 1

# Dummy login credentials
VALID_USERNAME = "admin"
VALID_PASSWORD = "admin123"

# Predefined train details
train_table = [
    {"Train No.": "10001", "Train Name": "Express 1", "From": "Delhi", "To": "Mumbai",
     "Available Dates": ["2025-07-20", "2025-07-21", "2025-07-22"], "Seats Available": 100},
     
    {"Train No.": "10002", "Train Name": "Express 2", "From": "Delhi", "To": "Bangalore",
     "Available Dates": ["2025-12-20", "2025-12-22"], "Seats Available": 50},
     
    {"Train No.": "10003", "Train Name": "Super Fast 1", "From": "Mumbai", "To": "Chennai",
     "Available Dates": ["2025-12-21", "2025-12-23"], "Seats Available": 70},
     
    {"Train No.": "10004", "Train Name": "Super Fast 2", "From": "Delhi", "To": "Hyderabad",
     "Available Dates": ["2025-12-19", "2025-12-20"], "Seats Available": 60},
     
    {"Train No.": "10005", "Train Name": "Rajdhani Express", "From": "Mumbai", "To": "Delhi",
     "Available Dates": ["2025-12-20", "2025-12-22"], "Seats Available": 80},
     
    {"Train No.": "10006", "Train Name": "Shatabdi Express", "From": "Delhi", "To": "Amritsar",
     "Available Dates": ["2025-12-20", "2025-12-21", "2025-12-23"], "Seats Available": 50},
     
    {"Train No.": "10007", "Train Name": "Duronto Express", "From": "Chennai", "To": "Kolkata",
     "Available Dates": ["2025-12-21", "2025-12-22"], "Seats Available": 120},
     
    {"Train No.": "10008", "Train Name": "Garib Rath", "From": "Mumbai", "To": "Jaipur",
     "Available Dates": ["2025-12-22", "2025-12-23"], "Seats Available": 40},
     
    {"Train No.": "10009", "Train Name": "Nizamuddin Express", "From": "Delhi", "To": "Chennai",
     "Available Dates": ["2025-12-21", "2025-12-24"], "Seats Available": 90},
     
    {"Train No.": "10010", "Train Name": "Bandra Terminus", "From": "Mumbai", "To": "Surat",
     "Available Dates": ["2025-12-20", "2025-12-25"], "Seats Available": 70}
]

@app.route('/order_food', methods=['GET', 'POST'])
def order_food():
    if request.method == 'POST':
        name = request.form['passenger_name']
        seat = request.form['seat_no']
        return render_template('checkout.html', passenger_name=name, seat_no=seat)
    return render_template('order_food.html')

@app.route('/checkout', methods=['POST'])
def checkout():
    passenger_name = request.form.get('passenger_name')
    seat_no = request.form.get('seat_no')
    
    food_items = {
        "Chicken_Biryani": {"name": "Chicken Biryani", "price": 180},
        "Samosa": {"name": "Samosa", "price": 30},
        "Veg_Sandwich": {"name": "Veg Sandwich", "price": 50},
        "Veg_Thali": {"name": "Veg Thali", "price": 120},
    }

    selected_items = []
    total_amount = 0

    for key, info in food_items.items():
        quantity = int(request.form.get(f"item_{key}", 0))
        if quantity > 0:
            item_total = quantity * info["price"]
            total_amount += item_total
            selected_items.append({
                "name": info["name"],
                "price": info["price"],
                "quantity": quantity
            })

    return render_template(
        'checkout.html',
        passenger_name=passenger_name,
        seat_no=seat_no,
        selected_items=selected_items,
        total_amount=total_amount
    )

@app.route('/confirm_order', methods=['POST'])
def confirm_order():
    return redirect(url_for('index'))




def login_required(route_function):
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            flash("You must be logged in to access this page.", "danger")
            return redirect(url_for("login"))
        return route_function(*args, **kwargs)
    wrapper.__name__ = route_function.__name__
    return wrapper

@app.route("/")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html")


@app.route('/')
@app.route('/index')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route("/train-table")
def train_table_view():
    return render_template("train_table.html", train_table=train_table)
def generate_pnr():
    now = datetime.now()
    random_digits = random.randint(1000, 9999)
    return f"{now.strftime('%y%m%d%H')}{random_digits}"
@app.route("/book-ticket", methods=["GET", "POST"])
def book_ticket():
    global serial_number_counter

    if request.method == "POST":
        try:
            sno = serial_number_counter
            serial_number_counter += 1
            fno = request.form.get("train_no", "").strip()
            date = request.form.get("date_of_journey", "").strip()
            pname = request.form.get("passenger_name", "").strip().upper()
            age = request.form.get("passenger_age", "").strip()
            travel_class = request.form.get("class", "").strip()

            if not (fno and date and pname and age and travel_class):
                flash("All fields are required.", "error")
                return redirect(url_for("book_ticket"))

            fno = int(fno)
            age = int(age)

            train = next((train for train in train_table if train["Train No."] == str(fno)), None)
            if not train:
                flash(f"Train number {fno} does not exist.", "error")
                return redirect(url_for("book_ticket"))

            if date not in train["Available Dates"]:
                flash(f"Date {date} is not available for Train {train['Train Name']}.", "error")
                return redirect(url_for("book_ticket"))

            if train["Seats Available"] <= 0:
                flash(f"No seats available for Train {train['Train Name']} on {date}.", "error")
                return redirect(url_for("book_ticket"))

            sno = serial_number_counter
            serial_number_counter += 1
            seat_no = f"{random.randint(10, 99)}{random.choice(['A', 'B', 'C', 'D'])}{random.randint(1, 9)}"
            at = f"{random.randint(0, 23)}:{random.randint(0, 59):02d}"
            dp = f"{(int(at.split(':')[0]) + 1) % 24}:{int(at.split(':')[1]):02d}"
            pnr = generate_pnr()

            ticket = {
                "PNR": pnr, "S.NO": sno, "PASSENGER NAME": pname, "AGE": age,
                "TRAIN NO.": fno, "FROM STATION": train["From"], "TO STATION": train["To"],
                "DATE OF JOURNEY": date, "SEAT NO.": seat_no,
                "ARRIVAL TIME": at, "DEPARTURE TIME": dp, "CLASS": travel_class
            }

            tickets = load_tickets()
            tickets.append(ticket)
            save_tickets(tickets)
            train["Seats Available"] -= 1

            flash(f"Booking successful! PNR: {pnr}.", "success")
            return redirect(url_for("book_ticket"))

        except ValueError:
            flash("Train Number and Age must be numbers.", "error")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")

    return render_template("book_ticket.html", train_table=train_table)

@app.route("/view_tickets")
def view_tickets():
    tickets = load_tickets()
    return render_template("view_tickets.html", tickets=tickets)

@app.route("/update-ticket", methods=["GET", "POST"])
def update_ticket():
    if request.method == "POST":
        pnr = request.form.get("pnr")
        new_name = request.form.get("new_name", "").upper()
        new_age = request.form.get("new_age")

        try:
            new_age = int(new_age)
            updated = update_ticket_by_pnr(pnr, new_name, new_age)
            flash("Ticket updated successfully!" if updated else "PNR not found.")
        except Exception as e:
            flash(f"Error: {e}")

        return redirect(url_for("update_ticket"))

    return render_template("update_ticket.html")

@app.route("/cancel-ticket", methods=["GET", "POST"])
def cancel_ticket():
    if request.method == 'POST':
        pnr = request.form.get('pnr')
        if not pnr:
            flash("PNR is required.", "danger")
        else:
            cancelled = cancel_ticket_by_pnr(pnr)
            if cancelled:
                flash(f"Ticket with PNR {pnr} cancelled successfully.", "success")
            else:
                flash("PNR not found.", "danger")
        return redirect(url_for('cancel_ticket'))

    return render_template('cancel_ticket.html')

@app.route('/pnr-status', methods=['GET', 'POST'])
def pnr_status():
    pnr_number = request.args.get('pnr')
    status = None
    if pnr_number:
        ticket = find_ticket_by_pnr(pnr_number)
        if ticket:
            status = {
                'status': 'Confirmed',
                'train_no': ticket['TRAIN NO.'],
                'train_name': next((t['Train Name'] for t in train_table if t['Train No.'] == str(ticket['TRAIN NO.'])), 'N/A'),
                'date': ticket['DATE OF JOURNEY']
            }
    return render_template('pnr_status.html', pnr_number=pnr_number, status=status)

@app.route('/passenger_help', methods=['GET', 'POST'])
def passenger_help():
    if request.method == 'POST':
        pnr = request.form['pnr']
        remark = request.form['remark']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Save the help request to a .dat file
        with open('passenger_help.dat', 'a') as f:
            f.write(f"{timestamp} | PNR: {pnr} | Remark: {remark}\n")

        flash('Wait while RPF or TTE arrive on your seat as soon as possible.', 'info')
        return redirect(url_for('passenger_help'))

    return render_template('passenger_help.html')
if __name__ == "__main__":
    app.run(debug=False, port=4800)
