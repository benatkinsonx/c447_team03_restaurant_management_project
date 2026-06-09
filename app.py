<<<<<<< HEAD
from flask import Flask, render_template
from routes.checkout import checkout
=======
from flask import Flask, render_template, request

>>>>>>> 5111370 (Creation of main home page and tempates for many of the pages that will be included, creating a connection  to the db and adding the reservation table, added some logic and a basic form for the booking page, yet to hook up to the db as users and other tables are needed. CSS for the pages included, add as you go along)
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