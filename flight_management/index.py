from flight_management import app
from flask import render_template

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == "__main__":
    with app.app_context():
        app.run(host='0.0.0.0', port=500,debug=True)