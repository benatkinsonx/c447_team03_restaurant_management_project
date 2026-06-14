from datetime import timedelta
import os
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for
from flask_jwt_extended import JWTManager, unset_jwt_cookies

from routes.checkout import checkout

from routes.auth import auth
from routes.dashboard import dashboard_route
from routes.menu import menu_bp
from routes.bookings import booking_bp

load_dotenv()

app = Flask(__name__)

flask_secret = os.getenv("FLASK_SECRET_KEY")
jwt_secret = os.getenv("JWT_SECRET_KEY")

if not flask_secret:
    raise RuntimeError("FLASK_SECRET_KEY is missing from .env")

if not jwt_secret:
    raise RuntimeError("JWT_SECRET_KEY is missing from .env")

app.config["SECRET_KEY"] = flask_secret
app.config["JWT_SECRET_KEY"] = jwt_secret

# read from cookies
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
    minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "120"))
)
app.config["JWT_COOKIE_SECURE"] = (
    os.getenv("JWT_COOKIE_SECURE", "false").lower() == "true"
)

app.config["JWT_COOKIE_SAMESITE"] = "Lax"


# Enable JWT CSRF protection for HTML forms 
app.config["JWT_COOKIE_CSRF_PROTECT"] = True 
app.config["JWT_CSRF_IN_COOKIES"] = True 
app.config["JWT_CSRF_CHECK_FORM"] = True 
app.config["JWT_ACCESS_CSRF_FIELD_NAME"] = "csrf_token" 

# Flask sessions remain for basket and checkout data a
app.config["SESSION_COOKIE_HTTPONLY"] = True 
app.config["SESSION_COOKIE_SAMESITE"] = "Lax" 
app.config["SESSION_COOKIE_SECURE"] = ( os.getenv( "SESSION_COOKIE_SECURE", "false" ).lower() == "true" ) 

jwt = JWTManager(app) 

@jwt.unauthorized_loader 
def missing_token(reason): 
    return redirect( url_for( "auth.login", next=request.path ) ) 

@jwt.expired_token_loader 
def expired_token(jwt_header, jwt_payload): 
    response = redirect( url_for( "auth.login", next=request.path ) ) 
    unset_jwt_cookies(response) 
    return response

@jwt.invalid_token_loader 
def invalid_token(reason): 
    response = redirect( url_for("auth.login") ) 
    unset_jwt_cookies(response) 
    return response


app.register_blueprint(auth)
app.register_blueprint(dashboard_route)
app.register_blueprint(checkout)
app.register_blueprint(menu_bp)
app.register_blueprint(booking_bp)


@app.route("/")
def home():
    return render_template("home.html")


# fucntions for view menu etc stuff that dont need user to be logged in

# @app.route("/bookings", methods=["GET", "POST"])
# def bookings():
#     #get form input
#     first_name = request.form.get("first_name")
#     last_name = request.form.get("last_name")
#     email = request.form.get("email")
#     phone = request.form.get("phone")
#     date = request.form.get("date")
#     time = request.form.get("time")
#     guests = request.form.get("guests")


#     return render_template("bookings.html")

# @app.route("/submitbooking")
# def submit_booking():
#     return render_template("submit_booking.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)
