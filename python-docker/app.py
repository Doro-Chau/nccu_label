from flask import Flask, render_template, request
import os
import random

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/", methods=['POST'])
def login_home():
    email = request.form['email']
    psw = request.form['psw']
    print(email, psw)
    return render_template("index.html")

@app.route("/click")
def click():
    return render_template("result.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
