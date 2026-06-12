
from flask import Flask, render_template, request
from routes.checkout import checkout

from routes.auth import auth
from routes.dashboard import dashboard_route
from routes.menu import menu_bp
from routes.bookings import booking_page

app = Flask(__name__)
app.secret_key = "boo"



app.register_blueprint(auth)
app.register_blueprint(dashboard_route)
app.register_blueprint(checkout)
app.register_blueprint(menu_bp)
app.register_blueprint(booking_page)


@app.route("/")
def home():
    return render_template("home.html")

# fucntions for view menu etc stuff that dont need user to be logged in



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)