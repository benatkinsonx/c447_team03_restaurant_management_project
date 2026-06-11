
from flask import Flask, render_template, request
from routes.checkout import checkout

from routes.auth import auth
from routes.dashboard import dashboard_route
from routes.menu import menu_bp

app = Flask(__name__)
app.secret_key = "boo"



app.register_blueprint(auth)
app.register_blueprint(dashboard_route)
app.register_blueprint(checkout)
app.register_blueprint(menu_bp)


@app.route("/")
def home():
    return render_template("home.html")

# fucntions for view menu etc stuff that dont need user to be logged in

@app.route("/bookings", methods=["GET", "POST"])
def bookings():
    #get form input
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    date = request.form.get("date")
    time = request.form.get("time")
    guests = request.form.get("guests")

    
    return render_template("bookings.html")

@app.route("/submitbooking")
def submit_booking():
    return render_template("submit_booking.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)

