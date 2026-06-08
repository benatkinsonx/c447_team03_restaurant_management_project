from flask import Flask, render_template
from routes.auth import auth
from routes.dashboard import dashboard_route

app = Flask(__name__)
app.secret_key = "boo"

app.register_blueprint(auth)
app.register_blueprint(dashboard_route)


@app.route("/")
def index():
    return render_template("index.html")

# fucntions for view menu etc stuff that dont need user to be logged in


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)